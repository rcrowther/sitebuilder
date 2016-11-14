
import os.path
from html.parser import HTMLParser
import sitebuilder.statlog
statlog = sitebuilder.statlog


## TODO: 
# Defend 'no href' matches
# More stripping
# logs

class CSSParser(HTMLParser):
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
        replaceMatch,
        statLog
        ):
            
        HTMLParser.__init__(self)
        
        self.output = []
        self.firstLink = False

        # settings
        self.newCode = newCode
        self.action = action
        #print ('action:' + str(action))
        self.replaceMatch = replaceMatch.strip()

        # setting-derived internal values
        self.extensionMatch = '.css'
        self.basenameMatch = replaceMatch + self.extensionMatch
        
        strippedCode = self.newCode.strip()
        # ensure empty if empty
        if (not strippedCode):
            self.insertCode = strippedCode
        else:
            self.insertCode = '<link rel="stylesheet" type="text/css" href="%s"/>' % (strippedCode)
        #print(self.insertCode)
        self.statLog = statLog 
    


        
    def p(self, value):
        self.output.append(value)

    def _matchesHrefBasename(self, tag, attrs):
        if (tag == 'link'):
            matches = next(e for e in attrs if e[0] == 'href')
            if (matches):
                basename = os.path.basename(matches[1])
                #print('m:' + basename)
                return basename == self.basenameMatch
            else:
                return False
        else:
            return False
            
    def _matchesHrefSuffix(self, tag, attrs):
        if (tag == 'link'):
            matches = next(e for e in attrs if e[0] == 'href')
            if (matches):
                #print('m:' + matches[1])
                href = matches[1]
                return href.endswith(self.extensionMatch)
            else:
                return False
        else:
            return False
        
    def handle_startendtag(self, tag, attrs):
        #print('tag: ' + tag)
        #print('attrs: ' + attrs[''])
        if (tag != 'link'):
                self.p(self.get_starttag_text())
        else:
            #print('tag: ' + tag)
            if (self.action == self.BELOW):
                # A pass-through ('handle_endtag' renders BELOW)
                self.p(self.get_starttag_text())

            if (self.action == self.ABOVE):
                # put replacement link in, print all others
                if (self.firstLink):
                    self.p(self.get_starttag_text())
                else:
                    self.firstLink = True
                    self.p(self.insertCode)
                    self.statLog.changed()        
                    self.p(self.get_starttag_text())                

            if (self.action == self.REPLACE_ALL):
                # put replacement link in, write no other link
                if (not self.firstLink):
                    self.firstLink = True
                    self.p(self.insertCode) 
                    self.statLog.changed()        
                if (not self._matchesHrefSuffix(tag, attrs)):
                    self.p(self.get_starttag_text())
                    
                                                
            if (self.action == self.REPLACE_NAMED_LINK):
                # if matches, use replacement, otherwise pass-through
                if (self._matchesHrefBasename(tag, attrs)):
                        self.p(self.insertCode)
                        self.statLog.changed()
                else:
                    self.p(self.get_starttag_text())


                
    def handle_starttag(self, tag, attrs):
        self.p(self.get_starttag_text())
        

    def handle_endtag(self, tag):
        # put 'below' new link in
        if (tag == 'head' and self.action == self.BELOW):
            self.p(self.insertCode)
            self.statLog.changed()         
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
    replaceMatch,
    statLog
    ):
    try:
        # convert_charrefs will default to True in py3.5:
        parser = CSSParser(
            newCode,
            action,
            replaceMatch,
            statLog,
            convert_charrefs=False
            )
    except TypeError:
        # convert_charrefs was added in py3.4:
        parser = CSSParser(
            newCode,
            action,
            replaceMatch,
            statLog
            )

 
        
    parser.feed(src)

    return "".join(parser.output)
