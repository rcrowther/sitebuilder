import os.path 

from html.parser import HTMLParser

import sitebuilder.statlog
statlog = sitebuilder.statlog

##TODO:
# rename
# live without the extra methos, only start/end?

class TheHTMLParser(HTMLParser):
    def __init__(
        self,
        newHeaderHTML,
        overwriteHeader,
        statLog
        ):
        HTMLParser.__init__(self)
        
        self.prevTag = None
        self.output = []
        self.firstBodyElem = False
        self.headerForRemovalOpen = False
        self.deleteTagcontents = False

        # settings
        self.newHeaderHTML = newHeaderHTML
        self.overwriteHeader = overwriteHeader

        self.statLog = statLog

        
    def p(self, value):
        if(not self.deleteTagcontents):
            self.output.append(value)

    def handle_startendtag(self, tag, attrs):
        self.p(self.get_starttag_text())


                
    def handle_starttag(self, tag, attrs):
        # For headers
        if (self.firstBodyElem):
            self.firstBodyElem = False

            if (tag != 'header'):
                self.p(self.newHeaderHTML)
                self.statLog.changed()
                # write the non-header tag
                self.p(self.get_starttag_text())
                
            if (tag == 'header'): 
                if (self.overwriteHeader):
                    self.p(self.newHeaderHTML)
                    self.statLog.changed()
                    # delete the old tag pair
                    self.headerForRemovalOpen = True
                    self.deleteTagcontents = True                
                else:
                    # write the non-header tag
                    self.p(self.get_starttag_text())
        else:                
            if (tag == 'body'):
                self.firstBodyElem = True
            self.p(self.get_starttag_text())
        

    def handle_endtag(self, tag):
        if(self.headerForRemovalOpen):
            if(tag == 'header'):
                # don't write original tag, but cease to delete 
                self.headerForRemovalOpen = False
                self.deleteTagcontents = False
        else:
            self.p("</%s>" % (tag,))


    def handle_data(self, data):
        self.p(data)

    def handle_comment(self, data):
        self.p("<!--%s-->" % (data,))

    def handle_entityref(self, name):
        self.p("&%s;" % (name,))

    def handle_charref(self, name):
        self.p("&#%s;" % (name,))

    def handle_decl(self, data):
        self.p("<!%s>" % (data,))

    def handle_pi(self, data):
        self.p("<?%s>" % (data,))

def run(
    src,
    newHeaderHTML,
    overwriteHeader,
    statLog
    ):
    
    try:
        # convert_charrefs will default to True in py3.5:
        parser = TheHTMLParser(
            newHeaderHTML,
            overwriteHeader,
            statLog,
            convert_charrefs=False
            )
    except TypeError:
        # convert_charrefs was added in py3.4:
        parser = TheHTMLParser(
            newHeaderHTML,
            overwriteHeader,
            statLog
            )

    parser.feed(src)

    return "".join(parser.output)

