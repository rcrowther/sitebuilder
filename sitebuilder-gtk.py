#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gio, GLib, Gdk

import glob
import os.path
from os import walk

import shutil

# how does 
#/usr/bin/apertium-tolk
# see
#/usr/share/pyshared/tolk?

import sitebuilder
statlog = sitebuilder.statlog
#import header_merge
#import css_update
#import js_update
#import index_create
#import img_update
#_ = sitebuilder._
#import header_merge
#import css_update
#import js_update
#import index_create
#import img_update

#import statlog

'''
Perform various actions on website pages.

This GTK interface needs a GSettings schema installing.
'''

## TODO:
# target navigation to single files
# Compressor?
# advanced logs?
# redo commandline
# entry keystroke on some textboxes
# spinner not showing?
# DRY up a bit

#################
### User Data ##
#################

GSCHEMA = "uk.co.archaicgroves.sitebuilder-gtk"
DATA_KEY = 'data'


# a(targetPathStr, recursive, headerStr, headerOverwrite, 
# indexHeadHTML, indexOverwrite, indexAbsoluteURLs, indexAbsoluteRootPath, indexShortURLs, indexInsertBodyHeader
# metaStr, metaButtonIndex,
# cssStr, cssButtonIndex, cssMatch,
# jsStr, jsOverwrite, jsMatch, 
# imgStr)
DATA_SIGNATURE = "a(sbsbsbbsbbsisississ)"




############
# Internal #
############

class MyWindow(Gtk.Window):

    # URL substitution actions
    ABOVE = 0
    BELOW = 1
    REPLACE_ALL = 2
    REPLACE_NAMED_LINK = 3
    
    
    ## GUI mods/accessors
    
    def message(self, message):
        self.statusbar.set_text(message)

    def request(self, message):
        msg = '[<span foreground="blue">request</span>] ' + message 
        self.statusbar.set_markup(msg)
        
    def warning(self, message):
        msg = '[<span foreground="orange">warning</span>] ' + message 
        self.statusbar.set_markup(msg)
        
    def error(self, message):
        msg = '[<span foreground="red">error</span>] <span foreground="red">' + message + '</span>'
        self.statusbar.set_markup(msg)

    def clearStatus(self):
        self.statusbar.set_text('')
    
    def statMessage(self, statLog):
        eLen = len(statLog.errors)
        if (eLen > 0):
            self.error("{0} reported\nLast error:{1}".format(eLen, statLog.errors[eLen - 1]))
        else:
            self.message("{0} file(s) touched, {1} file(s) altered".format(statLog.touchedCount, statLog.changedCount))
            
    def spinnerStop(self):
        self.spinner.stop()
        #self.spinner.hide()
            
    def spinnerStart(self):
        self.spinner.start()
        #self.spinner.show()
        

    def getBufferText(self, textBuffer):
        start = textBuffer.get_start_iter()
        end = textBuffer.get_end_iter()
        return  textBuffer.get_text(start, end, True)
		
             
    def getActiveToggle(self, group):
        i = 0
        for b in reversed(group):
            if b.get_active():
                break
            i += 1
        return i

    def setActiveByIndex(self, group, index):
        idx = len(group) - 1 - index
        group[idx].set_active(True)
    
    
        
    ## GSettings 
    
    def saveSettings(self):
        print('saving settings')
        targetPathStr = self.targetPath.get_text()
        targetRecursive = self.recursiveVisit.get_active()
        
        headerStr = self.getBufferText(self.headerBuffer)
        headerOverwrite = self.overwriteHeader.get_active()

        indexStr = self.getBufferText(self.indexHeadHTML)
        indexOverwrite = self.overwriteIndexes.get_active()
        indexAbsoluteURLs = self.indexAbsoluteURLs.get_active()
        indexURLRootPath = self.indexAbsoluteRoot.get_text()
        indexShortURLs = self.indexShortURLs.get_active() 
        indexInsertBodyHeader = self.indexInsertBodyHeader.get_active() 
        
        metaStr = self.getBufferText(self.metaHTML)
        metaButtonIdx = self.getActiveToggle(self.MetaGroup)
        
        cssStr = self.cssPath.get_text()
        cssButtonIdx = self.getActiveToggle(self.CSSGroup)
        cssMatchStr = self.matchCSS.get_text()

        jsStr = self.jsPath.get_text()
        jsButtonIdx = self.getActiveToggle(self.JSGroup)
        jsMatchStr = self.matchJS.get_text()
				
        imgStr = self.imgPath.get_text()

        data = [(
        targetPathStr,
        targetRecursive,
        headerStr,
        headerOverwrite,
        indexStr,
        indexOverwrite,
        indexAbsoluteURLs,
        indexURLRootPath,
        indexShortURLs,
        indexInsertBodyHeader, 
        metaStr,
        metaButtonIdx,
        cssStr,
        cssButtonIdx,
        cssMatchStr,
        jsStr,
        jsButtonIdx,
        jsMatchStr,
        imgStr
        )]
        #print(tmpPathStr)

        gsettingBackups = GLib.Variant(DATA_SIGNATURE, data)
        gsettings.set_value(DATA_KEY, gsettingBackups)
        
    def loadSettings(self):
        print('loading settings')
        gsettingData = gsettings.get_value(DATA_KEY)
        if (len(gsettingData) == 0):
            #self._guiClear()
            self.message('no settings found')
        else:
            # Currently preset to load the first backup project
            # or group in gsettingRet:
            datum = gsettingData[0]
            self.targetPath.set_text(datum[0])
            self.recursiveVisit.set_active(datum[1])
            
            self.headerBuffer.set_text(datum[2])
            self.overwriteHeader.set_active(datum[3])
	
            self.indexHeadHTML.set_text(datum[4])
            self.overwriteIndexes.set_active(datum[5])
            self.indexAbsoluteURLs.set_active(datum[6])
            self.indexAbsoluteRoot.set_text(datum[7])
            self.indexShortURLs.set_active(datum[8])            
            self.indexInsertBodyHeader.set_active(datum[9])
             

            self.metaHTML.set_text(datum[10])
            self.setActiveByIndex(self.MetaGroup, datum[11])
            
            self.cssPath.set_text(datum[12])
            self.setActiveByIndex(self.CSSGroup, datum[13])
            self.matchCSS.set_text(datum[14])
	
            self.jsPath.set_text(datum[15])
            self.setActiveByIndex(self.JSGroup, datum[16])
            self.matchJS.set_text(datum[17])
					
            self.imgPath.set_text(datum[18])



    ## Actions

    def _notebookSwitched(self, notebook, page, pageNum):
        # clear status
        self.clearStatus()
        
        
            
    ## TODO Remove hidden files
    class _dir_iter():
        def __init__(self, path, recursive):
            self.recursive = recursive
            self.it = walk(path)
            # This kind of thuggery is anti-Python, but if this is an
            # iterator...
            # To include the base path in the iterator,
            # pre-load the iterator batches with an empty
            # path converted to an iterator. This concatenates
            # to base, as the first item (root), then the batch loading
            # kicks in (if recursing) and traversal continues downwards. 
            self.currentPath, self.currentEntryIt = path, iter(['']) 
            
        def _nextBatch(self):
            try:
                currentPath, currentEntries, _ = next(self.it)
            except StopIteration:
                raise StopIteration
            return (currentPath, iter(currentEntries))
            
        def __iter__(self):
            return self
            
        def __next__(self):
            try:
                #skip linux/Mac hidden/tmp
                nxt = None
                while True:
                    nxt =  next(self.currentEntryIt)
                    bn = os.path.basename(nxt)
                    if (not bn.startswith('.') and not bn.endswith('~')):
                        break
                return os.path.join(self.currentPath, nxt)
            except StopIteration:
                try:
                    if (not self.recursive):
                        raise StopIteration
                    self.currentPath, self.currentEntryIt = self._nextBatch()
                    return self.__next__()
                except StopIteration:
                    raise StopIteration


    class _entry_iter():
        def __init__(self, path, recursive):
            self.recursive = recursive
            self.it = walk(path) 
            self.currentPath, self.currentEntryIt = self._nextBatch()
            
        def _nextBatch(self):
            try:
                currentPath, _, currentEntries = next(self.it)
            except StopIteration:
                raise StopIteration
            return (currentPath, iter(currentEntries))
            
        def __iter__(self):
            return self
            
        def __next__(self):
            nxt = None
            try:
                #skip linux/Mac hidden/tmp
                while True:
                    nxt =  next(self.currentEntryIt)
                    bn = os.path.basename(nxt)
                    if (not bn.startswith('.') and not bn.endswith('~')):
                        break
                return os.path.join(self.currentPath, nxt)
            except StopIteration:
                try:
                    if (not self.recursive):
                        raise StopIteration
                    self.currentPath, self.currentEntryIt = self._nextBatch()
                    return self.__next__()
                except StopIteration:
                    raise StopIteration

        
    def _modification_target_entry_iter(self):
        path = self.targetPath.get_text().strip()
        if (not path):
            self.warning('Target directory path is empty!')
            return None
        else:
            recurse = self.recursiveVisit.get_active()
            return self._entry_iter(path, recurse)
        
    def _modification_target_dir_iter(self):
        path = self.targetPath.get_text().strip()
        if (not path):
            self.warning('Target directory path is empty!')
            return None            
        else:
            recurse = self.recursiveVisit.get_active()
            return self._dir_iter(path, recurse)



    # protect empty/non-existent paths?      
    def _insertHeaders(self, widget):
        self.clearStatus()
            
        b = self.getBufferText(self.headerBuffer).strip()
        o = self.overwriteHeader.get_active()

        if (not b and not o):
            self.warning("empty insert?")
        else:
            targetIt = self._modification_target_entry_iter()
            if (targetIt):
                sl = statlog.statLog()
                self.spinnerStart()
                for p in targetIt:
                    sl.touched()
                    src = "".join(open(p).readlines())            
                    modified = sitebuilder.header_merge.run(
                        src,
                        b,
                        o,
                        sl
                        )
                    with open(p, 'w') as out:
                        out.write(modified)
                self.spinnerStop()
                self.statMessage(sl)
                
    def _createIndexes(self, widget):
        self.clearStatus()

        headHTML = self.getBufferText(self.indexHeadHTML)
        o = self.overwriteIndexes.get_active()
        a = self.indexAbsoluteURLs.get_active()
        r = self.indexAbsoluteRoot.get_text().strip()
        s = self.indexShortURLs.get_active()
        h = self.indexInsertBodyHeader.get_active()
        
        if (not r and a):
            self.warning("root path empty for absolute URLs?")
        else:
            ## TODO: not including self?
            targetIt = self._modification_target_dir_iter()
            if (targetIt):
                bodyHeaderMarkup = self.getBufferText(self.headerBuffer).strip() if (h) else ''
                
                sl = statlog.statLog()
                self.spinnerStart()
                for p in targetIt:
                    sl.touched()
                    sitebuilder.index_create.run(
                        headHTML,
                        bodyHeaderMarkup,
                        p,
                        o,
                        a,
                        r,
                        s,
                        sl
                        )
                self.spinnerStop()
                self.statMessage(sl)
                
                
    def _insertMeta(self, widget):
        self.clearStatus()
        
        meta = self.getBufferText(self.metaHTML).strip()

        actionIdx = self.getActiveToggle(self.MetaGroup)

        if ((actionIdx == self.ABOVE) and not meta):
            self.warning("empty insert?")
        else:
            targetIt = self._modification_target_entry_iter()
            if (targetIt):                
                sl = statlog.statLog()
                self.spinnerStart()
                for p in targetIt:
                    sl.touched()
                    src = "".join(open(p).readlines())  
                    modified = sitebuilder.meta_update.run(
                        src,
                        meta,
                        actionIdx,
                        sl
                        )
                    with open(p, 'w') as out:
                        out.write(modified)
                self.spinnerStop()
                self.statMessage(sl)
                        
                                  
    def _insertCSS(self, widget):
        self.clearStatus()
        
        css = self.cssPath.get_text().strip()
        actionIdx = self.getActiveToggle(self.CSSGroup)
        cssMatchStr = self.matchCSS.get_text()

        if ((actionIdx == self.ABOVE or actionIdx == self.BELOW) and not css):
            self.warning("empty insert?")
        else:
            if (actionIdx == self.REPLACE_NAMED_LINK and not cssMatchStr):
                self.warning("empty match for 'replace all'")
            else:
                targetIt = self._modification_target_entry_iter()
                if (targetIt):                
                    sl = statlog.statLog()
                    self.spinnerStart()
                    for p in targetIt:
                        sl.touched()
                        src = "".join(open(p).readlines())  
                        modified = sitebuilder.css_update.run(
                            src,
                            css,
                            actionIdx,
                            cssMatchStr,
                            sl
                            )
                        with open(p, 'w') as out:
                            out.write(modified)
                    self.spinnerStop()
                    self.statMessage(sl)


    def _insertJS(self, widget):
        self.clearStatus()

        js = self.jsPath.get_text()
        actionIdx = self.getActiveToggle(self.JSGroup)
        jsMatchStr = self.matchJS.get_text().strip()


        if ((actionIdx == self.ABOVE or actionIdx == self.BELOW) and not js):
            self.warning("empty insert?")
        else:
            if (actionIdx == self.REPLACE_NAMED_LINK and not jsMatchStr):
                self.warning("empty match for 'replace all'")
            else:
                targetIt = self._modification_target_entry_iter()
                if (targetIt):
                    sl = statlog.statLog()                    
                    self.spinnerStart()
                    for p in targetIt:
                        sl.touched()
                        src = "".join(open(p).readlines())  
                        modified = sitebuilder.js_update.run(
                            src,
                            js,
                            actionIdx,
                            jsMatchStr,
                            sl
                            )
                        with open(p, 'w') as out:
                            out.write(modified)
                    self.spinnerStop()
                    self.statMessage(sl)

				
    def _updateImgHref(self, widget):
        self.clearStatus()

        rootP = self.imgPath.get_text()
        if (not rootP):
            self.warning("empty re-root path?")
        else:
            targetIt = self._modification_target_entry_iter()
            if (targetIt):            
                sl = statlog.statLog()
                self.spinnerStart()
                for p in targetIt:
                    sl.touched()
                    src = "".join(open(p).readlines())
                    modified = sitebuilder.img_update.run(
                        src,
                        rootP,
                        sl
                        )
                    with open(p, 'w') as out:
                        out.write(modified)
                self.spinnerStop()
                self.statMessage(sl)

			
            
            	
    ## Widgets


    def _selectTargetFolder(self, widget):
            dialog = Gtk.FileChooserDialog("Please choose a folder", self,
                Gtk.FileChooserAction.SELECT_FOLDER,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                 "Select", Gtk.ResponseType.OK))
            dialog.set_default_size(800, 400)
            # contrary to GTK3 advice
            dialog.set_current_folder(self.targetPath.get_text())
            
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                path = dialog.get_filename()
                self.targetPath.set_text(path)
                #self._guiClear()
                self.message('New target folder')
            elif response == Gtk.ResponseType.CANCEL:
                self.message('Selection cancelled')
    
            dialog.destroy()
         
         
    def targetPage(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_homogeneous(False)
		
		## Target directory
        label = Gtk.Label()
        label.set_markup ("<b>Target directory</b>")
        label.set_halign(Gtk.Align.START)  
        box.pack_start(label, False, True, 0)
        
        selectTargetButton = Gtk.Button(label="Select target directory")
        selectTargetButton.connect("clicked", self._selectTargetFolder)
        box.pack_start(selectTargetButton, False, True, 0)
        
        self.targetPath = Gtk.Entry()
        self.targetPath.set_margin_bottom(8)
        box.pack_start(self.targetPath, False, True, 0)

        self.recursiveVisit = Gtk.CheckButton.new_with_label("Visit recursive")
        self.recursiveVisit.set_margin_bottom(8)
        box.pack_start(self.recursiveVisit, False, False, 0)       


        #separator = Gtk.Separator()
        #separator.set_margin_bottom(8)
        #box.pack_start(separator, False, True, 4)

        return box
        
        
         
    def headersPage(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_homogeneous(False)

		## Headers
        label = Gtk.Label()
        label.set_markup ("Insert at top of body:\n<i>(default inserts if not exists)</i>")
        label.set_halign(Gtk.Align.START)  
        box.pack_start(label, False, True, 0)
        
        self.headerView = Gtk.TextView()
        self.headerView.set_margin_bottom(8)
        self.headerView.set_wrap_mode(Gtk.WrapMode.WORD)
        self.headerView.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(1,1,1,.5))
        box.pack_start(self.headerView, True, True, 0)
        
        self.headerBuffer = self.headerView.get_buffer()

        self.overwriteHeader = Gtk.CheckButton.new_with_label("Replace existing. Text can be empty for delete")
        box.pack_start(self.overwriteHeader, False, False, 0)
        
            
        button = Gtk.Button(label="Change headers")
        button.connect("clicked", self._insertHeaders)
        button.set_margin_bottom(8)
        box.pack_start(button, False, False, 0)        

        return box

        
         
    def indexesPage(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_homogeneous(False)        

		## Indexes

        label = Gtk.Label()
        label.set_markup ("Extra markup for webpage head:\n<i>Meta/CSS/script/ etc.</i>")
        label.set_halign(Gtk.Align.START)  
        box.pack_start(label, False, True, 0)
                
        view = Gtk.TextView()
        view.set_margin_bottom(8)
        view.set_wrap_mode(Gtk.WrapMode.WORD)
        view.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(1,1,1,.5))
        box.pack_start(view, True, True, 0)
        
        self.indexHeadHTML = view.get_buffer()
                
                
        #.get_active().
        self.overwriteIndexes = Gtk.CheckButton.new_with_label("Overwrite existing")
        box.pack_start(self.overwriteIndexes, False, False, 0)


        self.indexAbsoluteURLs = Gtk.CheckButton.new_with_label("Generate absolute URLs")
        box.pack_start(self.indexAbsoluteURLs, False, False, 0)
       
        label = Gtk.Label()
        label.set_markup("root for absolute indexes:")
        label.set_halign(Gtk.Align.START)  
        box.pack_start(label, False, True, 0)
                        
        self.indexAbsoluteRoot = Gtk.Entry()
        box.pack_start(self.indexAbsoluteRoot, False, True, 0)
         
        self.indexShortURLs = Gtk.CheckButton.new_with_label("Generate short URLs")
        box.pack_start(self.indexShortURLs, False, False, 0)        
        
        self.indexInsertBodyHeader = Gtk.CheckButton.new_with_label("Insert page header from 'Page Headers' tab")
        box.pack_start(self.indexInsertBodyHeader, False, False, 0) 
        
        button = Gtk.Button(label="Make indexes")
        button.connect("clicked", self._createIndexes)
        button.set_margin_bottom(8)
        box.pack_start(button, False, False, 0)

        return box

    def metaPage(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_homogeneous(False)
    
    
		## Meta elements
        label = Gtk.Label()
        label.set_markup("<b>Meta elements</b>")
        label.set_halign(Gtk.Align.START)  
        box.pack_start(label, False, True, 0)

        label = Gtk.Label()
        label.set_markup("insert:\n<i>(full element, replace can be empty for delete)</i>")
        label.set_halign(Gtk.Align.START)  
        box.pack_start(label, False, True, 0)
                
        view = Gtk.TextView()
        view.set_margin_bottom(8)
        view.set_wrap_mode(Gtk.WrapMode.WORD)
        view.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(1,1,1,.5))
        box.pack_start(view, True, True, 0)
        self.metaHTML = view.get_buffer()

        self.insertAboveMeta = Gtk.RadioButton.new_with_label(None, "Insert below <head>")
        box.pack_start(self.insertAboveMeta, False, False, 0)      

        self.replaceAllMeta = Gtk.RadioButton.new_from_widget(self.insertAboveMeta)
        self.replaceAllMeta.set_label("Replace existing")
        box.pack_start(self.replaceAllMeta, False, False, 0)
                
        self.MetaGroup = self.insertAboveMeta.get_group()

        button = Gtk.Button(label="Insert meta elements")
        button.set_margin_bottom(8)
        button.connect("clicked", self._insertMeta)
        box.pack_start(button, False, True, 0)                
        
        return box
        
           
    def cssUrlPage(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_homogeneous(False)
    
    
		## CSS URLs
        label = Gtk.Label()
        label.set_markup("<b>CSS URLs</b>")
        label.set_halign(Gtk.Align.START)  
        box.pack_start(label, False, True, 0)

        label = Gtk.Label()
        label.set_markup("insert:\n<i>(full path with extension, replace can be empty for delete)</i>")
        label.set_halign(Gtk.Align.START)  
        box.pack_start(label, False, True, 0)
                
        self.cssPath = Gtk.Entry()
        box.pack_start(self.cssPath, False, True, 0)


        self.insertAboveCSS = Gtk.RadioButton.new_with_label(None, "Insert above existing CSS")
        box.pack_start(self.insertAboveCSS, False, False, 0)

        self.insertBelowCSS = Gtk.RadioButton.new_from_widget(self.insertAboveCSS)
        self.insertBelowCSS.set_label("Insert below existing CSS")
        box.pack_start(self.insertBelowCSS, False, False, 0)        

        self.replaceAllCSS = Gtk.RadioButton.new_from_widget(self.insertAboveCSS)
        self.replaceAllCSS.set_label("Replace all existing CSS")
        box.pack_start(self.replaceAllCSS, False, False, 0)        

        self.replaceMatchCSS = Gtk.RadioButton.new_from_widget(self.insertAboveCSS)
        self.replaceMatchCSS.set_label("Replace this link basename (no extension):")
        box.pack_start(self.replaceMatchCSS, False, False, 0)        

        self.matchCSS = Gtk.Entry()
        self.matchCSS.set_margin_bottom(4)
        box.pack_start(self.matchCSS, False, True, 0)
                
        self.CSSGroup = self.insertAboveCSS.get_group()

        button = Gtk.Button(label="Change CSS URLs")
        button.set_margin_bottom(8)
        button.connect("clicked", self._insertCSS)
        box.pack_start(button, False, True, 0)                
        
        return box


            
    def jsUrlPage(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_homogeneous(False)
                
        ## JS URLs
        label = Gtk.Label()
        label.set_markup("<b>JS URLs</b>")
        label.set_halign(Gtk.Align.START)
        box.pack_start(label, False, True, 0)

        label = Gtk.Label()
        label.set_markup("insert:\n<i>(full path with extension, replace can be empty for delete)</i>")
        label.set_halign(Gtk.Align.START)  
        box.pack_start(label, False, True, 0)
                
        self.jsPath = Gtk.Entry()
        self.jsPath.set_margin_bottom(4)
        box.pack_start(self.jsPath, False, True, 0)

        self.insertAboveJS = Gtk.RadioButton.new_with_label_from_widget(None, "Insert above existing JS")
        box.pack_start(self.insertAboveJS, False, False, 0)

		
        self.insertBelowJS = Gtk.RadioButton.new_from_widget(self.insertAboveJS)
        self.insertBelowJS.set_label("Insert below existing JS")
        box.pack_start(self.insertBelowJS, False, True, 0)
        
        self.replaceAllJS = Gtk.RadioButton.new_from_widget(self.insertAboveJS)
        self.replaceAllJS.set_label("Replace all existing JS")
        box.pack_start(self.replaceAllJS, False, False, 0)
                
        self.replaceMatchJS = Gtk.RadioButton.new_from_widget(self.insertAboveJS)
        self.replaceMatchJS.set_label("Replace this link basename(no extension):")
        box.pack_start(self.replaceMatchJS, False, False, 0)  
        
        self.matchJS = Gtk.Entry()
        self.matchJS.set_margin_bottom(4)
        box.pack_start(self.matchJS, False, True, 0)
                      
        self.JSGroup = self.insertAboveJS.get_group()
        
        button = Gtk.Button(label="Change JS URLs")
        button.set_margin_bottom(8)
        button.connect("clicked", self._insertJS)
        box.pack_start(button, False, True, 0)         
        
        return box

        
    def imgHrefPage(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_homogeneous(False)
        
        
         ## Image URLs
        label = Gtk.Label()
        label.set_markup ("<b>Image URL roots</b>")
        label.set_halign(Gtk.Align.START)  
        box.pack_start(label, False, True, 0)

        label = Gtk.Label()
        label.set_markup ("Replace exisitng with:")
        label.set_halign(Gtk.Align.START)  
        box.pack_start(label, False, True, 0)

        
        self.imgPath = Gtk.Entry()
        self.imgPath.set_margin_bottom(4)
        box.pack_start(self.imgPath, False, True, 0)

        #self.overwriteImg = Gtk.CheckButton.new_with_label("Overwrite existing")
        #box.pack_start(self.overwriteImg, False, False, 0)
        
        button = Gtk.Button(label="Update Image URL roots")
        button.set_margin_bottom(8)
        button.connect("clicked", self._updateImgHref)
        box.pack_start(button, False, True, 0)         
        
        return box                
        
        
        
    def __init__(self):
        Gtk.Window.__init__(self, title="GSitebuilder")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.set_homogeneous(False)
        self.add(box)

        self.notebook = Gtk.Notebook()
        box.pack_start(self.notebook, True, True, 0)

        page = self.targetPage()
        page.set_border_width(10)
        self.notebook.append_page(page, Gtk.Label('Target'))

        page = self.headersPage()
        page.set_border_width(10)
        self.notebook.append_page(page, Gtk.Label('Page Headers'))

        page = self.indexesPage()
        page.set_border_width(10)
        self.notebook.append_page(page, Gtk.Label('Indexes'))                
        
        page = self.metaPage()
        page.set_border_width(10)
        self.notebook.append_page(page, Gtk.Label('Meta elems'))
        
        page = self.cssUrlPage()
        page.set_border_width(10)
        self.notebook.append_page(page, Gtk.Label('CSS URLs'))

        page = self.jsUrlPage()
        page.set_border_width(10)
        self.notebook.append_page(page, Gtk.Label('JS URLs'))
        
        page = self.imgHrefPage()
        page.set_border_width(10)
        self.notebook.append_page(page, Gtk.Label('Image URLs'))        
        
        self.notebook.connect("switch-page", self._notebookSwitched)
        
        ## Statusbar
        separator = Gtk.Separator()
        box.pack_start(separator, False, True, 4)
        
        statusbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        statusbox.set_margin_bottom(4)
        statusbox.set_homogeneous(False)
        box.pack_start(statusbox, False, True, 0)

        self.spinner = Gtk.Spinner()
        self.spinner.set_margin_left(4)
        statusbox.pack_start(self.spinner, False, True, 0)
        
        self.statusbar = Gtk.Label()
        self.statusbar.set_margin_left(4)
        #self.statusbar.set_margin_bottom(4)
        statusbox.pack_start(self.statusbar, False, True, 0)
        



def end(widget, event):
    print('end...')
    widget.saveSettings()
    Gtk.main_quit()
        
# settings for last used files.
gsettings = Gio.Settings.new(GSCHEMA)

win = MyWindow()
win.connect("delete-event", end)
win.show_all()

# rset gui
#win.spinnerStart()
#win.spinner.stop()


# populate
win.loadSettings()
    
Gtk.main()
