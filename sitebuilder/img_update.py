import re
import os.path 
import sitebuilder.statlog
statlog = sitebuilder.statlog


# match img links
srcRe = re.compile(r'src=\"([^\"]+)"', re.IGNORECASE)

def rewriteImgURLs(content, newRootPath, statLog):

    def imgRep(m):
        p = os.path.join(newRootPath, os.path.basename(m.group(1)))
        statLog.changed()
        return 'src=\"' + p + '"'

    return  re.sub(srcRe, imgRep, content)


    
def run(
    src,
    newRootPath,
    statLog
    ):
    return rewriteImgURLs(src, newRootPath, statLog)

