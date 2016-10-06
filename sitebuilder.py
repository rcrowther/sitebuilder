#!/usr/bin/env python

"""
sitebuilder
===========
Gaudy name for conversions of html files to place in websites.

The script works recursively from a given directory.


Usage
~~~~~
From the commandline::

    ./sitebuilder.py <options> -d /.../inputFile

Options include::

  -h, --help           show this help message and exit
  -d FILE, --dir=FILE  directory to start
  -i, --indexes        generate HTML indexes in every visited folder
  -l, --links          rewrite urls in links and images. Overwrites existing
                       urls.
  -n, --navbars        insert navbars into pages
  -N, --forcenavbars   Slow! Risky! insert navbars into pages, attempting to
                       remove previous bars
  -s, --shorturls      for indexes, generate urls as short (no -index.htm-
                       extensions to directories, no extensions on files)





Indexes
~~~~~~~
An index can be built to the contents of a folder.

The script will not build an index if a file 'index.*' exists. Once an 
index is created it will not be replaced. To rebuild an index the 
existing 'index,htm' must be deleted.

Only visible directories (not starting with '.' or '~') are placed in an
index. Only regular files ending with '.htm' or 'html', are placed in an
index.The title of the index is taken from the folder name. Declared
navbar information is also written into the page. Links written to an
index are relative. Text in the links is file basenames with underscores
replaced by spaces.
 
Index entries are sorted. The current layout separates folders from 
regular files, in two separate lists. Within each list, names starting
with a symbol come first, followed by names starting with a number,
followed by names starting with an alphabetic character. Each 
sub-category is internally sorted.

The links in an index can be modified by,


'-s': short urls
---------------
Links are formatted as short urls. The server or content manager 
configuration must support short urls to work. If '/plants' contains
'/plants/weeds/ragwort.htm', the default link is::

    <a href="/plants/weeds/ragwort.htm">ragwort</a>

using the short option::

    <a href="/plants/weeds/ragwort">ragwort</a>

'-s' also affects directory links. If '/plants' contains
'/plants/weeds' and '/plants/shrubs', the default link in the 'plants'
index, to 'weeds', is::

    <a href="/plants/weeds/index.htm">weeds</a>

using the short option::

    <a href="/plants/weeds/">weeds</a>
    
which presumes a server/content manager can guess to look for an
'index.htm' file.



Link rewriting
~~~~~~~~~~~~~~
The script can rewrite links to static resources.

Warning: link detection is risky.

The script detects 'src' attributes, or 'href' attributes with links
ending in '.js' or '.css'. The base name is extracted from matching
links, and added to a root path stated in the script (these links would 
usually be absolute).

 

Navbars
~~~~~~~~
WARNING: The markup text must be sequential in the file, no newlines.

The script can place header or navbar markup after a <body> tag. 

The text used is set in the variable::

    bodyHeaderMarkup = ...

The code defends against inserting the markup if a <header> or <nav> tag
exists. So it will not repeatedly insert if the script is run multiple
times.

Navbars are not automatically built, because website top level folders
may contain folders for static files, protected folders, etc.
  

'-N': forced navbar insertion
-----------------------------
Replace a navbar.

Since detection of HTML elements is risky without a parser, this action
has an explicit option. 


    :copyright: 2016 Rob Crowther
    :license: GPL, see LICENSE for details.
"""
# TODO:
#x sort index entries
#x sort numeric index entries correctly
#x should write navbars into indexes
# remove hidden directories
#x move temp files
# check base dir handling
#x check dirs .index.htm for long, /... for short
#x dont build indexes for empty folders?
#x skip index if overwriting
#x fix relatives
#x rewrite other links
### extra
# display book
# i-col index for book
from optparse import OptionParser
import sys, getopt, re
import os.path 
from collections import namedtuple
from os import walk




### User vars ###

# Change for new navbar. Should start with a 'header' or 'nav' element.
bodyHeaderMarkup = '<header id="site-nav"><nav><ul><li><a href="/articles/">Articles</a></li><li><a href="/projects/">Projects</a></li><li><a href="/about.htm">About</a></li></ul></nav></header>'

# Change for static link targets
# Would usually be absolute links
# followed by trailing hash (basename is extracted from original link)
cssRoot = "/home/rob/Code/css/print/book/"
jsRoot = "/js/"
imageRoot = "/images/"


# Change for new intro to indexes
def webPageOpen(f, title):
    #css1 = '/home/rob/Code/css/display/plain_carbon_display/plain_carbon_display.css'
    css1 = '/home/rob/Code/css/print/book/book.css'
    css2 = '/home/rob/Code/css/display/book/webbook.css'

    f.write('<!DOCTYPE html>\n<html>\n<head>\n<title>{0}</title>\n'.format(title))
    f.write('<meta http-equiv="content-type" content="text/html; charset=UTF-8" />\n')
    f.write('<link rel="stylesheet" type="text/css" media="screen" href="{0}"/>\n'.format(css1))
    f.write('<link rel="stylesheet" type="text/css" media="screen" href="{0}"/>\n'.format(css2))

    f.write('</head>\n<body>')
    f.write(bodyHeaderMarkup)
    f.write('<article>\n<h1>')
    f.write(title)
    f.write('</h1>\n')


# Change for new outro to indexes
def webPageClose(f):
    f.write('</article></body></html>')
    
def indexOpenTemplate():
    return '<nav class="toc">\n'
        
def indexCloseTemplate():
    return '</nav>\n'

        
def indexLinkTemplate(href, text):
    return '<li><a href="{0}">{1}</a></li>\n'.format(href, text)



### Internal ###
def printInfo(msg):
    print('[info] {0}'.format(msg))
    
def printError(msg):
    print('[Error] {0}'.format(msg))
    
    
    
def limitsFirstHeader(line, targetedTag):
    '''
    header/nav must be there, and well-formed, or this can cause a lot 
    of damage.
    @return tuple of start/stop, or None
    '''
    start = -1
    end = -1
    bs = line.find('<body')
    if bs != -1:
        be = line.find('>', bs + 5)
        if be != -1:
            start = be + 1
            closeTarget = '</' + targetedTag + '>'
            cs = line.find(closeTarget, start)
            if cs != -1:
                end = cs + len(closeTarget) 
    return (start, end) if(end != -1) else None

def getBodyFollowingTag(line):
    # only do this is fast string match says ok
    if (line.find('<body') != -1):
        m = re.search(bodyHeaderRe, line)
        return m.group(2) if m else ''
    else:
        return ''

#line = '></head><body><nav><ul></ul></nav><article>'

def removeNavbar(line):
    tt = getBodyFollowingTag(line)
    if (tt == 'nav' or tt == 'header'):
        r = limitsFirstHeader(line, tt)
        if r:
            return line[0:r[0]] + line[r[1]:]
    return line

    
bodyHeaderRe = re.compile(r'(<body[^>]*>)<([^> ]+)')

def insertNavbar(line):
    def navbarRep(m):
        if (m.group(2) != 'nav' and m.group(2) != 'header'):
            return m.group(1) + bodyHeaderMarkup + '<' + m.group(2) 
        else: 
            # match test means should never be called
            return m.group(0)
            
    # only do this is fast string match says ok
    return re.sub(bodyHeaderRe, navbarRep, line) if (line.find('<body') != -1) else line



# match. Note the opening dot skip for relative links
cssJSRe = re.compile(r'href=\"(\.?\.?[^\.]+\.(css|js))\"', re.IGNORECASE)
# match img links
srcRe = re.compile(r'src=\"([^\"]+)"', re.IGNORECASE)
 
def rewriteLinks(line):
    def cssRep(m):
        root = cssRoot if m.group(2) == "css" else jsRoot
        p = os.path.join(root, os.path.basename(m.group(1)))
        return 'href=\"' + p + '"'
        
    def imgRep(m):
        p = os.path.join(imageRoot, os.path.basename(m.group(1)))
        return 'src=\"' + p + '"'

    l1 = re.sub(cssJSRe, cssRep, line)
    l2 = re.sub(srcRe, imgRep, l1)
    return l2



def cmpkeyRespectingNumerics(this):
    def findNumeric(s):
        c = 0
        i = -1
        while True:
            i += 1
            c = s[i]
            if not c.isdigit():
                break 
        return i
    
    i = findNumeric(this)

    return int(this[0:i])
    
def sortRespectingNumerics(l):
        num = []
        alpha = []
        sym = []
        for e in l:
            if (e[0].isdigit()):
                num.append(e)
            elif (e[0].isalpha()):
                alpha.append(e)
            else:
                sym.append(e)

        alphas = sorted(alpha) 
        nums = sorted(num, key=cmpkeyRespectingNumerics)
        syms = sorted(sym) 
        return syms + nums + alphas 
        
def mkIndex(rootDir, dirPath, dirnameList, filePathList, options):
    p =  os.path.join(dirPath, 'index.htm')
    
    try:
        f = open(p, 'w')

        # title
        # Uppercase fails badly in Unicode. Use CSS? Probably better.
        lastElem = os.path.basename(dirPath).replace('_', ' ')
        title = "defaulty" if(not lastElem or lastElem == '.') else lastElem
        
        webPageOpen(f, title)

        f.write(indexOpenTemplate())
        f.write('<ul  class="wide">\n')

        # directories
        dfpl = sortRespectingNumerics(dirnameList)

        for fp in dfpl:
            #print 'fp', fp
            # if not given index file target, enforce final slash 
            href = fp + '/' if options.shorturls else fp + os.path.sep + 'index.htm' 
            txt = fp.replace('_', ' ')
            f.write( indexLinkTemplate(href, txt) )
            
        f.write('</ul>\n<ul  class="wide">\n')


        # files
        rfpl = sortRespectingNumerics(filePathList)

        for fp in rfpl:
            # chop the extension, only .htm or .html
            noExtPath = fp[: fp.rfind('.')]
            href = noExtPath if options.shorturls else fp
            txt = noExtPath.replace('_', ' ')
            f.write( indexLinkTemplate(href, txt) )

        f.write('</ul>\n')
        f.write(indexCloseTemplate())

        webPageClose(f)

        f.close()
    except IOError:
        printError('index file can not be created (exists? permissions?): %s' % p)


def rewriteFiles(rootDir, dirPath, dirnameList, filePathList, options):
    for fp in filePathList:
        inP = os.path.join(dirPath, fp)
        outP = inP + '.tmp'

        fIn = open(inP, 'r')
        # out to a temp file
        fOut = open(outP, 'w')

        for l in fIn:
            l1 = rewriteLinks(l) if options.links else l
            #print l1
            l2 = removeNavbar(l1) if options.forcednavbars else l1
            l3 = insertNavbar(l2) if options.navbars else l2
            fOut.write(l3)
            
        fOut.close()
        fIn.close()
        
        # replace in with .tmp
        # needs P3.3 to go cross-platform
        #os.replace(outP, inP)
        os.rename(outP, inP)
    
def containsIndex(filenames):
    r = False
    for e in filenames:
        r = r or e.startswith('index')
    return r
    
def processDirs(rootPath, options):    
    for (dirPath, dirnames, filenames) in walk(rootPath):
        
        # ignore hidden files
        dirPathList = []
        for fd in dirnames:
            first = fd[0]
            if first != '.' and first != '~':
                dirPathList.append(fd)
              
        # ignore non-htm in rewrite treatment and index lists 
        entryPathList = []
        for fn in filenames:
            if fn.endswith(('.htm','.html')):
                entryPathList.append(fn)

        #print filePathList       
        # options.forcednavbars also enables option.navbars
        if options.links or options.navbars: 
            rewriteFiles(
                rootPath,
                dirPath, 
                dirPathList, 
                entryPathList, 
                options
                )   
                
        # indexes after links
        # dont rewrite existing
        #print containsIndex(filenames)
        if options.indexes:
            if not containsIndex(filenames): 
                mkIndex(
                    rootPath,
                    dirPath, 
                    dirPathList, 
                    entryPathList, 
                    options
                    )        
            else:
                printInfo("Existing index ignored Path:" + dirPath)
        
# main

def main(argv):
    rootDir = ''
    mkIndexes = False
    shortURLs = False
    
    usage = 'Usage: sitebuilder.py [options]\nMost data such as paths and templates is defined in the script, and must be changed there.'
    parser = OptionParser(usage=usage)
    parser.add_option("-d", "--dir", dest="rootfile", default='.',
                  help="directory to start", metavar="FILE")
    parser.add_option("-i", "--indexes",
                  action="store_true", dest="indexes", default=False,
                  help="generate HTML indexes in every visited folder")
    parser.add_option("-l", "--links",
                  action="store_true", dest="links", default=False,
                  help="rewrite urls in links and images. Overwrites existing urls.")
    parser.add_option("-n", "--navbars",
                  action="store_true", dest="navbars", default=False,
                  help="insert navbars into pages")
    parser.add_option("-N", "--forcenavbars",
                  action="store_true", dest="forcednavbars", default=False,
                  help="Slow! Risky! insert navbars into pages, attempting to remove previous bars")
    parser.add_option("-s", "--shorturls",
                  action="store_true", dest="shorturls", default=False,
                  help="for indexes, generate urls as short (no -index.htm- extensions to directories, no extensions on files)")
                  
    (options, args) = parser.parse_args()
    
    # set and test these options
    #parser.print_help()
    if options.forcednavbars:
        options.navbars = True

            
    rootPath = os.path.abspath(options.rootfile)

    print('Root directory:', rootPath)
    print('Make Indexes:', options.indexes)
    print('Make Links:', options.links)
    print('Make Navbars:', options.navbars)
    print('Force Navbars:', options.forcednavbars)
    print('ShortURLs:', options.shorturls)
    
    #try:
    processDirs(rootPath, options)
    #except IOError:
      #  print('file would not open: %s' % inPath)
    #finally:

if __name__ == "__main__":
    main(sys.argv[1:])
