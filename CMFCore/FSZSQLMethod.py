# Copyright (c) 2001 New Information Paradigms Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.
#
# $Id$

"""(not yet)Customizable ZSQL methods that come from the filesystem."""
__version__='$Revision$'[11:-2]

import Globals
from AccessControl import ClassSecurityInfo
from zLOG import LOG,ERROR

from Products.CMFCore.CMFCorePermissions import View, ViewManagementScreens
from Products.CMFCore.DirectoryView import registerFileExtension, registerMetaType, expandpath
from Products.CMFCore.FSObject import FSObject

from Products.ZSQLMethods.SQL import SQL

from utils import _dtmldir

import Acquisition

class FSZSQLMethod(SQL, FSObject):
    """FSZSQLMethods act like Z SQL Methods but are not directly
    modifiable from the management interface."""

    meta_type = 'Filesystem Z SQL Method'

    manage_options=(
        (
            {'label':'Customize', 'action':'manage_customise'},
            {'label':'Test', 'action':'manage_testForm',
             'help':('ZSQLMethods','Z-SQL-Method_Test.stx')},
            )
        )

    # Use declarative security
    security = ClassSecurityInfo()
    
    security.declareObjectProtected(View)
    
    # Make mutators private
    security.declarePrivate('manage_main','manage_edit','manage_advanced','manage_advancedForm')
    manage=None
    
    security.declareProtected(ViewManagementScreens, 'manage_customise')
    manage_customise = Globals.DTMLFile('custzsql', _dtmldir)

    def __init__(self, id, filepath, fullname=None, properties=None):
        FSObject.__init__(self, id, filepath, fullname, properties)

    def _createZODBClone(self):
        """Create a ZODB (editable) equivalent of this object."""
        # I guess it's bad to 'reach inside' ourselves like this,
        # but Z SQL Methods don't have accessor methdods ;-)
        s = SQL(self.id,
                self.title,
                self.connection_id,
                self.arguments_src,
                self.src)
        s.manage_advanced(self.max_rows_,
                          self.max_cache_,
                          self.cache_time_,
                          '',
                          '')
        return s

    def _readFile(self, reparse):
        fp = expandpath(self._filepath)
        file = open(fp, 'rb')
        try:
            data = file.read()
        finally: file.close()

        # parse parameters
        parameters={}
        start = data.find('<dtml-comment>')
        end   = data.find('</dtml-comment>')
        if start==-1 or end==-1 or start>end:
            raise ValueError,'Could not find parameter block'
        block = data[start+14:end]

        for line in block.split('\n'):
            pair = line.split(':',1)
            if len(pair)!=2:
                continue
            parameters[pair[0].strip().lower()]=pair[1].strip()

        # check for required an optional parameters
        try:            
            title =         parameters.get('title','')
            connection_id = parameters.get('connection id',parameters['connection_id'])
            arguments =     parameters.get('arguments','')
            max_rows =      parameters.get('max_rows',1000)
            max_cache =     parameters.get('max_cache',100)
            cache_time =    parameters.get('cache_time',0)            
        except KeyError,e:
            raise ValueError,"The '%s' parameter is required but was not supplied" % e
        
        self.manage_edit(title,
                         connection_id,
                         arguments,
                         template=data)

        self.manage_advanced(max_rows,
                             max_cache,
                             cache_time,
                             '', # don't really see any point in allowing
                             '') # brain specification...

        # do we need to do anything on reparse?


    if Globals.DevelopmentMode:
        # Provide an opportunity to update the properties.
        def __of__(self, parent):
            try:
                self = Acquisition.ImplicitAcquisitionWrapper(self, parent)
                self._updateFromFS()
                return self
            except:
                from zLOG import LOG, ERROR
                import sys
                LOG('FS Z SQL Method',
                    ERROR,
                    'Error during __of__',
                    error=sys.exc_info())
                raise

Globals.InitializeClass(FSZSQLMethod)

registerFileExtension('zsql', FSZSQLMethod)
registerMetaType('Z SQL Method', FSZSQLMethod)
