##############################################################################
#
# Copyright (c) 2004 Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source 
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this 
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" External method for upgrading existing AccessControl.User.UserFolder

    NOTA BENE: Use at your own risk. This external method will replace a
    stock User Folder (AccessControl.User.UserFolder) with a
    PluggableAuthService consisting of the following:

        - ZODBUserManager with a record for each existing User
          (AccessControl.User.User)

        - ZODBRoleManger with a record for each existing role present
          in the __ac_roles__ attribute of the container (minus Anonymous
          and Authenticated)

    Each migrated user will be assigned the global roles they have in the
    previous acl_users record.

$Id$
"""
from zLOG import LOG, INFO

def _write( response, tool, message, level=INFO ):

    LOG( tool, level, message )
    if response is not None:
        response.write( message )

def _replaceUserFolder(self, RESPONSE=None):
    """replaces the old acl_users folder with a PluggableAuthService,
    preserving users and passwords, if possible
    """
    from Acquisition import aq_base
    from Products.PluggableAuthService.PluggableAuthService \
        import PluggableAuthService, _PLUGIN_TYPE_INFO
    from Products.PluginRegistry.PluginRegistry import PluginRegistry
    from Products.PluggableAuthService.plugins.ZODBUserManager \
        import ZODBUserManager
    from Products.PluggableAuthService.plugins.ZODBRoleManager \
        import ZODBRoleManager
    from Products.PluggableAuthService.interfaces.plugins \
         import IAuthenticationPlugin, IUserEnumerationPlugin
    from Products.PluggableAuthService.interfaces.plugins \
        import IRolesPlugin, IRoleEnumerationPlugin, IRoleAssignerPlugin

    if getattr( aq_base(self), '__allow_groups__', None ):
        if self.__allow_groups__.__class__ is PluggableAuthService:
            _write( RESPONSE
                  , 'replaceUserFolder'
                  , 'Already replaced this user folder\n' )
            return
        old_acl = self.__allow_groups__
        new_acl = PluggableAuthService()
        preg = PluginRegistry( _PLUGIN_TYPE_INFO )
        preg._setId( 'plugins' )
        new_acl._setObject( 'plugins', preg )
        self._setObject( 'new_acl_users', new_acl )
        new_acl = getattr( self, 'new_acl_users' )

        user_folder = ZODBUserManager( 'users' )
        new_acl._setObject( 'users', user_folder )
        role_manager = ZODBRoleManager( 'roles' )
        new_acl._setObject( 'roles', role_manager )

        plugins = getattr( new_acl, 'plugins' )
        plugins.activatePlugin( IAuthenticationPlugin, 'users' )
        plugins.activatePlugin( IUserEnumerationPlugin, 'users' )
        plugins.activatePlugin( IRolesPlugin, 'roles' )
        plugins.activatePlugin( IRoleEnumerationPlugin, 'roles' )
        plugins.activatePlugin( IRoleAssignerPlugin, 'roles' )
        for user_name in old_acl.getUserNames():
            old_user = old_acl.getUser( user_name )
            _write( RESPONSE
                  , 'replaceRootUserFolder'
                  , 'Translating user %s\n' % user_name )
            _migrate_user( new_acl.users, user_name, old_user._getPassword() )
            new_user = new_acl.getUser( user_name )
            for role_id in old_user.getRoles():
                if role_id not in ['Authenticated', 'Anonymous']:
                    new_acl.roles.assignRoleToPrincipal( role_id,
                                                         new_user.getId() )
        self._delObject( 'acl_users' )
        self._setObject( 'acl_users', aq_base( new_acl ) )
        self._delObject( 'new_acl_users' )
        self.__allow_groups__ = aq_base( new_acl )
        _write( RESPONSE
              , 'replaceRootUserFolder'
              , 'Replaced root acl_users with PluggableAuthService\n' )

    get_transaction().commit()

def _migrate_user( new_user_folder, login, password ):

    from AccessControl import AuthEncoding

    if AuthEncoding.is_encrypted( password ):
        new_user_folder._user_passwords[ login ] = password
        new_user_folder._login_to_userid[ login ] = login
        new_user_folder._userid_to_login[ login ] = login
    else:
        new_user_folder.addUser( login, login, password )

def _upgradeLocalRoleAssignments(self, RESPONSE=None):
    """ upgrades the __ac_local_roles__ attributes on objects to account
        for a move to using the PluggableAuthService.
    """
    from Acquisition import aq_base

    seen = {}

    def descend(user_folder, obj):
        path = obj.getPhysicalPath()
        if path not in seen:
            # get __ac_local_roles__, break it apart and refashion it
            # with new spellings.
            seen[path] = 1
            if getattr( aq_base( obj ), '__ac_local_roles__', None ):
                if not callable(obj.__ac_local_roles__):
                    new_map = {}
                    map = obj.__ac_local_roles__
                    for key in map.keys():
                        new_principals = user_folder.searchPrincipals(id=key)
                        if not new_principals:
                            _write(
                                RESPONSE
                              , 'upgradeLocalRoleAssignmentsFromRoot'
                              , '  Ignoring map for unknown principal %s\n'
                                % key )
                            new_map[key] = map[key]
                            continue
                        npid = new_principals[0]['id']
                        new_map[npid] = map[key]
                        _write( RESPONSE
                              , 'upgradeLocalRoleAssignmentsFromRoot'
                              , '  Translated %s to %s\n' % ( key, npid ) )
                        _write( RESPONSE
                              , 'upgradeLocalRoleAssignmentsFromRoot'
                              , '  Assigned roles %s to %s\n' % ( map[key]
                                                                , npid ) )
                    obj.__ac_local_roles__ = new_map
                    _write( RESPONSE
                          , 'upgradeLocalRoleAssignmentsFromRoot'
                          , ( 'Local Roles map changed for (%s)\n'
                              % '/'.join(path) ) )
            if (len(seen) % 100 ) == 0:
                get_transaction().commit()
                _write( RESPONSE
                      , 'upgradeLocalRoleAssignmentsFromRoot'
                      , "  -- committed at object # %d\n" % len( seen ) )
            if getattr(aq_base(obj), 'isPrincipiaFolderish', 0):
                for o in obj.objectValues():
                    descend(user_folder, o)

    if getattr( self, '_upgraded_acl_users', None ):
        _write( RESPONSE
              , '_upgradeLocalRoleAssignments'
              , 'Local role assignments have already been updated.\n' )
        return

    descend(self.acl_users, self)

    get_transaction().commit()

# External Method to use

def replace_acl_users(self, RESPONSE=None):
    _replaceUserFolder(self, RESPONSE)
    _upgradeLocalRoleAssignments(self, RESPONSE)
    self._upgraded_acl_users = 1
    _write( RESPONSE
          , 'replace_acl_users'
          , 'Root acl_users has been replaced,'
            ' and local role assignments updated.\n' )
