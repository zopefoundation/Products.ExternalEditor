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
"""Customizable DTML methods that come from the filesystem."""
__version__='$Revision$'[11:-2]

import Globals
from Globals import HTML, HTMLFile
from OFS.DTMLMethod import DTMLMethod, decapitate, guess_content_type
import Acquisition
from AccessControl import getSecurityManager
from OFS.SimpleItem import Item_w__name__
from DirectoryView import registerFileExtension, registerMetaType, expandpath
from string import split
from os import path, stat
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from CMFCorePermissions import View, ViewManagementScreens
import CMFCorePermissions


class FSDTMLMethod (HTML, Acquisition.Implicit, Item_w__name__):
    """FSDTMLMethods act like DTML methods but are not directly
    modifiable from the management interface."""

    meta_type = 'Filesystem DTML Method'
    title = ''

    manage_options=(
        (
            {'label':'Customize', 'action':'manage_main'},
            {'label':'View', 'action':'',
             'help':('OFSP','DTML-DocumentOrMethod_View.stx')},
            )
        )

    # Use declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(CMFCorePermissions.View)
    security.declareProtected(CMFCorePermissions.View, 'index_html',)

    file_mod_time = 0

    def __init__(self, id, filepath, fullname=None, properties=None):
        if properties:
            # Since props come from the filesystem, this should be
            # safe.
            self.__dict__.update(properties)
        self._filepath = filepath
        data = self._readFile()
        fp = expandpath(filepath)
        try: self.file_mod_time = stat(fp)[8]
        except: pass
        HTML.__init__(self, data, __name__=id)

    security.declareProtected(ViewManagementScreens, 'manage_main')
    manage_main = HTMLFile('dtml/custdtml', globals())

    security.declareProtected(ViewManagementScreens, 'manage_doCustomize')
    def manage_doCustomize(self, folder_path, data=None, RESPONSE=None):
        '''
        Makes a DTMLMethod with the same code.
        '''
        custFolder = self.getCustomizableObject()
        fpath = tuple(split(folder_path, '/'))
        folder = self.restrictedTraverse(fpath)
        if data is None:
            data = self.read()
        id = self.getId()
        obj = DTMLMethod(data, __name__=id)
        folder._verifyObjectPaste(obj, validate_src=0)
        folder._setObject(id, obj)
        if RESPONSE is not None:
            RESPONSE.redirect('%s/%s/manage_main' % (
                folder.absolute_url(), id))

    security.declareProtected(ViewManagementScreens, 'getMethodFSPath')
    def getMethodFSPath(self):
        return self._filepath

    def _readFile(self):
        fp = expandpath(self._filepath)
        file = open(fp, 'rb')
        try: data = file.read()
        finally: file.close()
        return data

    def _updateFromFS(self):
        if Globals.DevelopmentMode:
            fp = expandpath(self._filepath)
            try:    mtime=stat(fp)[8]
            except: mtime=0
            if mtime != self.file_mod_time:
                self.file_mod_time = mtime
                self.raw = self._readFile()
                self.cook()

    def __str__(self):
        self._updateFromFS()
        return self.read()

    def getId(self):
        return self.__name__

    #### The following is mainly taken from OFS/DTMLMethod.py ###
        
    index_html=None # Prevent accidental acquisition

    # Documents masquerade as functions:
    class func_code: pass
    func_code=func_code()
    func_code.co_varnames='self','REQUEST','RESPONSE'
    func_code.co_argcount=3

    default_content_type='text/html'

    def __call__(self, client=None, REQUEST={}, RESPONSE=None, **kw):
        """Render the document given a client object, REQUEST mapping,
        Response, and key word arguments."""

        self._updateFromFS()

        kw['document_id']   =self.getId()
        kw['document_title']=self.title

        security=getSecurityManager()
        security.addContext(self)
        try:
        
            if client is None:
                # Called as subtemplate, so don't need error propagation!
                r=apply(HTML.__call__, (self, client, REQUEST), kw)
                if RESPONSE is None: result = r
                else: result = decapitate(r, RESPONSE)
                return result

            r=apply(HTML.__call__, (self, client, REQUEST), kw)
            if type(r) is not type('') or RESPONSE is None:
                return r

        finally: security.removeContext(self)

        have_key=RESPONSE.headers.has_key
        if not (have_key('content-type') or have_key('Content-Type')):
            if self.__dict__.has_key('content_type'):
                c=self.content_type
            else:
                c, e=guess_content_type(self.getId(), r)
            RESPONSE.setHeader('Content-Type', c)
        result = decapitate(r, RESPONSE)
        return result

    def get_size(self):
        return len(self.raw)

    def validate(self, inst, parent, name, value, md):
        return getSecurityManager().validate(inst, parent, name, value)

    security.declareProtected(View, 'manage_FTPget')
    def manage_FTPget(self):
        "Get source for FTP download"
        return self.read()

    security.declareProtected(ViewManagementScreens, 'getModTime')
    def getModTime(self):
        '''
        '''
        return DateTime(self.file_mod_time)

Globals.InitializeClass(FSDTMLMethod)

registerFileExtension('dtml', FSDTMLMethod)
registerMetaType('DTML Method', FSDTMLMethod)
