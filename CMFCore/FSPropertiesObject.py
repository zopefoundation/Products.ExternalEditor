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
import Acquisition
from AccessControl import getSecurityManager
from OFS.SimpleItem import Item
from OFS.Folder import Folder
from OFS.PropertyManager import PropertyManager
from DirectoryView import registerFileExtension, registerMetaType, expandpath
from string import split, join, strip
from os import path, stat
from DateTime import DateTime
from ZPublisher.Converters import get_converter
from AccessControl import ClassSecurityInfo
from CMFCorePermissions import ViewManagementScreens
import CMFCorePermissions

class FSPropertiesObject (Acquisition.Implicit, Item, PropertyManager):
    """FSPropertiesObjects simply hold properties."""

    meta_type = 'Filesystem Properties Object'
    title = ''

    manage_options = ({'label':'Customize', 'action':'manage_main'},)

    
    security = ClassSecurityInfo()

    _file_mod_time = 0

    def __init__(self, id, filepath, fullname=None, properties=None):
        self.id = id
        self._filepath = filepath
        self._readFile()

    security.declareProtected(ViewManagementScreens, 'manage_main')
    manage_main = HTMLFile('dtml/custprops', globals())

    # Make all mutators private.
    security.declarePrivate('manage_addProperty',
                            'manage_editProperties',
                            'manage_delProperties',
                            'manage_changeProperties',
                            'manage_propertiesForm',
                            'manage_propertyTypeForm',
                            'manage_changePropertyTypes',)
                               
    security.declareProtected(ViewManagementScreens, 'manage_doCustomize')
    def manage_doCustomize(self, folder_path, RESPONSE=None):
        '''
        Makes a Folder with the same properties.
        '''
        custFolder = self.getCustomizableObject()
        fpath = tuple(split(folder_path, '/'))
        folder = self.restrictedTraverse(fpath)
        id = self.getId()
        obj = Folder(id)
        map = []
        for p in self._properties:
            # This should be secure since the properties come
            # from the filesystem.
            setattr(obj, p['id'], getattr(self, p['id']))
            map.append({'id': p['id'],
                        'type': p['type'],
                        'mode': 'wd',})
        obj._properties = tuple(map)
        obj.id = id
        folder._verifyObjectPaste(obj, validate_src=0)
        folder._setObject(id, obj)
        if RESPONSE is not None:
            RESPONSE.redirect('%s/%s/manage_propertiesForm' % (
                folder.absolute_url(), id))

    security.declareProtected(ViewManagementScreens, 'getObjectFSPath')
    def getObjectFSPath(self):
        '''
        '''
        self._updateFromFS()
        return self._filepath

    def _readFile(self):
        fp = expandpath(self._filepath)
        file = open(fp, 'rb')
        try: lines = file.readlines()
        finally: file.close()
        map = []
        for line in lines:
            propname, proptv = split( line, ':' )
            #XXX multi-line properties?
            proptype, propvstr = split( proptv, '=' )
            propname = strip(propname)
            proptv = strip(proptv)
            propvstr = strip(propvstr)
            converter = get_converter( proptype, lambda x: x )
            propvalue = converter( strip( propvstr ) )
            # Should be safe since we're loading from
            # the filesystem.
            setattr(self, propname, propvalue)
            map.append({'id':propname,
                        'type':proptype,
                        'mode':'',
                        'default_value':propvalue,
                        })
        self._properties = tuple(map)            

    def _updateFromFS(self):
        if Globals.DevelopmentMode:
            fp = expandpath(self._filepath)
            try:    mtime=stat(fp)[8]
            except: mtime=0
            if mtime != self._file_mod_time:
                self._file_mod_time = mtime
                self._readFile()

    if Globals.DevelopmentMode:
        # Provide an opportunity to update the properties.
        def __of__(self, parent):
            self = Acquisition.ImplicitAcquisitionWrapper(self, parent)
            self._updateFromFS()
            return self

    def getId(self):
        return self.id

##    def propertyMap(self):
##        """Return a tuple of mappings, giving meta-data for properties."""
##        # Don't allow changes.
##        return map(lambda dict: dict.copy(), self._properties)

    


Globals.InitializeClass(FSPropertiesObject)

registerFileExtension('props', FSPropertiesObject)
registerMetaType('Properties Object', FSPropertiesObject)
