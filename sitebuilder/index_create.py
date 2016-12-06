
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
from html.parser import HTMLParser
import sitebuilder.statlog
statlog = sitebuilder.statlog



### User vars ###

# Change for new navbar. Should start with a 'header' or 'nav' element.
#bodyHeaderMarkup = '<header id="site-nav"><nav><ul><li><a href="/articles/">Articles</a></li><li><a href="/projects/">Projects</a></li><li><a href="/about.htm">About</a></li></ul></nav></header>'




# Change for new intro to indexes
def webPageOpen(f, title, headHTML, headerHTML):
    f.write('<!DOCTYPE html>\n<html>\n<head>\n')
    f.write(headHTML)
    f.write('</head>\n<body>\n')
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



### Header Parser ###
class HeaderParser(HTMLParser):
    '''
    Parse for contents of 'head', and a first-child header in 'body'.
    @param return tuple of parse results. HTML is returned without 'head' or 'header' tags.
    '''
    
    def __init__(
        self
        ):
            
        HTMLParser.__init__(self)
        
        self.builder = []
        self.readingHead = False
        self.readingHeader = False
        self.firstElemInBody = False

        self.headHTML = []
        self.headerHTML = []
    


        
    #def p(self, value):
     #   self.builder.append(value)
        
    def clearBuilder(self):
        self.builder = []
             
    def filteredP(self, value):
        if(self.readingHead or self.readingHeader):
            self.builder.append(value)

        
    def handle_startendtag(self, tag, attrs):
        #print('tag: ' + tag)
        #print('attrs: ' + attrs[''])
        self.filteredP(self.get_starttag_text())

                
    def handle_starttag(self, tag, attrs):
        if (tag == 'head'):
            self.readingHead = True
        else:
            if (self.firstElemInBody):
                if(tag == 'header'):
                    self.readingHeader = True
                self.firstElemInBody = False  
            else:
                if (tag == 'body'):
                    self.firstElemInBody = True
                else:
                    self.filteredP(self.get_starttag_text())


    def handle_endtag(self, tag):
        # put 'below' new link in
        if (tag == 'head'):
            self.readingHead = False
            self.headHTML = self.builder
            self.clearBuilder()
        else:
            if (tag == 'header' and self.readingHeader):
                self.readingHeader = False
                self.headerHTML = self.builder
                self.clearBuilder()
            else:
                self.filteredP("</%s>" % (tag,))

    def handle_data(self, data):
        self.filteredP(data)

    def handle_comment(self, data):
        self.filteredP("<!--%s-->" % (data,))

    def handle_entityref(self, name):
        self.filteredP("&%s;" % (name,))

    def handle_charref(self, name):
        self.filteredP("&#%s;" % (name,))

    def handle_decl(self, data):
        self.filteredP("<!%s>" % (data,))

    def handle_pi(self, data):
        self.filteredP("<?%s>" % (data,))

    def result(self):
        return ("".join(self.headHTML).strip(), "".join(self.headerHTML).strip())

def getHeaders(
    srcPath
    ):
    try:
        # convert_charrefs will default to True in py3.5:
        parser = HeaderParser(
            convert_charrefs=False
            )
    except TypeError:
        # convert_charrefs was added in py3.4:
        parser = HeaderParser(
            )

    # protect
    srcHTML = "".join(open(srcPath).readlines()) 
        
    parser.feed(srcHTML)

    return parser.result()


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


def pageTitle(dirPath):
    # Make page title        
    # get a tail....
    head, tail = os.path.split(dirPath)
    # if tail fails, likely passed a slash-ended directory, so go one higher...
    lastElem = tail if (tail) else os.path.basename(head)
    
    # if left at a root (who does this?) default, 
    # otherwise substitute out underscores for the title.
    # Uppercase/capitalising fails badly in Unicode. Leave styling to CSS.
    return "defaulty" if (not lastElem or lastElem == '.') else lastElem.replace('_', ' ')


def mkIndex(
    headHTML,
    headerHTML,
    dirPath,
    indexPath,
    dirNameList,
    entryNameList,
    absoluteURLs, 
    absoluteRoot,
    shortURLs,
    insertHeaders
    ):

    p =  os.path.join(dirPath, 'index.htm')
    humanTitle = pageTitle(dirPath)
    
    # an index exists (and is being replaced) and needs headers
    # get the head data
    respectingCurrentHeadHTML = ''
    respectingCurrentHeaderHTML = ''
    
    if (indexPath and insertHeaders):
        # use what is in current file
        (currentHeadHTML, currentHeaderHTML) = getHeaders(p)
        respectingCurrentHeadHTML = currentHeadHTML
        if(currentHeaderHTML):
            respectingCurrentHeaderHTML = '<header>\n' + currentHeaderHTML + '</header>\n'
    else:
        # construct from given data
        titleHTML = '<title>{0}</title>\n'.format(humanTitle)
        respectingCurrentHeadHTML = titleHTML + headHTML
        respectingCurrentHeaderHTML = headerHTML 
    try:
        f = open(p, 'w')

        webPageOpen(
            f,
            humanTitle,
            respectingCurrentHeadHTML, 
            respectingCurrentHeaderHTML
            )

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


    
def processDirs(
    headHTML,
    headerHTML,
    rootPath,
    acceptList,
    replace,
    absoluteURLs,
    absoluteRoot,
    shortURLs,
    insertHeaders,
    statLog
    ):

    # dirPath = full URL. dirNames/entrynames are basenames (with extension)
    # dirpath the same as rootPath... use dirPath as normalised
    (dirPath, dirNames, entryNames) = next(walk(rootPath), (None, [], []))

    #print(dirPath)
    #print(', '.join(dirNames))
    #print(', '.join(entryNames))
    
    ##TODO: if none?
    
    # filter directory names for hidden
    dirNameList = []
    for n in dirNames:
        first = n[0]
        if first != '.' and first != '~':
            dirNameList.append(n)
            
            
    # filter entry names
    # for hidden and extensions
    entryNameList = []
    for n in entryNames:
        first = n[0]
        if first != '.' and first != '~' and n.endswith(acceptList):
            entryNameList.append(n)
            
    # split entry names for 'index'
    # only looking for one, discard overwrite extra
    nonIndexEntryNameList = []
    indexEntryName = None
    for n in entryNameList:
        first = n[0]
        if n.startswith('index'):
            indexEntryName = n
        else:
            nonIndexEntryNameList.append(n)
            
    print('ip:'+ str(indexEntryName))

    # test if to create, if so, run
    #print('index')
    if (indexEntryName and not replace):
        #TODO; log?
        print("Existing index, no index generated. Path: " + dirPath)
    else:
        #print('create index')
        statLog.changed()
        mkIndex(
            headHTML,
            headerHTML,
            dirPath,
            indexEntryName,
            dirNameList,
            nonIndexEntryNameList, 
            absoluteURLs,
            absoluteRoot,
            shortURLs,
            insertHeaders
            )
        


def run(
    headHTML,
    headerHTML,
    dirPath,
    replace,
    absoluteURLs,
    absoluteRoot,
    shortURLs,
    insertHeaders,
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
        insertHeaders,
        statLog
        )

