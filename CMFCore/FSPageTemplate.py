##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##########################################################################
"""Customizable page templates that come from the filesystem."""
__version__='$Revision$'[11:-2]

from string import split, replace
from os import stat

import Globals, Acquisition
from DateTime import DateTime
from DocumentTemplate.DT_Util import html_quote
from AccessControl import getSecurityManager, ClassSecurityInfo
from Shared.DC.Scripts.Script import Script
from Products.PageTemplates.PageTemplate import PageTemplate
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate, Src

from DirectoryView import registerFileExtension, registerMetaType, expandpath
from CMFCorePermissions import ViewManagementScreens, View, FTPAccess
from FSObject import FSObject

class FSPageTemplate(FSObject, Script, PageTemplate):
    "Wrapper for Page Template"
     
    meta_type = 'Filesystem Page Template'

    manage_options=(
        (
            {'label':'Customize', 'action':'manage_main'},
            {'label':'Test', 'action':'ZScriptHTML_tryForm'},
            )
        )

    security = ClassSecurityInfo()
    security.declareObjectProtected(View)

    security.declareProtected(ViewManagementScreens, 'manage_main')
    manage_main = Globals.DTMLFile('dtml/custpt', globals())

    # Declare security for unprotected PageTemplate methods.
    security.declarePrivate('pt_edit', 'write')

    def __init__(self, id, filepath, fullname=None, properties=None):
        FSObject.__init__(self, id, filepath, fullname, properties)
        self.ZBindings_edit(self._default_bindings)

    def _createZODBClone(self):
        """Create a ZODB (editable) equivalent of this object."""
        obj = ZopePageTemplate(self.getId(), self._text, self.content_type)
        obj.write(self.read())
        return obj

    def ZCacheable_isCachingEnabled(self):
        return 0

    def _readFile(self, reparse):
        fp = expandpath(self._filepath)
        file = open(fp, 'rb')
        try: data = file.read()
        finally: file.close()
        self.write(data)

    security.declarePrivate('read')
    def read(self):
        # Tie in on an opportunity to auto-update
        self._updateFromFS()
        return FSPageTemplate.inheritedAttribute('read')(self)

    ### The following is mainly taken from ZopePageTemplate.py ###

    expand = 0

    func_defaults = None
    func_code = ZopePageTemplate.func_code
    _default_bindings = ZopePageTemplate._default_bindings

    security.declareProtected(View, '__call__')

    def pt_macros(self):
        # Tie in on an opportunity to auto-reload
        self._updateFromFS()
        return FSPageTemplate.inheritedAttribute('pt_macros')(self)

    if Globals.DevelopmentMode:
        
        # Redefine pt_render if in debug mode to give a bit more info
        
        def pt_render(self, source=0, extra_context={}):
            # Tie in on an opportunity to auto-reload
            self._updateFromFS()
            try:
                return FSPageTemplate.inheritedAttribute('pt_render')( self,
                    source, extra_context )
            except RuntimeError:
                err = FSPageTemplate.inheritedAttribute( 'pt_errors' )( self )
                err_type = err[0]
                err_msg = '<pre>%s</pre>' % replace( err[1], "\'", "'" )
                msg = 'FS Page Template %s has errors: %s.<br>%s' % (
                    self.id, err_type, html_quote(err_msg) )
                raise RuntimeError, msg
            
    # Copy over more mothods
    security.declareProtected(FTPAccess, 'manage_FTPget')
    security.declareProtected(View, 'get_size')
    security.declareProtected(ViewManagementScreens, 'PrincipiaSearchSource',
        'document_src')

    _exec = ZopePageTemplate._exec
    pt_getContext = ZopePageTemplate.pt_getContext
    ZScriptHTML_tryParams = ZopePageTemplate.ZScriptHTML_tryParams
    manage_FTPget = ZopePageTemplate.manage_FTPget
    get_size = ZopePageTemplate.get_size
    getSize = get_size
    PrincipiaSearchSource = ZopePageTemplate.PrincipiaSearchSource
    document_src = ZopePageTemplate.document_src


d = FSPageTemplate.__dict__
d['source.xml'] = d['source.html'] = Src()

Globals.InitializeClass(FSPageTemplate)

registerFileExtension('pt', FSPageTemplate)
registerFileExtension('html', FSPageTemplate)
registerFileExtension('htm', FSPageTemplate)
registerMetaType('Page Template', FSPageTemplate)

