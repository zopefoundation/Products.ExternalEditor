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
""" Basic portal catalog.

$Id$
"""

from Products.ZCatalog.ZCatalog import ZCatalog
from Globals import InitializeClass, package_home, DTMLFile
from DateTime import DateTime
from AccessControl.PermissionRole import rolesForPermissionOn
from AccessControl import ClassSecurityInfo

from utils import _checkPermission
from utils import _dtmldir
from utils import _getAuthenticatedUser
from utils import _mergedLocalRoles
from utils import UniqueObject
from ActionProviderBase import ActionProviderBase
from ActionInformation import ActionInformation
from Expression import Expression
from CMFCorePermissions import AccessInactivePortalContent
from CMFCorePermissions import ManagePortal
from CMFCorePermissions import View
from Acquisition import aq_base

from interfaces.portal_catalog \
        import IndexableObjectWrapper as IIndexableObjectWrapper
from interfaces.portal_catalog import portal_catalog as ICatalogTool


class IndexableObjectWrapper:

    __implements__ = IIndexableObjectWrapper

    def __init__(self, vars, ob):
        self.__vars = vars
        self.__ob = ob

    def __getattr__(self, name):
        vars = self.__vars
        if vars.has_key(name):
            return vars[name]
        return getattr(self.__ob, name)

    def allowedRolesAndUsers(self):
        """
        Return a list of roles and users with View permission.
        Used by PortalCatalog to filter out items you're not allowed to see.
        """
        ob = self.__ob
        allowed = {}
        for r in rolesForPermissionOn(View, ob):
            allowed[r] = 1
        localroles = _mergedLocalRoles(ob)
        for user, roles in localroles.items():
            for role in roles:
                if allowed.has_key(role):
                    allowed['user:' + user] = 1
        if allowed.has_key('Owner'):
            del allowed['Owner']
        return list(allowed.keys())

class CatalogTool (UniqueObject, ZCatalog, ActionProviderBase):
    """ This is a ZCatalog that filters catalog queries.
    """

    __implements__ = (ICatalogTool, ActionProviderBase.__implements__)

    id = 'portal_catalog'
    meta_type = 'CMF Catalog'
    _actions = ()

    security = ClassSecurityInfo()

    manage_options = ( ZCatalog.manage_options +
                      ActionProviderBase.manage_options +
                      ({ 'label' : 'Overview', 'action' : 'manage_overview' }
                     , 
                     ))

    def __init__(self):
        ZCatalog.__init__(self, self.getId())
        
        if not hasattr(self, 'Vocabulary'):
            # As of 2.6, the Catalog no longer adds a vocabulary in itself
            from Products.PluginIndexes.TextIndex.Vocabulary import Vocabulary
            vocabulary = Vocabulary('Vocabulary', 'Vocabulary', globbing=1)
            self._setObject('Vocabulary', vocabulary)
            
        self._initIndexes()

    #
    #   Subclass extension interface
    #
    security.declarePublic( 'enumerateIndexes' ) # Subclass can call
    def enumerateIndexes( self ):
        #   Return a list of ( index_name, type ) pairs for the initial
        #   index set.
        #   id is depricated and may go away, use getId!
        return ( ('Title', 'TextIndex')
               , ('Subject', 'KeywordIndex')
               , ('Description', 'TextIndex')
               , ('Creator', 'FieldIndex')
               , ('SearchableText', 'TextIndex')
               , ('Date', 'FieldIndex')
               , ('Type', 'FieldIndex')
               , ('created', 'FieldIndex')
               , ('effective', 'FieldIndex')
               , ('expires', 'FieldIndex')
               , ('modified', 'FieldIndex')
               , ('allowedRolesAndUsers', 'KeywordIndex')
               , ('review_state', 'FieldIndex')
               , ('in_reply_to', 'FieldIndex')
               , ('meta_type', 'FieldIndex')
               , ('id', 'FieldIndex')
               , ('getId', 'FieldIndex')
               , ('path', 'PathIndex')
               , ('portal_type', 'FieldIndex')
               )
    
    security.declarePublic( 'enumerateColumns' )
    def enumerateColumns( self ):
        #   Return a sequence of schema names to be cached.
        #   id is depricated and may go away, use getId!
        return ( 'Subject'
               , 'Title'
               , 'Description'
               , 'Type'
               , 'review_state'
               , 'Creator'
               , 'Date'
               , 'getIcon'
               , 'created'
               , 'effective'
               , 'expires'
               , 'modified'
               , 'CreationDate'
               , 'EffectiveDate'
               , 'ExpiresDate'
               , 'ModificationDate'
               , 'id'
               , 'getId'
               , 'portal_type'
               )

    def _initIndexes(self):

        # Content indexes
        self._catalog.indexes.clear()
        for index_name, index_type in self.enumerateIndexes():
            self.addIndex(index_name, index_type)

        # Cached metadata
        self._catalog.names = ()
        self._catalog.schema.clear()
        for column_name in self.enumerateColumns():
            self.addColumn(column_name)

    #
    #   ZMI methods
    #
    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = DTMLFile( 'explainCatalogTool', _dtmldir )

    #
    #   'portal_catalog' interface methods
    #

    def _listAllowedRolesAndUsers( self, user ):
        result = list( user.getRoles() )
        result.append( 'Anonymous' )
        result.append( 'user:%s' % user.getId() )
        return result

    # searchResults has inherited security assertions.
    def searchResults(self, REQUEST=None, **kw):
        """
            Calls ZCatalog.searchResults with extra arguments that
            limit the results to what the user is allowed to see.
        """
        user = _getAuthenticatedUser(self)
        kw[ 'allowedRolesAndUsers' ] = self._listAllowedRolesAndUsers( user )

        if not _checkPermission( AccessInactivePortalContent, self ):
            now = DateTime()
            kw['effective'] = {'query': now, 'range': 'max'}
            kw['expires'] = {'query': now, 'range': 'min'}

        return ZCatalog.searchResults(self, REQUEST, **kw)

    __call__ = searchResults

    def __url(self, ob):
        return '/'.join( ob.getPhysicalPath() )

    manage_catalogFind = DTMLFile( 'catalogFind', _dtmldir )

    def catalog_object(self, object, uid, idxs=[]):
        # Wraps the object with workflow and accessibility
        # information just before cataloging.
        wf = getattr(self, 'portal_workflow', None)
        if wf is not None:
            vars = wf.getCatalogVariablesFor(object)
        else:
            vars = {}
        w = IndexableObjectWrapper(vars, object)
        ZCatalog.catalog_object(self, w, uid, idxs)

    security.declarePrivate('indexObject')
    def indexObject(self, object):
        '''Add to catalog.
        '''
        url = self.__url(object)
        self.catalog_object(object, url)

    security.declarePrivate('unindexObject')
    def unindexObject(self, object):
        '''Remove from catalog.
        '''
        url = self.__url(object)
        self.uncatalog_object(url)

    security.declarePrivate('reindexObject')
    def reindexObject(self, object, idxs=[]):
        '''Update catalog after object data has changed.
        The optional idxs argument is a list of specific indexes
        to update (all of them by default).
        '''
        url = self.__url(object)
        if idxs != []:
            # Filter out invalid indexes.
            valid_indexes = self._catalog.indexes.keys()
            idxs = [i for i in idxs if i in valid_indexes]
        self.catalog_object(object, url, idxs=idxs)

InitializeClass(CatalogTool)
