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
import re

import Globals, Acquisition
from DateTime import DateTime
from DocumentTemplate.DT_Util import html_quote
from Acquisition import aq_parent
from AccessControl import getSecurityManager, ClassSecurityInfo
from Shared.DC.Scripts.Script import Script
from Products.PageTemplates.PageTemplate import PageTemplate
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate, Src

from DirectoryView import registerFileExtension, registerMetaType, expandpath
from CMFCorePermissions import ViewManagementScreens, View, FTPAccess
from FSObject import FSObject
from utils import getToolByName

xml_detect_re = re.compile('^\s*<\?xml\s+')

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
        obj.expand = 0
        obj.write(self.read())
        return obj

    def ZCacheable_isCachingEnabled(self):
        return 0

    def _readFile(self, reparse):
        fp = expandpath(self._filepath)
        file = open(fp, 'rb')
        try: 
            data = file.read()
        finally: 
            file.close()
        if reparse:
            if xml_detect_re.match(data):
                # Smells like xml
                self.content_type = 'text/xml'
            else:
                try:
                    del self.content_type
                except (AttributeError, KeyError):
                    pass
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

    def pt_render(self, source=0, extra_context={}):
        self._updateFromFS()  # Make sure the template has been loaded.
        try:
            if not source: # Hook up to caching policy.

                REQUEST = getattr( self, 'REQUEST', None )

                if REQUEST:

                    content = aq_parent( self )

                    mgr = getToolByName( content
                                       , 'caching_policy_manager'
                                       , None
                                       )

                    if mgr:
                        view_name = self.getId()
                        RESPONSE = REQUEST[ 'RESPONSE' ]
                        headers = mgr.getHTTPCachingHeaders( content
                                                           , view_name
                                                           , extra_context
                                                           )
                        for key, value in headers:
                            RESPONSE.setHeader( key, value )

            return FSPageTemplate.inheritedAttribute('pt_render')( self,
                    source, extra_context )

        except RuntimeError:
            if Globals.DevelopmentMode:
                err = FSPageTemplate.inheritedAttribute( 'pt_errors' )( self )
                err_type = err[0]
                err_msg = '<pre>%s</pre>' % replace( err[1], "\'", "'" )
                msg = 'FS Page Template %s has errors: %s.<br>%s' % (
                    self.id, err_type, html_quote(err_msg) )
                raise RuntimeError, msg
            else:
                raise
                
    def _exec(self, bound_names, args, kw):
        """Call a FSPageTemplate"""
        if not kw.has_key('args'):
            kw['args'] = args
        bound_names['options'] = kw

        try:
            response = self.REQUEST.RESPONSE
        except AttributeError:
            response = None

        security=getSecurityManager()
        bound_names['user'] = security.getUser()

        # Retrieve the value from the cache.
        keyset = None
        if self.ZCacheable_isCachingEnabled():
            # Prepare a cache key.
            keyset = {'here': self._getContext(),
                      'bound_names': bound_names}
            result = self.ZCacheable_get(keywords=keyset)
            if result is not None:
                # Got a cached value.
                if response is not None:
                    response.setHeader('content-type',self.content_type)
                return result
                
        # Execute the template in a new security context.
        security.addContext(self)
        try:
            result = self.pt_render(extra_context=bound_names)
            if response is not None:
                # content_type may not have been cooked until now
                response.setHeader('content-type',self.content_type)
            if keyset is not None:
                # Store the result in the cache.
                self.ZCacheable_set(result, keywords=keyset)
            return result
        finally:
            security.removeContext(self)
                        
    # Copy over more methods
    security.declareProtected(FTPAccess, 'manage_FTPget')
    security.declareProtected(View, 'get_size')
    security.declareProtected(ViewManagementScreens, 'PrincipiaSearchSource',
        'document_src')

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

