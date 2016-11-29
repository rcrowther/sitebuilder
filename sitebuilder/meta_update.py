
import os.path
from html.parser import HTMLParser
import sitebuilder.statlog
statlog = sitebuilder.statlog


## TODO: 
# Defend 'no href' matches
# More stripping
# logs

class MetaParser(HTMLParser):
    '''
    Both replacements can be zero. An empty string is then used, no template.
    This will then delete the matches (either ALL or NAMED_LINK). 
    REPLACE_NAMED_LINK Derives the basename, so is smart enough, for
    example, not to mix ''book' with 'webbook'.
    REPLACE_ALL An empty match will cause all strings to be replaced
    (likey, this is unintended behaviour).
    @param action 0 = insert above, 1 = insert below, 2 = replace all, 
    3 = replace link with named match
    '''
    ABOVE = 0
    BELOW = 1
    REPLACE_ALL = 2
    REPLACE_NAMED_LINK = 3
    
    def __init__(
        self,
        newCode,
        action,
        statLog
        ):
            
        HTMLParser.__init__(self)
        
        self.output = []
        #self.firstLink = False

        # settings
        self.newCode = newCode.strip()
        self.action = action
        #print ('action:' + str(action))
        
        self.statLog = statLog 
    


        
    def p(self, value):
        self.output.append(value)


            

        
    def handle_startendtag(self, tag, attrs):
        #print('tag: ' + tag)
        #print('attrs: ' + attrs[''])
        if (tag != 'meta' or self.action == self.ABOVE):
            self.p(self.get_starttag_text())



                
    def handle_starttag(self, tag, attrs):
        self.p(self.get_starttag_text())
        if (tag == 'head'):
            # print new meta
            self.p(self.newCode)
            self.statLog.changed()        


    def handle_endtag(self, tag):        
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
    newCode,
    action,
    statLog
    ):
    try:
        # convert_charrefs will default to True in py3.5:
        parser = MetaParser(
            newCode,
            action,
            statLog,
            convert_charrefs=False
            )
    except TypeError:
        # convert_charrefs was added in py3.4:
        parser = MetaParser(
            newCode,
            action,
            statLog
            )

 
        
    parser.feed(src)

    return "".join(parser.output)
