##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
##############################################################################
"""Customizable page templates that come from the filesystem."""
__version__='$Revision$'[11:-2]

import Globals
from Globals import DTMLFile
import Acquisition
from AccessControl import getSecurityManager
from OFS.SimpleItem import Item
from Products.CMFCore.DirectoryView import registerFileExtension, \
     registerMetaType, expandpath
from string import split
from os import stat
from AccessControl import ClassSecurityInfo
from Products.CMFCore.CMFCorePermissions import ViewManagementScreens
from DateTime import DateTime

from Products.PageTemplates.PageTemplate import PageTemplate
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Shared.DC.Scripts.Script import Script
from Shared.DC.Scripts.Signature import FuncCode


class FSPageTemplate(Script, PageTemplate):
    "Wrapper for Page Template"
     
    meta_type = 'Filesystem Page Template'
    title = ''
    _file_mod_time = 0
    expand = 0

    func_defaults = None
    func_code = FuncCode((), 0)

    _default_bindings = {'name_subpath': 'traverse_subpath'}

    manage_options=(
        (
            {'label':'Customize', 'action':'manage_main'},
            {'label':'Test', 'action':'ZScriptHTML_tryForm'},
            )
        )

    security = ClassSecurityInfo()

    # Declare security for unprotected PageTemplate methods.
    security.declarePrivate('pt_edit', 'write')

    def __init__(self, id, filepath, fullname=None, properties=None):
        self.id = id
        if properties:
            # Since props come from the filesystem, this should be
            # safe.
            self.__dict__.update(properties)
        self._filepath = filepath
        self.ZBindings_edit(self._default_bindings)
        self._updateFromFS(1)

    security.declareProtected(ViewManagementScreens, 'manage_doCustomize')
    def manage_doCustomize(self, folder_path, body=None, RESPONSE=None):
        '''
        Makes a ZopePageTemplate with the same code.
        '''
        custFolder = self.getCustomizableObject()
        fpath = tuple(split(folder_path, '/'))
        folder = self.restrictedTraverse(fpath)
        if body is None:
            body = self.read()
        id = self.getId()
        obj = ZopePageTemplate(id, self._text, self.content_type)
        folder._verifyObjectPaste(obj, validate_src=0)
        folder._setObject(id, obj)
        obj = folder._getOb(id)
        obj.write(body)
        if RESPONSE is not None:
            RESPONSE.redirect('%s/%s/manage_main' % (
                folder.absolute_url(), id))

    security.declareProtected(ViewManagementScreens, 'getMethodFSPath')
    def getMethodFSPath(self):
        return self._filepath

    def _updateFromFS(self, force=0):
        if force or Globals.DevelopmentMode:
            fp = expandpath(self._filepath)
            try:    mtime=stat(fp)[8]
            except: mtime=0
            if force or mtime != self._file_mod_time:
                self._file_mod_time = mtime
                fp = expandpath(self._filepath)
                file = open(fp, 'rb')
                try: data = file.read()
                finally: file.close()
                self.write(data)

    def getId(self):
        self._updateFromFS()
        return self.id

    security.declareProtected(ViewManagementScreens, 'getModTime')
    def getModTime(self):
        '''
        '''
        return DateTime(self._file_mod_time)

    ### The following is mainly taken from ZopePageTemplate.py ###

    security.declareObjectProtected('View')
    security.declareProtected('View', '__call__')

    security.declareProtected(ViewManagementScreens, 'manage_main')
    manage_main = DTMLFile('dtml/custpt', globals())

##    pt_diagnostic = DTMLFile('dtml/ptDiagnostic', globals())

    def ZScriptHTML_tryParams(self):
        """Parameters to test the script with."""
        return []

    def pt_getContext(self):
        self._updateFromFS()
        root = self.getPhysicalRoot()
        c = {'template': self,
             'here': self._getContext(),
             'container': self._getContainer(),
             'nothing': None,
             'options': {},
             'root': root,
             'request': getattr(root, 'REQUEST', None),
             }
        return c

    def _exec(self, bound_names, args, kw):
        """Call a Page Template"""
        if not kw.has_key('args'):
            kw['args'] = args
        bound_names['options'] = kw

        try:
            self.REQUEST.RESPONSE.setHeader('content-type',
                                            self.content_type)
        except AttributeError: pass

        # Execute the template in a new security context.
        security=getSecurityManager()
        security.addContext(self)
        try:
            return self.pt_render(extra_context=bound_names)
        finally:
            security.removeContext(self)

    def manage_FTPget(self):
        "Get source for FTP download"
        self.REQUEST.RESPONSE.setHeader('Content-Type', self.content_type)
        return self.read()

    def get_size(self):
        return len(self.read())
    getSize = get_size

    def PrincipiaSearchSource(self):
        "Support for searching - the document's contents are searched."
        return self.read()

    def document_src(self, REQUEST=None, RESPONSE=None):
        """Return expanded document source."""

        if RESPONSE is not None:
            RESPONSE.setHeader('Content-Type', self.content_type)
        return self.read()


class Src(Acquisition.Explicit):
    " "

    document_src = Acquisition.Acquired
    index_html = None
    
    def __call__(self, REQUEST, RESPONSE):
        " "
        return self.document_src(REQUEST, RESPONSE)

d = FSPageTemplate.__dict__
d['source.xml'] = d['source.html'] = Src()


Globals.InitializeClass(FSPageTemplate)

registerFileExtension('pt', FSPageTemplate)
registerMetaType('Page Template', FSPageTemplate)

