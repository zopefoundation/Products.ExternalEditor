import time
import pkg_resources
import os

import Globals
from Globals import ImageFile
from Globals import DTMLFile
from Globals import package_home
from OFS.content_types import guess_content_type
from App.Common import rfc1123_date
from App.special_dtml import defaultBindings


## from Products.PageTemplates.PageTemplateFile import PageTemplateFile
## from Products.PageTemplates.PageTemplateFile import XML_PREFIX_MAX_LENGTH
## from zLOG import LOG
## from zLOG import ERROR
## from Globals import DevelopmentMode

## class PageTemplateResource(PageTemplateFile):
##     def _cook_check(self):
##         if self._v_last_read and not DevelopmentMode:
##             return
##         print self.filename
##         __traceback_info__ = self.filename
##         try:
##             mtime = os.path.getmtime(self.filename)
##         except OSError:
##             mtime = 0
##         if self._v_program is not None and mtime == self._v_last_read:
##             return
##         f = open(self.filename, "rb")
##         try:
##             text = f.read(XML_PREFIX_MAX_LENGTH)
##         except:
##             f.close()
##             raise
##         t = sniff_type(text)
##         if t != "text/xml":
##             # For HTML, we really want the file read in text mode:
##             f.close()
##             f = open(self.filename)
##             text = ''
##         text += f.read()
##         f.close()
##         self.pt_edit(text, t)
##         self._cook()
##         if self._v_errors:
##             LOG('PageTemplateFile', ERROR, 'Error in template',
##                 '\n'.join(self._v_errors))
##             return
##         self._v_last_read = mtime
        
class ImageResource(ImageFile):
    def __init__(self,path,_prefix=None):
        name = _prefix['__name__']
        resource = pkg_resources.resource_stream(name, path)

        data = resource.read()
        content_type, enc=guess_content_type(path, data)
        if content_type:
            self.content_type=content_type
        else:
            self.content_type='image/%s' % path[path.rfind('.')+1:]
        self.__name__=path[path.rfind('/')+1:]
        self.lmt=time.time()
        self.lmh=rfc1123_date(self.lmt)

class DTMLResource(DTMLFile):
    def __init__(self,name,_prefix=None, **kw):
        #DTMLFile.__init__(self, name, _prefix, **kw)
        self.ZBindings_edit(defaultBindings)
        self._setFuncSignature()

        #ClassicHTMLFile.__init__(self, name, _prefix, **kw)
        packagename = _prefix['__name__']
        if not kw.has_key('__name__'):
            kw['__name__'] = os.path.split(name)[-1]

        #FileMixin.__init__(self, *args, **kw)
        filename = name + '.dtml'
        self.raw = (packagename, filename)
        self.initvars(None, kw)
        self.setName(kw['__name__'] or filename)

    def read_raw(self):
        if self.edited_source:
            data = self.edited_source
        elif not self.raw:
            data = ''
        elif pkg_resources.resource_exists(*self.raw):
            data = pkg_resources.resource_stream(*self.raw).read()
        return data
        
    def _cook_check(self):
        if Globals.DevelopmentMode:
            __traceback_info__=str(self.raw)
            mtime = time.time()
            if mtime != self._v_last_read:
                self.cook()
                self._v_last_read=mtime
        elif not hasattr(self,'_v_cooked'):
            try: changed = self.__changed__()
            except: changed=1
            self.cook()
            if not changed:
                self.__changed__(0)
