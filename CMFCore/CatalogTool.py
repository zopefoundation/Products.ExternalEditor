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

"""Basic portal catalog.
$Id$
"""
__version__='$Revision$'[11:-2]


import os
from utils import UniqueObject, _checkPermission, _getAuthenticatedUser
from utils import getToolByName, _dtmldir
from Products.ZCatalog.ZCatalog import ZCatalog
from Globals import InitializeClass, package_home, DTMLFile
import urllib
from DateTime import DateTime
from string import join
from AccessControl.PermissionRole import rolesForPermissionOn
from AccessControl import ClassSecurityInfo
from utils import mergedLocalRoles
import os
import CMFCorePermissions
from Acquisition import aq_base


class IndexableObjectWrapper:

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
        for r in rolesForPermissionOn('View', ob):
            allowed[r] = 1
        localroles = mergedLocalRoles(ob)
        for user, roles in localroles.items():
            for role in roles:
                if allowed.has_key(role):
                    allowed['user:' + user] = 1
        if allowed.has_key('Owner'):
            del allowed['Owner']
        return list(allowed.keys())


class CatalogTool (UniqueObject, ZCatalog):
    '''This is a ZCatalog that filters catalog queries.
    '''
    id = 'portal_catalog'
    meta_type = 'CMF Catalog'
    security = ClassSecurityInfo()

    manage_options = ( { 'label' : 'Overview', 'action' : 'manage_overview' }
                     , 
                     ) + ZCatalog.manage_options

    def __init__(self):
        ZCatalog.__init__(self, self.getId())
        self._initIndexes()

    #
    #   Subclass extension interface
    #
    security.declarePublic( 'enumerateIndexes' ) # Subclass can call
    def enumerateIndexes( self ):
        #   Return a list of ( index_name, type ) pairs for the initial
        #   index set.
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
               )
    
    security.declarePublic( 'enumerateColumns' )
    def enumerateColumns( self ):
        #   Return a sequence of schema names to be cached.
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
               )

    def _initIndexes(self):
        base = aq_base(self)
        if hasattr(base, 'addIndex'):
            # Zope 2.4
            addIndex = self.addIndex
        else:
            # Zope 2.3 and below
            addIndex = self._catalog.addIndex
        if hasattr(base, 'addColumn'):
            # Zope 2.4
            addColumn = self.addColumn
        else:
            # Zope 2.3 and below
            addColumn = self._catalog.addColumn

        # Content indexes
        for index_name, index_type in self.enumerateIndexes():
            addIndex( index_name, index_type )

        # Cached metadata
        for column_name in self.enumerateColumns():
            addColumn( column_name )

    #
    #   ZMI methods
    #
    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'manage_overview' )
    manage_overview = DTMLFile( 'explainCatalogTool', _dtmldir )

    #
    #   'portal_catalog' interface methods
    #

    # searchResults has inherited security assertions.
    def searchResults(self, REQUEST=None, **kw):
        '''Calls ZCatalog.searchResults with extra arguments that
        limit the results to what the user is allowed to see.
        '''
        user = _getAuthenticatedUser(self)
        kw['allowedRolesAndUsers'] = list(user.getRoles()) + \
                                     ['Anonymous',
                                      'user:'+user.getUserName()]
        if not _checkPermission(
            CMFCorePermissions.AccessInactivePortalContent, self ):
            if kw.has_key('Date') and None:
                if kw.has_key('Date_usage'):
                    kw['Date'] = min(kw['Date'])
                kw['Date'] = [kw['Date'], DateTime()]
                kw['Date_usage'] = 'range:min:max'
            else:
                kw[ 'effective' ] = kw[ 'expires' ] = DateTime()
                kw['effective_usage'] = 'range:max'
                kw['expires_usage'] = 'range:min'

        return apply(ZCatalog.searchResults, (self, REQUEST), kw)

    __call__ = searchResults

    def __url(self, ob):
        return join(ob.getPhysicalPath(), '/')

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
    def reindexObject(self, object):
        '''Update catalog after object data has changed.
        '''
        url = self.__url(object)
        ## Zope 2.3 ZCatalog is supposed to work better if
        ## you don't uncatalog_object() when reindexing.
        # self.uncatalog_object(url)
        self.catalog_object(object, url)

InitializeClass(CatalogTool)
