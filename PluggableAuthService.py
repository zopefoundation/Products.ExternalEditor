##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights
# Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this
# distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Classes: PluggableAuthService

$Id$
"""

from Acquisition import Implicit, aq_parent, aq_base, aq_inner

from AccessControl import ClassSecurityInfo, ModuleSecurityInfo
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.Permissions import manage_users as ManageUsers
from AccessControl.User import nobody
from AccessControl.SpecialUsers import emergency_user

import sys
from zLOG import LOG, WARNING
from zExceptions import Unauthorized
from Persistence import PersistentMapping
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from ZTUtils import Batch
from App.class_init import default__class_init__ as InitializeClass
from Products.PluginRegistry.PluginRegistry import PluginRegistry
import Products

from interfaces.authservice import IUserFolder
from interfaces.authservice import _noroles
from interfaces.plugins import IExtractionPlugin
from interfaces.plugins import ILoginPasswordHostExtractionPlugin
from interfaces.plugins import IAuthenticationPlugin
from interfaces.plugins import IChallengePlugin
from interfaces.plugins import ICredentialsUpdatePlugin
from interfaces.plugins import ICredentialsResetPlugin
from interfaces.plugins import IUserFactoryPlugin
from interfaces.plugins import IAnonymousUserFactoryPlugin
from interfaces.plugins import IPropertiesPlugin
from interfaces.plugins import IGroupsPlugin
from interfaces.plugins import IRolesPlugin
from interfaces.plugins import IUpdatePlugin
from interfaces.plugins import IValidationPlugin
from interfaces.plugins import IUserEnumerationPlugin
from interfaces.plugins import IUserAdderPlugin
from interfaces.plugins import IGroupEnumerationPlugin
from interfaces.plugins import IRoleEnumerationPlugin
from interfaces.plugins import IRoleAssignerPlugin

from permissions import SearchPrincipals

from PropertiedUser import PropertiedUser
from utils import _wwwdir


security = ModuleSecurityInfo(
    'Products.PluggableAuthService.PluggableAuthService' )

#   Errors which plugins may raise, and which we suppress:
_SWALLOWABLE_PLUGIN_EXCEPTIONS = ( NameError
                                 , AttributeError
                                 , KeyError
                                 , TypeError
                                 , ValueError
                                 ) 

security.declarePublic( 'MANGLE_DELIMITER' )
MANGLE_DELIMITER = '__'

MultiPlugins = []
def registerMultiPlugin(meta_type):
    """ Register a 'multi-plugin' in order to expose it to the Add List
    """
    if meta_type in MultiPlugins:
        raise RuntimeError('Meta-type (%s) already available to Add List'
                           % meta_type)
    MultiPlugins.append(meta_type)

class DumbHTTPExtractor( Implicit ):

    __implements__ = ( ILoginPasswordHostExtractionPlugin, )

    security = ClassSecurityInfo()

    security.declarePrivate( 'extractCredentials' )
    def extractCredentials( self, request ):

        """ Pull HTTP credentials out of the request.
        """
        creds = {}
        login_pw = request._authUserPW()

        if login_pw is not None:
            name, password = login_pw

            creds[ 'login' ] = name
            creds[ 'password' ] = password
            creds[ 'remote_host' ] = request.get( 'REMOTE_HOST', '' )

            try:
                creds[ 'remote_address' ] = request.getClientAddr()
            except AttributeError:
                creds[ 'remote_address' ] = request.get( 'REMOTE_ADDR', '' )

        return creds

InitializeClass( DumbHTTPExtractor )
    

class EmergencyUserAuthenticator( Implicit ):

    __implements__ = ( IAuthenticationPlugin, )

    security = ClassSecurityInfo()

    security.declarePrivate( 'authenticateCredentials' )
    def authenticateCredentials( self, credentials ):

        """ Check credentials against the emergency user.
        """
        if isinstance( credentials, dict ):

            eu = emergency_user
            eu_name = eu.getUserName()
            login = credentials.get( 'login' )

            if login == eu_name:
                password = credentials.get( 'password' )

                if eu.authenticate( password, {} ):
                    return (eu_name, None)

        return None

InitializeClass( EmergencyUserAuthenticator )

        
class PluggableAuthService( Folder ):

    """ All-singing, all-dancing user folder.
    """
    __implements__ = ( IUserFolder, )

    security = ClassSecurityInfo()

    meta_type = 'Pluggable Auth Service'

    _id = id = 'acl_users'

    _emergency_user = emergency_user
    _nobody = nobody

    maxlistusers = -1   # Don't allow local role form to try to list us!
    
    def getId( self ):

        return self._id

    #
    #   IUserFolder implementation
    #
    security.declareProtected( ManageUsers, 'getUser' )
    def getUser( self, name ):

        """ See IUserFolder.
        """
        plugins = self._getOb( 'plugins' )

        user_id = self._verifyUser( plugins, login=name )

        if not user_id:
            return None

        return self._findUser( plugins, user_id, name 
                           # , cache=self._getUserCache()
                             )

    security.declareProtected( ManageUsers, 'getUserById' )
    def getUserById( self, id, default=None ):

        """ See IUserFolder.
        """
        plugins = self._getOb( 'plugins' )
        user_id = None

        try:
            plugin_id, principal_id = self._unmangleId( id )
        except ValueError:
            user_id = self._verifyUser( plugins, user_id=id )
        else:
            plugin = getattr( self, plugin_id, None )

            if plugin is not None:
                try:
                    user_info = plugin.enumerateUsers( id=principal_id
                                                     , exact_match=True )
                    assert( len( user_info ) in [ 0, 1 ] )
                except _SWALLOWABLE_PLUGIN_EXCEPTIONS:
                    LOG('PluggableAuthService', WARNING, 
                        'UserEnumerationPlugin %s error' % plugin_id,
                        error=sys.exc_info())
                else:
                    if user_info:
                        user_id = id

        if not user_id:
            return default

        return self._findUser( plugins, user_id
                           # , cache=self._getUserCache()
                             )

    security.declarePublic( 'validate' )     # XXX: public?
    def validate( self, request, auth='', roles=_noroles ):

        """ See IUserFolder.
        """
        plugins = self._getOb( 'plugins' )
        is_top = self._isTop()

        user_ids = self._extractUserIds( request
                                       , plugins
                                     # , cache=self._v_credentials_cache
                                       )
        ( accessed
        , container
        , name
        , value
        ) = self._getObjectContext( request[ 'PUBLISHED' ], request )

        for user_id, login in user_ids:

            user = self._findUser( plugins, user_id, login
                               # , cache=self._getUserCache()
                                 , request=request
                                 )

            if aq_base( user ) is emergency_user:

                if is_top:
                    return user
                else:
                    return None

            if self._authorizeUser( user    
                                  , accessed
                                  , container
                                  , name
                                  , value
                                  , roles
                                  ):
                return user

        if not is_top:
            return None

        #
        #   No other user folder above us can satisfy, and we have no user;
        #   return a constructed anonymous only if anonymous is authorized.
        #
        anonymous = self._createAnonymousUser( plugins )
        if self._authorizeUser( anonymous
                              , accessed
                              , container
                              , name
                              , value
                              , roles
                              ):
            return anonymous

        return None

    security.declareProtected( SearchPrincipals, 'searchUsers')
    def searchUsers(self, **kw):
        """ Search for users """
        exact_match = kw.get( 'exact_match', False )
        search_id = kw.get( 'id', None )
        search_name = kw.get( 'name', None )
        
        if exact_match and search_id:
            plugin_id, principal_id = self._unmangleId( search_id )
            plugin = getattr( self, plugin_id, None )
            if plugin is not None:
                try:
                    user_info = plugin.enumerateUsers( id=principal_id
                                                     , exact_match=True )
                    assert( len( user_info ) in [ 0, 1 ] )
                    if user_info:
                        user_info = user_info[ 0 ]
                        info = {}
                        info.update( user_info )
                        info[ 'userid' ] = principal_id
                        info[ 'id' ] = self._computeMangledId( user_info )
                        info[ 'principal_type' ] = 'user'
                        info[ 'title' ] = info[ 'login' ]
                        return ( info, )
                    else:
                        return ()
                except _SWALLOWABLE_PLUGIN_EXCEPTIONS:
                    LOG('PluggableAuthService', WARNING, 
                        'UserEnumerationPlugin %s error' % plugin_id,
                        error=sys.exc_info())
                    return ()
        
        result = []
        max_results = kw.get('max_results', '')
        sort_by = kw.get('sort_by', '')

        # We apply sorting and slicing here across all sets, so don't 
        # make the plugin do it
        if sort_by:
            del kw['sort_by']
        if max_results:
            del kw['max_results']
        if search_name:
            if kw.get('id') is not None:
                del kw['id'] # don't even bother searching by id
            kw['login'] = kw['name']

        plugins = self._getOb( 'plugins' )
        enumerators = plugins.listPlugins( IUserEnumerationPlugin )
        
        for enumerator_id, enum in enumerators:
            try:
                user_list = enum.enumerateUsers(**kw)
                for user_info in user_list:
                    info = {}
                    info.update( user_info )
                    info[ 'userid' ] = info[ 'id' ]
                    info[ 'id' ] = self._computeMangledId( info )
                    info[ 'principal_type' ] = 'user'
                    info[ 'title' ] = info[ 'login' ]
                    result.append(info)
                    
            except _SWALLOWABLE_PLUGIN_EXCEPTIONS:
                LOG('PluggableAuthService', WARNING, 
                    'UserEnumerationPlugin %s error' % enumerator_id,
                    error=sys.exc_info())

        if sort_by:
            result.sort( lambda a, b: cmp( a.get(sort_by, '').lower()
                                         , b.get(sort_by, '').lower()
                                         ) )

        if max_results:
            try:
                max_results = int(max_results)
                result = result[:max_results]
            except ValueError:
                pass

        return tuple(result)

    security.declareProtected( SearchPrincipals, 'searchGroups')
    def searchGroups(self, **kw):
        """ Search for groups """
        exact_match = kw.get( 'exact_match', False )
        search_id = kw.get( 'id', None )
        search_name = kw.get( 'name', None )
        
        if exact_match and search_id:
            plugin_id, principal_id = self._unmangleId( search_id )
            plugin = getattr( self, plugin_id, None )
            if plugin is not None:
                try:
                    group_info = plugin.enumerateGroups( id=principal_id
                                                       , exact_match=True )
                    assert( len( group_info ) in [ 0, 1 ] )
                    if group_info:
                        group_info = group_info[ 0 ]
                        info = {}
                        info.update( group_info )
                        info[ 'groupid' ] = principal_id
                        info[ 'id' ] = self._computeMangledId( group_info )
                        info[ 'principal_type' ] = 'group'
                        info[ 'title' ] = "(Group) %s" % principal_id
                        return ( info, )
                    else:
                        return ()
                except _SWALLOWABLE_PLUGIN_EXCEPTIONS:
                    LOG('PluggableAuthService', WARNING, 
                        'GroupEnumerationPlugin %s error' % plugin_id,
                        error=sys.exc_info())
                    return ()
        
        result = []
        max_results = kw.get('max_results', '')
        sort_by = kw.get('sort_by', '')

        # We apply sorting and slicing here across all sets, so don't 
        # make the plugin do it
        if sort_by:
            del kw['sort_by']
        if max_results:
            del kw['max_results']
        if search_name:
            if kw.get('id') is not None:
                del kw['id']
            kw['title'] = kw['name']

        plugins = self._getOb( 'plugins' )
        enumerators = plugins.listPlugins( IGroupEnumerationPlugin )

        for enumerator_id, enum in enumerators:
            try:
                 group_list = enum.enumerateGroups(**kw)
                 for group_info in group_list:
                    info = {}
                    info.update( group_info )
                    info[ 'groupid' ] = info[ 'id' ]
                    info[ 'id' ] = self._computeMangledId( info )
                    info[ 'principal_type' ] = 'group'
                    info[ 'title' ] = "(Group) %s" % info[ 'groupid' ]
                    result.append(info)
            except _SWALLOWABLE_PLUGIN_EXCEPTIONS:
                LOG('PluggableAuthService', WARNING, 
                    'GroupEnumerationPlugin %s error' % enumerator_id,
                    error=sys.exc_info())

        if sort_by:
            result.sort( lambda a, b: cmp( a.get(sort_by, '').lower()
                                         , b.get(sort_by, '').lower()
                                         ) )

        if max_results:
            try:
                max_results = int(max_results)
                result = result[:max_results + 1]
            except ValueError:
                pass

        return tuple(result)

    security.declareProtected( SearchPrincipals, 'searchPrincipals')
    def searchPrincipals(self, groups_first=False, **kw):
        """ Search for principals (users, groups, or both) """
        exact_match = kw.get( 'exact_match', False )
        max_results = kw.get( 'max_results', '' )

        search_id = kw.get( 'id', None )
        search_name = kw.get( 'name', None )
        if search_name:
            kw['title'] = search_name
            kw['login'] = search_name

        if exact_match and search_id:
            plugin_id, principal_id = self._unmangleId( search_id )
            plugin = getattr( self, plugin_id, None )
            if plugin is not None:
                if getattr( aq_base( plugin ), 'enumerateUsers', None ):
                    enumeratePrincipals = plugin.enumerateUsers
                    local_key = 'userid'
                    principal_type = 'user'
                    title_key = 'login'
                    title_pattern = "%s"
                else:
                    enumeratePrincipals = plugin.enumerateGroups
                    local_key = 'groupid'
                    principal_type = 'group'
                    title_key = 'groupid'
                    title_pattern = "(Group) %s"
                try:
                    principal_info = enumeratePrincipals( id=principal_id
                                                        , exact_match=True )
                    assert( len( principal_info ) in [ 0, 1 ] )
                    if principal_info:
                        principal_info = principal_info[ 0 ]
                        info = {}
                        info.update( principal_info )
                        info[ local_key ] = principal_id
                        info[ 'id' ] = self._computeMangledId( principal_info )
                        info[ 'principal_type' ] = principal_type
                        info[ 'title' ] = title_pattern % info[ title_key ]
                        return ( info, )
                    else:
                        return ()
                except _SWALLOWABLE_PLUGIN_EXCEPTIONS:
                    LOG('PluggableAuthService', WARNING, 
                        'UserEnumeratePlugin %s error' % plugin_id,
                        error=sys.exc_info())
                    return ()

        users = [ d.copy() for d in self.searchUsers( **kw ) ]
        groups = [ d.copy() for d in self.searchGroups( **kw ) ]

        if groups_first:
            result = groups + users
        else:
            result = users + groups

        if max_results:
            try:
                max_results = int( max_results )
                result = result[ :max_results + 1 ]
            except ValueError:
                pass

        return tuple( result )

    security.declarePrivate( '__creatable_by_emergency_user__' )
    def __creatable_by_emergency_user__( self ):
        return 1

    security.declarePrivate( '_setObject' )
    def _setObject( self, id, object, roles=None, user=None, set_owner=0 ):
        #
        #   Override ObjectManager's version to change the default for
        #   'set_owner' (we don't want to enforce ownership on contained
        #   objects).
        Folder._setObject( self, id, object, roles, user, set_owner )

    security.declarePrivate( '_delOb' )
    def _delOb( self, id ):
        #
        #   Override ObjectManager's version to clean up any plugin
        #   registrations for the deleted object
        #
        plugins = self._getOb( 'plugins', None )

        if plugins is not None:
            plugins.removePluginById( id )

        Folder._delOb( self, id )

    #
    # ZMI stuff
    #
    security.declareProtected(ManageUsers, 'manage_search')
    manage_search = PageTemplateFile('www/pasSearch', globals())

    manage_options = ( Folder.manage_options[:1]
                      + ( { 'label' : 'Search'
                          , 'action': 'manage_search' }
                        , 
                        )
                      + Folder.manage_options[2:]
                      )

    security.declareProtected(ManageUsers, 'resultsBatch')
    def resultsBatch(self, results, REQUEST, size=20, orphan=2, overlap=0):
        """ ZMI helper for getting batching for displaying search results """
        try:
            start_val = REQUEST.get('batch_start', '0')
            start = int(start_val)
            size = int(REQUEST.get('batch_size', size))
        except ValueError:
            start = 0

        batch = Batch(results, size, start, 0, orphan, overlap)

        if batch.end < len(results):
            qs = self._getBatchLink( REQUEST.get('QUERY_STRING', '')
                                   , start
                                   , batch.end
                                   )
            REQUEST.set( 'next_batch_url'
                       , '%s?%s' % (REQUEST.get('URL'), qs)
                       )

        if start > 0:
            new_start = start - size - 1

            if new_start < 0:
                new_start = 0

            qs = self._getBatchLink( REQUEST.get('QUERY_STRING', '')
                                   , start
                                   , new_start
                                   )
            REQUEST.set( 'previous_batch_url'
                       , '%s?%s' % (REQUEST.get('URL'), qs)
                       )

        return batch


    security.declarePrivate('_getBatchLink')
    def _getBatchLink(self, qs, old_start, new_start):
        """ Internal helper to generate correct query strings """
        if new_start is not None:
            if not qs:
                qs = 'batch_start=%d' % new_start
            elif qs.startswith('batch_start='):
                qs = qs.replace( 'batch_start=%d' % old_start
                               , 'batch_start=%d' % new_start
                               )
            elif qs.find('&batch_start=') != -1:
                qs = qs.replace( '&batch_start=%d' % old_start
                               , '&batch_start=%d' % new_start
                               )
            else:
                qs = '%s&batch_start=%d' % (qs, new_start)

        return qs


    #
    #   Helper methods
    #
    security.declarePrivate( '_extractUserIds' )
    def _extractUserIds( self, request, plugins, cache=None ):

        """ request -> [ validated_user_id ]

        o For each set of extracted credentials, try to authenticate
          a user;  accumulate a list of the IDs of such users over all
          our authentication and extraction plugins.
        """
        if cache is None:
            cache = {}

        result = []
        user_ids = []

        try:
            extractors = plugins.listPlugins( IExtractionPlugin )
        except _SWALLOWABLE_PLUGIN_EXCEPTIONS:
            LOG('PluggableAuthService', WARNING, 
                'Plugin listing error',
                error=sys.exc_info())
            extractors = ()

        if not extractors:
            extractors = ( ( 'default', DumbHTTPExtractor() ), )

        try:
            authenticators = plugins.listPlugins( IAuthenticationPlugin )
        except _SWALLOWABLE_PLUGIN_EXCEPTIONS:
            LOG('PluggableAuthService', WARNING, 
                'Plugin listing error',
                error=sys.exc_info())
            authenticators = ()

        for extractor_id, extractor in extractors:

            try:
                credentials = extractor.extractCredentials( request )
            except _SWALLOWABLE_PLUGIN_EXCEPTIONS:
                LOG('PluggableAuthService', WARNING, 
                    'ExtractionPlugin %s error' % extractor_id,
                    error=sys.exc_info())
                continue

            if credentials:

                try:
                    credentials[ 'extractor' ] = extractor_id # XXX: in key?
                    items = credentials.items()
                  # credentials[ 'extractor' ] = extractor_id # XXX: in key?
                    items.sort()
                    cache_key = tuple( items )
                except _SWALLOWABLE_PLUGIN_EXCEPTIONS:
                    LOG('PluggableAuthService', WARNING, 
                        'Credentials error: %s' % credentials,
                        error=sys.exc_info())
                    cache_key = None
                else:
                    user_ids = cache.get( cache_key, [] )

                if not user_ids:

                    # first try to authenticate against the emergency
                    # user, and return immediately if authenticated
                    user_id, name = self._tryEmergencyUserAuthentication( 
                                                                credentials )

                    if user_id is not None:
                        return [ ( user_id, name ) ]

                    for authenticator_id, auth in authenticators:

                        try:
                            user_id, name = auth.authenticateCredentials( 
                                                                credentials ) 
                        except _SWALLOWABLE_PLUGIN_EXCEPTIONS:
                            LOG('PluggableAuthService', WARNING, 
                                'AuthenticationPlugin %s error' % authenticator_id,
                                error=sys.exc_info())
                            continue

                        if user_id is not None:
                            mangled_id = self._mangleId( authenticator_id
                                                       , user_id )
                            user_ids.append( (mangled_id, name) )


                    if cache_key is not None:
                        cache[ cache_key ] = user_ids

                result.extend( user_ids )

        if not user_ids:
            user_id, name = self._tryEmergencyUserAuthentication( 
                    DumbHTTPExtractor().extractCredentials( request ) )

            if user_id is not None:
                result.append( ( user_id, name ) )

        return result

    security.declarePrivate( '_unmangleId' )
    def _unmangleId( self, mangled_id ):
        
        return mangled_id.split( MANGLE_DELIMITER, 1 )

    security.declarePrivate( '_mangleId' )
    def _mangleId( self, namespace, id ):

        return MANGLE_DELIMITER.join( ( namespace, id ) )

    security.declarePrivate( '_computeMangledId' )
    def _computeMangledId( self, info_dict ):

        """ Synthesize an from info_dict.
        
        o Mangle plugin and original id together.
        """
        return self._mangleId( info_dict[ 'pluginid' ], info_dict[ 'id' ] )

    security.declarePrivate( '_tryEmergencyUserAuthentication' )
    def _tryEmergencyUserAuthentication( self, credentials ):
        
        """ credentials -> emergency_user or None
        """
        try:
            eua = EmergencyUserAuthenticator()
            user_id, name = eua.authenticateCredentials( credentials )
        except _SWALLOWABLE_PLUGIN_EXCEPTIONS:
            LOG('PluggableAuthService', WARNING, 
                'Credentials error: %s' % credentials,
                error=sys.exc_info())
            user_id, name = ( None, None )

        return ( user_id, name )

    security.declarePrivate( '_getGroupsForPrincipal' )
    def _getGroupsForPrincipal( self
                              , principal
                              , request=None
                              , plugins=None
                              , ignore_plugins=None
                              ):
        all_groups = {}

        if ignore_plugins is None:
            ignore_plugins = ()

        if plugins is None:
            plugins = self._getOb( 'plugins' )
        groupmakers = plugins.listPlugins( IGroupsPlugin )

        for groupmaker_id, groupmaker in groupmakers:

            if groupmaker_id in ignore_plugins:
                continue
            groups = groupmaker.getGroupsForPrincipal( principal, request )
            for group in groups:
                try:
                    # We may be getting a mangled groupid already
                    group_plugin, group_id = self._unmangleId( group )
                except ValueError:
                    # group id hasn't been mangled yet
                    mangled_group = self._mangleId( groupmaker_id, group )
                else:
                    # group has already been mangled
                    mangled_group = group
                principal._addGroups( [ mangled_group ] )
                all_groups[ mangled_group ] = 1

        return all_groups.keys()

    security.declarePrivate( '_createAnonymousUser' )
    def _createAnonymousUser( self, plugins ):

        """ Allow IAnonymousUserFactoryPlugins to create or fall back.
        """
        factories = plugins.listPlugins( IAnonymousUserFactoryPlugin )

        for factory_id, factory in factories:

            anon = factory.createAnonymousUser()

            if anon is not None:
                return anon.__of__( self )

        return nobody.__of__( self )

    security.declarePrivate( '_createUser' )
    def _createUser( self, plugins, user_id, name ):

        """ Allow IUserFactoryPlugins to create, or fall back to default.
        """
        factories = plugins.listPlugins( IUserFactoryPlugin )

        for factory_id, factory in factories:

            user = factory.createUser( user_id, name )

            if user is not None:
                return user.__of__( self )

        return PropertiedUser( user_id, name ).__of__( self )

    security.declarePrivate( '_findUser' )
    def _findUser( self, plugins, user_id, name=None, cache=None
                 , request=None ):

        """ user_id -> decorated_user
        """
        if user_id == self._emergency_user.getUserName():
            return self._emergency_user

        if cache is None:
            cache = {}

        user = cache.get( user_id )

        if user is None:

            user = self._createUser( plugins, user_id, name )
            propfinders = plugins.listPlugins( IPropertiesPlugin )

            for propfinder_id, propfinder in propfinders:

                data = propfinder.getPropertiesForUser( user, request )
                if data:
                    user.addPropertysheet( propfinder_id, data )

            groups = self._getGroupsForPrincipal( user, request
                                                , plugins=plugins )
            user._addGroups( groups )
            
            rolemakers = plugins.listPlugins( IRolesPlugin )

            for rolemaker_id, rolemaker in rolemakers:

                roles = rolemaker.getRolesForPrincipal( user, request )

                # Role names *can't* be mangled;  other parts of the
                # client applications know about them!
                if roles:
                    user._addRoles( roles )

            cache[ user_id ] = user

        return user.__of__( self )

    security.declarePrivate( '_verifyUser' )
    def _verifyUser( self, plugins, user_id=None, login=None ):

        """ user_id -> boolean
        """
        criteria = {}

        if user_id is not None:
            criteria[ 'id' ] = user_id
            criteria[ 'exact_match' ] = True

        if login is not None:
            criteria[ 'login' ] = login

        if criteria:

            enumerators = plugins.listPlugins( IUserEnumerationPlugin )

            for enumerator_id, enumerator in enumerators:
                try:
                    info = enumerator.enumerateUsers( **criteria )

                    if info:
                        return self._computeMangledId( info[0] )

                except _SWALLOWABLE_PLUGIN_EXCEPTIONS:
                    LOG('PluggableAuthService', WARNING, 
                        'UserEnumerationPlugin %s error' % enumerator_id,
                        error=sys.exc_info())

        return 0

    security.declarePrivate( '_authorizeUser' )
    def _authorizeUser( self
                      , user
                      , accessed
                      , container
                      , name
                      , value
                      , roles=_noroles
                      ):

        """ -> boolean (whether user has roles).

        o Add the user to the SM's stack, if successful.

        o Return
        """
        user = aq_base( user ).__of__( self )
        newSecurityManager( None, user )
        security = getSecurityManager()
        try:
            try:
                if security.validate( accessed
                                    , container
                                    , name
                                    , value
                                    , roles
                                    ):
                    return 1
            except:
                noSecurityManager()
                raise

        except Unauthorized:
            pass

        return 0


    security.declarePrivate( '_isTop' )
    def _isTop( self ):

        """ Are we the user folder in the root object?
        """
        try:
            parent = aq_base( aq_parent( self ) )
            if parent is None:
                return 0
            return parent.isTopLevelPrincipiaApplicationObject
        except AttributeError:
            return 0


    security.declarePrivate( '_getObjectContext' )
    def _getObjectContext( self, v, request ):

        """ request -> ( a, c, n, v )

        o 'a 'is the object the object was accessed through

        o 'c 'is the physical container of the object

        o 'n 'is the name used to access the object

        o 'v' is the object (value) we're validating access to

        o XXX:  Lifted from AccessControl.User.BasicUserFolder._getobcontext
        """
        if len( request.steps ) == 0: # someone deleted root index_html

            request[ 'RESPONSE' ].notFoundError(
                'no default view (root default view was probably deleted)' )

        root = request[ 'PARENTS' ][ -1 ]
        request_container = aq_parent( root )

        n = request.steps[ -1 ]

        # default to accessed and container as v.aq_parent
        a = c = request[ 'PARENTS' ][ 0 ]

        # try to find actual container
        inner = aq_inner( v )
        innerparent = aq_parent( inner )

        if innerparent is not None:

            # this is not a method, we needn't treat it specially
            c = innerparent

        elif hasattr(v, 'im_self'):

            # this is a method, we need to treat it specially
            c = v.im_self
            c = aq_inner( v )

        # if pub's aq_parent or container is the request container, it
        # means pub was accessed from the root
        if a is request_container:
            a = root

        if c is request_container:
            c = root

        return a, c, n, v

    security.declarePrivate( '_getEmergencyUser' )
    def _getEmergencyUser( self ):

        return emergency_user.__of__( self )


    security.declarePrivate( '_doAddUser' )
    def _doAddUser( self, login, password, roles, domains, **kw ):
        """ Create a user with login, password and roles if, and only if,
            we have a registered user manager and role manager that will
            accept specific plugin interfaces.
        """
        plugins = self._getOb( 'plugins' )
        useradders = plugins.listPlugins( IUserAdderPlugin )
        roleassigners = plugins.listPlugins( IRoleAssignerPlugin )
        
        user = None

        if not (useradders and roleassigners):
            raise NotImplementedError( "There are no plugins"
                                       " that can create"
                                       " users and assign roles to them." )

        for useradder_id, useradder in useradders:
            if useradder.doAddUser( login, password ):
                user = self.getUser( login )
                break

        for roleassigner_id, roleassigner in roleassigners:
            for role in roles:
                try:
                    roleassigner.doAssignRoleToPrincipal( user.getId(), role )
                except _SWALLOWABLE_PLUGIN_EXCEPTIONS:
                    LOG('PluggableAuthService', WARNING, 
                        'RoleAssigner %s error' % roleassigner_id,
                        error=sys.exc_info())
                    pass

    security.declarePublic('all_meta_types')
    def all_meta_types(self):
        """ What objects can be put in here? """
        allowed_types = tuple(MultiPlugins)

        return [x for x in Products.meta_types if x['name'] in allowed_types]

    security.declarePrivate( 'manage_beforeDelete' )
    def manage_beforeDelete(self, item, container):
        if item is self:
            try:
                del container.__allow_groups__
            except:
                pass

    security.declarePrivate( 'manage_afterAdd' )
    def manage_afterAdd(self, item, container):
        if item is self:
            container.__allow_groups__ = aq_base(self)

    security.declarePublic( 'hasUsers' )
    def hasUsers(self):
        """Zope quick start sacrifice.

        The quick start page expects a hasUsers() method.
        """
        return True

InitializeClass( PluggableAuthService )

_PLUGIN_TYPE_INFO = (
    ( IExtractionPlugin
    , 'IExtractionPlugin'
    , 'extraction'
    , "Extraction plugins are responsible for extracting credentials " 
      "from the request."
    )
  , ( IAuthenticationPlugin
    , 'IAuthenticationPlugin'
    , 'authentication'
    , "Authentication plugins are responsible for validating credentials "
      "generated by the Extraction Plugin."
    )
  , ( IChallengePlugin
    , 'IChallengePlugin'
    , 'challenge'
    , "Challenge plugins initiate a challenge to the user to provide "
      "credentials."
    )
  , ( ICredentialsUpdatePlugin
    , 'ICredentialsUpdatePlugin'
    , 'update credentials'
    , "Credential update plugins respond to the user changing "
      "credentials."
    )
  , ( ICredentialsResetPlugin
    , 'ICredentialsResetPlugin'
    , 'reset credentials'
    , "Credential clear plugins respond to a user logging out."
    )
  , ( IUserFactoryPlugin
    , 'IUserFactoryPlugin'
    , 'userfactory'
    , "Create users."
    )
  , ( IAnonymousUserFactoryPlugin
    , 'IAnonymousUserFactoryPlugin'
    , 'anonymoususerfactory'
    , "Create anonymous users."
    )
  , ( IPropertiesPlugin
    , 'IPropertiesPlugin'
    , 'properties'
    , "Properties plugins generate property sheets for users."
    )
  , ( IGroupsPlugin
    , 'IGroupsPlugin'
    , 'groups'
    , "Groups plugins determine the groups to which a user belongs."
    )
  , ( IRolesPlugin
    , 'IRolesPlugin'
    , 'roles'
    , "Roles plugins determine the global roles which a user has."
    )
  , ( IUpdatePlugin
    , 'IUpdatePlugin'
    , 'update'
    , "Update plugins allow the user or the application to update "
      "the user's properties."
    )
  , ( IValidationPlugin
    , 'IValidationPlugin'
    , 'validation'
    , "Validation plugins specify allowable values for user properties "
      "(e.g., minimum password length, allowed characters, etc.)"
    )
  , ( IUserEnumerationPlugin
    , 'IUserEnumerationPlugin'
    , 'user_enumeration'
    , "Enumeration plugins allow querying users by ID, and searching for "
      "users who match particular criteria."
    )
  , ( IUserAdderPlugin
    , 'IUserAdderPlugin'
    , 'user_adder'
    , "User Adder plugins allow the Pluggable Auth Service to create users."
    )
  , ( IGroupEnumerationPlugin
    , 'IGroupEnumerationPlugin'
    , 'group_enumeration'
    , "Enumeration plugins allow querying groups by ID."
    )
  , ( IRoleEnumerationPlugin
    , 'IRoleEnumerationPlugin'
    , 'role_enumeration'
    , "Enumeration plugins allow querying roles by ID."
    )
  , ( IRoleAssignerPlugin
    , 'IRoleAssignerPlugin'
    , 'role_assigner'
    , "Role Assigner plugins allow the Pluggable Auth Service to assign"
      " roles to principals."
    )
  )

def addPluggableAuthService( dispatcher, REQUEST=None ):

    """ Add a PluggableAuthService to 'self.
    """
    pas = PluggableAuthService()
    preg = PluginRegistry( _PLUGIN_TYPE_INFO )
    preg._setId( 'plugins' )
    pas._setObject( 'plugins', preg )
    dispatcher._setObject( pas.getId(), pas )


    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(
                                '%s/manage_workspace'
                                '?manage_tabs_message='
                                'PluggableAuthService+added.'
                              % dispatcher.absolute_url() ) 
