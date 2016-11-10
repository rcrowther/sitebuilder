
## TODO:
# use a builder?
#x should write navbars into indexes?
# check base dir handling
#x dont build indexes for empty folders?
## extra
# display book
# alternatives to order entries?
# import header material?

import os.path 
from os import walk
import statlog



### User vars ###

# Change for new navbar. Should start with a 'header' or 'nav' element.
#bodyHeaderMarkup = '<header id="site-nav"><nav><ul><li><a href="/articles/">Articles</a></li><li><a href="/projects/">Projects</a></li><li><a href="/about.htm">About</a></li></ul></nav></header>'




# Change for new intro to indexes
def webPageOpen(f, title, headHTML, headerHTML):
    f.write('<!DOCTYPE html>\n<html>\n<head>\n<title>{0}</title>\n'.format(title))
    f.write(headHTML)
    f.write('</head>\n<body>')
    f.write(headerHTML)
    f.write('<article>\n<h1>')
    f.write(title)
    f.write('</h1>\n')


# Change for new outro to indexes
def webPageClose(f):
    f.write('</article></body></html>')
    
def indexOpenTemplate():
    '''
    Open the index. 
    Usually a 'nav' tag.
    '''
    return '<nav class="toc">\n'
        
def indexCloseTemplate():
    '''
    Close the index. 
    Usually a '/nav' tag.
    '''
    return '</nav>\n'

def indexSectionOpenTemplate():
    '''
    Open the two lists of dirs and files. 
    Usually a 'ul' tag.
    '''
    return '<ul class="wide">\n'
        
def indexSectionCloseTemplate():
    '''
    Close the two lists of dirs and files. 
    Usually a '/ul' tag.
    '''
    return '</ul>\n'
        
def indexLinkTemplate(href, text):
    return '<li><a href="{0}">{1}</a></li>\n'.format(href, text)




### Internal ###

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
        '''
        Sort a list in dictionary style.
        Three lists concatenated. Lists are split by first character; 
        symbols, numerics, then alphabetic.
        Each list is ordered according to character encoding.
        '''
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
        
        
def mkIndex(
    headHTML,
    headerHTML,
    dirPath,
    dirNameList,
    entryNameList,
    absoluteURLs, 
    absoluteRoot,
    shortURLs
    ):

    p =  os.path.join(dirPath, 'index.htm')
        
    try:
        f = open(p, 'w')

        # make page title
        # Uppercase fails badly in Unicode. Use CSS? Probably better.
        lastElem = os.path.basename(dirPath).replace('_', ' ')
        title = "defaulty" if(not lastElem or lastElem == '.') else lastElem
        
        webPageOpen(f, title, headHTML, headerHTML)

        f.write( indexOpenTemplate() )
        f.write( indexSectionOpenTemplate() )


        # directories
        dfpl = sortRespectingNumerics(dirNameList)

        for bn in dfpl:
            url = os.path.join(absoluteRoot, bn) if (absoluteURLs) else bn
            # if not given index file target, enforce final slash 
            href = url + '/' if shortURLs else url + os.path.sep + 'index.htm'
             
            txt = bn.replace('_', ' ')
            f.write( indexLinkTemplate(href, txt) )
            

        f.write( indexSectionCloseTemplate() )
        f.write( indexSectionOpenTemplate() )


        # files
        rfpl = sortRespectingNumerics(entryNameList)

        for bn in rfpl:
            # chop the extension, only .htm or .html
            noExtPath = bn[: bn.rfind('.')]
            hrefBN = noExtPath if shortURLs else bn
            href = os.path.join(absoluteRoot, hrefBN) if (absoluteURLs) else hrefBN 
            txt = noExtPath.replace('_', ' ')
            f.write( indexLinkTemplate(href, txt) )

        f.write( indexSectionCloseTemplate() )
        f.write( indexCloseTemplate() )

        webPageClose(f)

        f.close()
    except IOError:
        print('index file can not be created (exists? permissions?): %s' % p)



def containsIndex(filenames):
    r = False
    for e in filenames:
        r = r or e.startswith('index')
    return r
    
def processDirs(
    headHTML,
    headerHTML,
    rootPath,
    acceptList,
    replace,
    absoluteURLs,
    absoluteRoot,
    shortURLs,
    statLog
    ):

    # dirPath = full URL. dirNames/entrynames are basenames (with extension)
    # dirpath the same as rootPath... use dirPath as normalised
    (dirPath, dirNames, entryNames) = next(walk(rootPath), (None, [], []))

    #print(dirPath)
    #print(', '.join(dirNames))
    #print(', '.join(entryNames))
    
    ##TODO: if none?
    
    # filter directory names
    # for hidden
    dirNameList = []
    for n in dirNames:
        first = n[0]
        if first != '.' and first != '~':
            dirNameList.append(n)
            
            
    # filter entry names
    # get this test first
    hasIndex = containsIndex(entryNames)
    
    # for hidden and extensions
    entryNameList = []
    for n in entryNames:
        first = n[0]
        if first != '.' and first != '~' and n.endswith(acceptList) and not n.startswith('index'):
            entryNameList.append(n)
              


    # test if to create, if so, run
    #print('index')
    if (hasIndex and not replace):
        #TODO; log
        print("Existing index ignored Path:" + dirPath)
    else:
        #print('create index')
        statLog.changed()
        mkIndex(
            headHTML,
            headerHTML,
            dirPath,
            dirNameList,
            entryNameList, 
            absoluteURLs,
            absoluteRoot,
            shortURLs
            )
        


def run(
    headHTML,
    headerHTML,
    dirPath,
    replace,
    absoluteURLs,
    absoluteRoot,
    shortURLs,
    statLog
    ):


    acceptList = ('.htm', '.html')
    processDirs(
        headHTML,
        headerHTML,
        dirPath,
        acceptList,
        replace,
        absoluteURLs,
        absoluteRoot, 
        shortURLs,
        statLog
        )

