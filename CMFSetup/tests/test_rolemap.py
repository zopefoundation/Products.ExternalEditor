""" CMFSetup rolemap export / import unit tests

$Id$
"""

import unittest

from OFS.Folder import Folder

from common import BaseRegistryTests
from common import DummyExportContext
from common import DummyImportContext

class RolemapConfiguratorTests( BaseRegistryTests ):

    def _getTargetClass( self ):

        from Products.CMFSetup.rolemap import RolemapConfigurator
        return RolemapConfigurator

    def test_listRoles_normal( self ):

        EXPECTED = [ 'Anonymous', 'Authenticated', 'Manager', 'Owner' ]
        self.root.site = Folder( id='site' )
        site = self.root.site
        exporter = self._makeOne( site )

        roles = list( exporter.listRoles() )
        self.assertEqual( len( roles ), len( EXPECTED ) )

        roles.sort()

        for found, expected in zip( roles, EXPECTED ):
            self.assertEqual( found, expected )

    def test_listRoles_added( self ):

        EXPECTED = [ 'Anonymous', 'Authenticated', 'Manager', 'Owner', 'ZZZ' ]
        self.root.site = Folder( id='site' )
        site = self.root.site
        existing_roles = list( getattr( site, '__ac_roles__', [] ) )[:]
        existing_roles.append( 'ZZZ' )
        site.__ac_roles__ = existing_roles

        exporter = self._makeOne( site )

        roles = list( exporter.listRoles() )
        self.assertEqual( len( roles ), len( EXPECTED ) )

        roles.sort()

        for found, expected in zip( roles, EXPECTED ):
            self.assertEqual( found, expected )

    def test_listPermissions_nooverrides( self ):

        self.root.site = Folder( id='site' )
        site = self.root.site
        exporter = self._makeOne( site )

        self.assertEqual( len( exporter.listPermissions() ), 0 )

    def test_listPermissions_nooverrides( self ):

        site = Folder( id='site' ).__of__( self.root )
        exporter = self._makeOne( site )

        self.assertEqual( len( exporter.listPermissions() ), 0 )

    def test_listPermissions_acquire( self ):

        ACI = 'Access contents information'
        ROLES = [ 'Manager', 'Owner' ]

        site = Folder( id='site' ).__of__( self.root )
        site.manage_permission( ACI, ROLES, acquire=1 )
        exporter = self._makeOne( site )

        self.assertEqual( len( exporter.listPermissions() ), 1 )
        info = exporter.listPermissions()[ 0 ]
        self.assertEqual( info[ 'name' ], ACI )
        self.assertEqual( info[ 'roles' ], ROLES )
        self.failUnless( info[ 'acquire' ] )

    def test_listPermissions_no_acquire( self ):

        ACI = 'Access contents information'
        ROLES = [ 'Manager', 'Owner' ]

        site = Folder( id='site' ).__of__( self.root )
        site.manage_permission( ACI, ROLES )
        exporter = self._makeOne( site )

        self.assertEqual( len( exporter.listPermissions() ), 1 )
        info = exporter.listPermissions()[ 0 ]
        self.assertEqual( info[ 'name' ], ACI )
        self.assertEqual( info[ 'roles' ], ROLES )
        self.failIf( info[ 'acquire' ] )

    def test_generateXML_empty( self ):

        self.root.site = Folder( id='site' )
        site = self.root.site
        exporter = self._makeOne( site ).__of__( site )

        self._compareDOM( exporter.generateXML(), _EMPTY_EXPORT )

    def test_generateXML_added_role( self ):

        self.root.site = Folder( id='site' )
        site = self.root.site
        existing_roles = list( getattr( site, '__ac_roles__', [] ) )[:]
        existing_roles.append( 'ZZZ' )
        site.__ac_roles__ = existing_roles
        exporter = self._makeOne( site ).__of__( site )

        self._compareDOM( exporter.generateXML(), _ADDED_ROLE_EXPORT )

    def test_generateEXML_acquired_perm( self ):

        ACI = 'Access contents information'
        ROLES = [ 'Manager', 'Owner' ]

        site = Folder( id='site' ).__of__( self.root )
        site.manage_permission( ACI, ROLES, acquire=1 )
        exporter = self._makeOne( site ).__of__( site )

        self._compareDOM( exporter.generateXML(), _ACQUIRED_EXPORT )

    def test_generateEXML_unacquired_perm( self ):

        ACI = 'Access contents information'
        ROLES = [ 'Manager', 'Owner', 'ZZZ' ]

        site = Folder( id='site' ).__of__( self.root )
        existing_roles = list( getattr( site, '__ac_roles__', [] ) )[:]
        existing_roles.append( 'ZZZ' )
        site.__ac_roles__ = existing_roles
        site.manage_permission( ACI, ROLES )
        exporter = self._makeOne( site ).__of__( site )

        self._compareDOM( exporter.generateXML(), _COMBINED_EXPORT )

    def test_generateEXML_unacquired_perm_added_role( self ):

        ACI = 'Access contents information'
        ROLES = [ 'Manager', 'Owner' ]

        site = Folder( id='site' ).__of__( self.root )
        site.manage_permission( ACI, ROLES )
        exporter = self._makeOne( site ).__of__( site )

        self._compareDOM( exporter.generateXML(), _UNACQUIRED_EXPORT )

    def test_parseXML_empty( self ):

        self.root.site = Folder( id='site' )
        site = self.root.site
        existing_roles = list( getattr( site, '__ac_roles__', [] ) )[:]
        exporter = self._makeOne( site )

        exporter.parseXML( _EMPTY_EXPORT )

        new_roles = list( getattr( site, '__ac_roles__', [] ) )[:]

        existing_roles.sort()
        new_roles.sort()

        self.assertEqual( existing_roles, new_roles )

    def test_parseXML_added_role( self ):

        self.root.site = Folder( id='site' )
        site = self.root.site
        exporter = self._makeOne( site )

        self.failIf( site._has_user_defined_role( 'ZZZ' ) )
        exporter.parseXML( _ADDED_ROLE_EXPORT )
        self.failUnless( site._has_user_defined_role( 'ZZZ' ) )

    def test_parseXML_acquired_permission( self ):

        ACI = 'Access contents information'

        self.root.site = Folder( id='site' )
        site = self.root.site
        exporter = self._makeOne( site )

        existing_allowed = [ x[ 'name' ]
                                for x in site.rolesOfPermission( ACI )
                                if x[ 'selected' ] ]

        self.assertEqual( existing_allowed, [ 'Manager' ] )
    
        self.failUnless( site.acquiredRolesAreUsedBy( ACI ) )

        exporter.parseXML( _ACQUIRED_EXPORT )

        new_allowed = [ x[ 'name' ]
                           for x in site.rolesOfPermission( ACI )
                           if x[ 'selected' ] ]

        self.assertEqual( new_allowed, [ 'Manager', 'Owner' ] )
    
        self.failUnless( site.acquiredRolesAreUsedBy( ACI ) )

    def test_parseXML_unacquired_permission( self ):

        ACI = 'Access contents information'

        self.root.site = Folder( id='site' )
        site = self.root.site
        exporter = self._makeOne( site )

        existing_allowed = [ x[ 'name' ]
                                for x in site.rolesOfPermission( ACI )
                                if x[ 'selected' ] ]

        self.assertEqual( existing_allowed, [ 'Manager' ] )
    
        self.failUnless( site.acquiredRolesAreUsedBy( ACI ) )

        exporter.parseXML( _UNACQUIRED_EXPORT )

        new_allowed = [ x[ 'name' ]
                           for x in site.rolesOfPermission( ACI )
                           if x[ 'selected' ] ]

        self.assertEqual( new_allowed, [ 'Manager', 'Owner' ] )
    
        self.failIf( site.acquiredRolesAreUsedBy( ACI ) )

    def test_parseXML_unacquired_permission_added_role( self ):

        ACI = 'Access contents information'

        self.root.site = Folder( id='site' )
        site = self.root.site
        exporter = self._makeOne( site )

        existing_allowed = [ x[ 'name' ]
                                for x in site.rolesOfPermission( ACI )
                                if x[ 'selected' ] ]

        self.assertEqual( existing_allowed, [ 'Manager' ] )
    
        self.failUnless( site.acquiredRolesAreUsedBy( ACI ) )

        self.failIf( site._has_user_defined_role( 'ZZZ' ) )
        exporter.parseXML( _COMBINED_EXPORT )
        self.failUnless( site._has_user_defined_role( 'ZZZ' ) )

        new_allowed = [ x[ 'name' ]
                           for x in site.rolesOfPermission( ACI )
                           if x[ 'selected' ] ]

        self.assertEqual( new_allowed, [ 'Manager', 'Owner', 'ZZZ' ] )
    
        self.failIf( site.acquiredRolesAreUsedBy( ACI ) )


_EMPTY_EXPORT = """\
<?xml version="1.0"?>
<rolemap>
  <roles>
    <role name="Anonymous"/>
    <role name="Authenticated"/>
    <role name="Manager"/>
    <role name="Owner"/>
  </roles>
  <permissions>
  </permissions>
</rolemap>
"""

_ADDED_ROLE_EXPORT = """\
<?xml version="1.0"?>
<rolemap>
  <roles>
    <role name="Anonymous"/>
    <role name="Authenticated"/>
    <role name="Manager"/>
    <role name="Owner"/>
    <role name="ZZZ"/>
  </roles>
  <permissions>
  </permissions>
</rolemap>
"""

_ACQUIRED_EXPORT = """\
<?xml version="1.0"?>
<rolemap>
  <roles>
    <role name="Anonymous"/>
    <role name="Authenticated"/>
    <role name="Manager"/>
    <role name="Owner"/>
  </roles>
  <permissions>
    <permission name="Access contents information"
                roles="Manager Owner"
                acquire="True" />
  </permissions>
</rolemap>
"""

_UNACQUIRED_EXPORT = """\
<?xml version="1.0"?>
<rolemap>
  <roles>
    <role name="Anonymous"/>
    <role name="Authenticated"/>
    <role name="Manager"/>
    <role name="Owner"/>
  </roles>
  <permissions>
    <permission name="Access contents information"
                roles="Manager Owner"
                acquire="False" />
  </permissions>
</rolemap>
"""

_COMBINED_EXPORT = """\
<?xml version="1.0"?>
<rolemap>
  <roles>
    <role name="Anonymous"/>
    <role name="Authenticated"/>
    <role name="Manager"/>
    <role name="Owner"/>
    <role name="ZZZ"/>
  </roles>
  <permissions>
    <permission name="Access contents information"
                roles="Manager Owner ZZZ"
                acquire="False" />
  </permissions>
</rolemap>
"""

class Test_exportRolemap( BaseRegistryTests ):

    def test_unchanged( self ):

        self.root.site = Folder( 'site' )
        site = self.root.site

        context = DummyExportContext( site )

        from Products.CMFSetup.rolemap import exportRolemap
        exportRolemap( context )

        self.assertEqual( len( context._wrote ), 1 )
        filename, text, content_type = context._wrote[ 0 ]
        self.assertEqual( filename, 'rolemap.xml' )
        self._compareDOM( text, _EMPTY_EXPORT )
        self.assertEqual( content_type, 'text/xml' )

    def test_added_role( self ):

        self.root.site = Folder( 'site' )
        site = self.root.site
        existing_roles = list( getattr( site, '__ac_roles__', [] ) )[:]
        existing_roles.append( 'ZZZ' )
        site.__ac_roles__ = existing_roles

        context = DummyExportContext( site )

        from Products.CMFSetup.rolemap import exportRolemap
        exportRolemap( context )

        self.assertEqual( len( context._wrote ), 1 )
        filename, text, content_type = context._wrote[ 0 ]
        self.assertEqual( filename, 'rolemap.xml' )
        self._compareDOM( text, _ADDED_ROLE_EXPORT )
        self.assertEqual( content_type, 'text/xml' )


    def test_acquired_perm( self ):

        ACI = 'Access contents information'
        ROLES = [ 'Manager', 'Owner' ]

        self.root.site = Folder( 'site' )
        site = self.root.site
        site.manage_permission( ACI, ROLES, acquire=1 )

        context = DummyExportContext( site )

        from Products.CMFSetup.rolemap import exportRolemap
        exportRolemap( context )

        self.assertEqual( len( context._wrote ), 1 )
        filename, text, content_type = context._wrote[ 0 ]
        self.assertEqual( filename, 'rolemap.xml' )
        self._compareDOM( text, _ACQUIRED_EXPORT )
        self.assertEqual( content_type, 'text/xml' )

    def test_unacquired_perm( self ):

        ACI = 'Access contents information'
        ROLES = [ 'Manager', 'Owner', 'ZZZ' ]

        self.root.site = Folder( 'site' )
        site = self.root.site
        existing_roles = list( getattr( site, '__ac_roles__', [] ) )[:]
        existing_roles.append( 'ZZZ' )
        site.__ac_roles__ = existing_roles
        site.manage_permission( ACI, ROLES )

        context = DummyExportContext( site )

        from Products.CMFSetup.rolemap import exportRolemap
        exportRolemap( context )

        self.assertEqual( len( context._wrote ), 1 )
        filename, text, content_type = context._wrote[ 0 ]
        self.assertEqual( filename, 'rolemap.xml' )
        self._compareDOM( text, _COMBINED_EXPORT )
        self.assertEqual( content_type, 'text/xml' )

    def test_unacquired_perm_added_role( self ):

        ACI = 'Access contents information'
        ROLES = [ 'Manager', 'Owner' ]

        self.root.site = Folder( 'site' )
        site = self.root.site
        site.manage_permission( ACI, ROLES )

        context = DummyExportContext( site )

        from Products.CMFSetup.rolemap import exportRolemap
        exportRolemap( context )

        self.assertEqual( len( context._wrote ), 1 )
        filename, text, content_type = context._wrote[ 0 ]
        self.assertEqual( filename, 'rolemap.xml' )
        self._compareDOM( text, _UNACQUIRED_EXPORT )
        self.assertEqual( content_type, 'text/xml' )

class Test_importRolemap( BaseRegistryTests ):

    def test_empty_default_purge( self ):

        self.root.site = Folder( id='site' )
        site = self.root.site
        original_roles = list( getattr( site, '__ac_roles__', [] ) )[:]
        modified_roles = original_roles[:]
        modified_roles.append( 'ZZZ' )
        site.__ac_roles__ = modified_roles

        context = DummyImportContext( site )
        context._files[ 'rolemap.xml' ] = _EMPTY_EXPORT

        from Products.CMFSetup.rolemap import importRolemap
        importRolemap( context )

        new_roles = list( getattr( site, '__ac_roles__', [] ) )[:]

        original_roles.sort()
        new_roles.sort()

        self.assertEqual( original_roles, new_roles )

    def test_empty_explicit_purge( self ):

        self.root.site = Folder( id='site' )
        site = self.root.site
        original_roles = list( getattr( site, '__ac_roles__', [] ) )[:]
        modified_roles = original_roles[:]
        modified_roles.append( 'ZZZ' )
        site.__ac_roles__ = modified_roles

        context = DummyImportContext( site, True )
        context._files[ 'rolemap.xml' ] = _EMPTY_EXPORT

        from Products.CMFSetup.rolemap import importRolemap
        importRolemap( context )

        new_roles = list( getattr( site, '__ac_roles__', [] ) )[:]

        original_roles.sort()
        new_roles.sort()

        self.assertEqual( original_roles, new_roles )

    def test_empty_skip_purge( self ):

        self.root.site = Folder( id='site' )
        site = self.root.site
        original_roles = list( getattr( site, '__ac_roles__', [] ) )[:]
        modified_roles = original_roles[:]
        modified_roles.append( 'ZZZ' )
        site.__ac_roles__ = modified_roles

        context = DummyImportContext( site, False )
        context._files[ 'rolemap.xml' ] = _EMPTY_EXPORT

        from Products.CMFSetup.rolemap import importRolemap
        importRolemap( context )

        new_roles = list( getattr( site, '__ac_roles__', [] ) )[:]

        modified_roles.sort()
        new_roles.sort()

        self.assertEqual( modified_roles, new_roles )

    def test_acquired_permission_explicit_purge( self ):

        ACI = 'Access contents information'
        VIEW = 'View'

        self.root.site = Folder( id='site' )
        site = self.root.site
        site.manage_permission( ACI, () )
        site.manage_permission( VIEW, () )

        existing_allowed = [ x[ 'name' ]
                                for x in site.rolesOfPermission( ACI )
                                if x[ 'selected' ] ]

        self.assertEqual( existing_allowed, [] )
    
        self.failIf( site.acquiredRolesAreUsedBy( ACI ) )
        self.failIf( site.acquiredRolesAreUsedBy( VIEW ) )

        context = DummyImportContext( site, True )
        context._files[ 'rolemap.xml' ] = _ACQUIRED_EXPORT

        from Products.CMFSetup.rolemap import importRolemap
        importRolemap( context )

        new_allowed = [ x[ 'name' ]
                           for x in site.rolesOfPermission( ACI )
                           if x[ 'selected' ] ]

        self.assertEqual( new_allowed, [ 'Manager', 'Owner' ] )
    
        # ACI is overwritten by XML, but VIEW was purged
        self.failUnless( site.acquiredRolesAreUsedBy( ACI ) )
        self.failUnless( site.acquiredRolesAreUsedBy( VIEW ) )

    def test_acquired_permission_no_purge( self ):

        ACI = 'Access contents information'
        VIEW = 'View'

        self.root.site = Folder( id='site' )
        site = self.root.site
        site.manage_permission( ACI, () )
        site.manage_permission( VIEW, () )

        existing_allowed = [ x[ 'name' ]
                                for x in site.rolesOfPermission( ACI )
                                if x[ 'selected' ] ]

        self.assertEqual( existing_allowed, [] )
    
        self.failIf( site.acquiredRolesAreUsedBy( ACI ) )

        context = DummyImportContext( site, False )
        context._files[ 'rolemap.xml' ] = _ACQUIRED_EXPORT

        from Products.CMFSetup.rolemap import importRolemap
        importRolemap( context )

        new_allowed = [ x[ 'name' ]
                           for x in site.rolesOfPermission( ACI )
                           if x[ 'selected' ] ]

        self.assertEqual( new_allowed, [ 'Manager', 'Owner' ] )
    
        # ACI is overwritten by XML, but VIEW is not
        self.failUnless( site.acquiredRolesAreUsedBy( ACI ) )
        self.failIf( site.acquiredRolesAreUsedBy( VIEW ) )

    def test_unacquired_permission_explicit_purge( self ):

        ACI = 'Access contents information'
        VIEW = 'View'

        self.root.site = Folder( id='site' )
        site = self.root.site
        site.manage_permission( VIEW, () )

        existing_allowed = [ x[ 'name' ]
                                for x in site.rolesOfPermission( ACI )
                                if x[ 'selected' ] ]

        self.assertEqual( existing_allowed, [ 'Manager' ] )
    
        self.failUnless( site.acquiredRolesAreUsedBy( ACI ) )
        self.failIf( site.acquiredRolesAreUsedBy( VIEW ) )

        context = DummyImportContext( site, True )
        context._files[ 'rolemap.xml' ] = _UNACQUIRED_EXPORT

        from Products.CMFSetup.rolemap import importRolemap
        importRolemap( context )

        new_allowed = [ x[ 'name' ]
                           for x in site.rolesOfPermission( ACI )
                           if x[ 'selected' ] ]

        self.assertEqual( new_allowed, [ 'Manager', 'Owner' ] )
    
        self.failIf( site.acquiredRolesAreUsedBy( ACI ) )
        self.failUnless( site.acquiredRolesAreUsedBy( VIEW ) )

    def test_unacquired_permission_skip_purge( self ):

        ACI = 'Access contents information'
        VIEW = 'View'

        self.root.site = Folder( id='site' )
        site = self.root.site
        site.manage_permission( VIEW, () )

        existing_allowed = [ x[ 'name' ]
                                for x in site.rolesOfPermission( ACI )
                                if x[ 'selected' ] ]

        self.assertEqual( existing_allowed, [ 'Manager' ] )
    
        self.failUnless( site.acquiredRolesAreUsedBy( ACI ) )
        self.failIf( site.acquiredRolesAreUsedBy( VIEW ) )

        context = DummyImportContext( site, False )
        context._files[ 'rolemap.xml' ] = _UNACQUIRED_EXPORT

        from Products.CMFSetup.rolemap import importRolemap
        importRolemap( context )

        new_allowed = [ x[ 'name' ]
                           for x in site.rolesOfPermission( ACI )
                           if x[ 'selected' ] ]

        self.assertEqual( new_allowed, [ 'Manager', 'Owner' ] )
    
        self.failIf( site.acquiredRolesAreUsedBy( ACI ) )
        self.failIf( site.acquiredRolesAreUsedBy( VIEW ) )

    def test_unacquired_permission_added_role_explicit_purge( self ):

        ACI = 'Access contents information'
        VIEW = 'View'

        self.root.site = Folder( id='site' )
        site = self.root.site
        site.manage_permission( VIEW, () )

        existing_allowed = [ x[ 'name' ]
                                for x in site.rolesOfPermission( ACI )
                                if x[ 'selected' ] ]

        self.assertEqual( existing_allowed, [ 'Manager' ] )
    
        self.failUnless( site.acquiredRolesAreUsedBy( ACI ) )
        self.failIf( site.acquiredRolesAreUsedBy( VIEW ) )

        self.failIf( site._has_user_defined_role( 'ZZZ' ) )

        context = DummyImportContext( site, True )
        context._files[ 'rolemap.xml' ] = _COMBINED_EXPORT

        from Products.CMFSetup.rolemap import importRolemap
        importRolemap( context )

        self.failUnless( site._has_user_defined_role( 'ZZZ' ) )

        new_allowed = [ x[ 'name' ]
                           for x in site.rolesOfPermission( ACI )
                           if x[ 'selected' ] ]

        self.assertEqual( new_allowed, [ 'Manager', 'Owner', 'ZZZ' ] )
    
        self.failIf( site.acquiredRolesAreUsedBy( ACI ) )
        self.failUnless( site.acquiredRolesAreUsedBy( VIEW ) )

    def test_unacquired_permission_added_role_skip_purge( self ):

        ACI = 'Access contents information'
        VIEW = 'View'

        self.root.site = Folder( id='site' )
        site = self.root.site
        site.manage_permission( VIEW, () )

        existing_allowed = [ x[ 'name' ]
                                for x in site.rolesOfPermission( ACI )
                                if x[ 'selected' ] ]

        self.assertEqual( existing_allowed, [ 'Manager' ] )
    
        self.failUnless( site.acquiredRolesAreUsedBy( ACI ) )
        self.failIf( site.acquiredRolesAreUsedBy( VIEW ) )

        self.failIf( site._has_user_defined_role( 'ZZZ' ) )

        context = DummyImportContext( site, False )
        context._files[ 'rolemap.xml' ] = _COMBINED_EXPORT

        from Products.CMFSetup.rolemap import importRolemap
        importRolemap( context )

        self.failUnless( site._has_user_defined_role( 'ZZZ' ) )

        new_allowed = [ x[ 'name' ]
                           for x in site.rolesOfPermission( ACI )
                           if x[ 'selected' ] ]

        self.assertEqual( new_allowed, [ 'Manager', 'Owner', 'ZZZ' ] )
    
        self.failIf( site.acquiredRolesAreUsedBy( ACI ) )
        self.failIf( site.acquiredRolesAreUsedBy( VIEW ) )


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite( RolemapConfiguratorTests ),
        unittest.makeSuite( Test_exportRolemap ),
        unittest.makeSuite( Test_importRolemap ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
