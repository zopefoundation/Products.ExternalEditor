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
##############################################################################
"""Customizable properties that come from the filesystem."""
__version__='$Revision$'[11:-2]

from string import split, strip

import Globals
import Acquisition
from OFS.Folder import Folder
from OFS.PropertyManager import PropertyManager
from ZPublisher.Converters import get_converter
from AccessControl import ClassSecurityInfo

from utils import _dtmldir
from DirectoryView import registerFileExtension, registerMetaType, expandpath
from CMFCorePermissions import ViewManagementScreens
from FSObject import FSObject

class FSPropertiesObject (FSObject, PropertyManager):
    """FSPropertiesObjects simply hold properties."""

    meta_type = 'Filesystem Properties Object'

    manage_options = ({'label':'Customize', 'action':'manage_main'},)
    
    security = ClassSecurityInfo()

    security.declareProtected(ViewManagementScreens, 'manage_main')
    manage_main = Globals.DTMLFile('custprops', _dtmldir)

    # Declare all (inherited) mutating methods private.
    security.declarePrivate('manage_addProperty',
                            'manage_editProperties',
                            'manage_delProperties',
                            'manage_changeProperties',
                            'manage_propertiesForm',
                            'manage_propertyTypeForm',
                            'manage_changePropertyTypes',)
                               
    security.declareProtected(ViewManagementScreens, 'manage_doCustomize')
    def manage_doCustomize(self, folder_path, RESPONSE=None):
        """Makes a ZODB Based clone with the same data.

        Calls _createZODBClone for the actual work.
        """
        # Overridden here to provide a different redirect target.

        FSObject.manage_doCustomize(self, folder_path, RESPONSE)

        if RESPONSE is not None:
            fpath = tuple(split(folder_path, '/'))
            folder = self.restrictedTraverse(fpath)
            RESPONSE.redirect('%s/%s/manage_propertiesForm' % (
                folder.absolute_url(), self.getId()))
    
    def _createZODBClone(self):
        """Create a ZODB (editable) equivalent of this object."""
        # Create a Folder to hold the properties.
        obj = Folder()
        obj.id = self.getId()
        map = []
        for p in self._properties:
            # This should be secure since the properties come
            # from the filesystem.
            setattr(obj, p['id'], getattr(self, p['id']))
            map.append({'id': p['id'],
                        'type': p['type'],
                        'mode': 'wd',})
        obj._properties = tuple(map)

        return obj

    def _readFile(self, reparse):
        """Read the data from the filesystem.
        
        Read the file (indicated by exandpath(self._filepath), and parse the
        data if necessary.
        """

        fp = expandpath(self._filepath)

        file = open(fp, 'rb')
        try:
            lines = file.readlines()
        finally:
            file.close()

        map = []
        lino=0

        for line in lines:

            lino = lino + 1
            line = strip( line )

            if not line or line[0] == '#':
                continue

            try:
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
            except:
                raise ValueError, ( 'Error processing line %s of %s:\n%s'
                                  % (lino,fp,line) )
        self._properties = tuple(map)            

    if Globals.DevelopmentMode:
        # Provide an opportunity to update the properties.
        def __of__(self, parent):
            self = Acquisition.ImplicitAcquisitionWrapper(self, parent)
            self._updateFromFS()
            return self


Globals.InitializeClass(FSPropertiesObject)

registerFileExtension('props', FSPropertiesObject)
registerMetaType('Properties Object', FSPropertiesObject)
