import Zope
import unittest
import re
import OFS.Folder, OFS.SimpleItem
from AccessControl import SecurityManager
from Products.CMFCore.CatalogTool import CatalogTool
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.PortalFolder import *

class UnitTestSecurityPolicy:
    """
        Stub out the existing security policy for unit testing purposes.
    """
    #
    #   Standard SecurityPolicy interface
    #
    def validate(self, accessed, container, name, value, context, roles,
                 *args, **kw):
        return 1
    
    def checkPermission( self, permission, object, context) :
        return 1

class DummyContent( PortalContent ):
    """
    """
    after_add_called = before_delete_called = 0

    def __init__( self, id, catalog=0 ):
        self.id = id
        self.reset()
        self.catalog = catalog

    def manage_afterAdd( self, item, container ):
        self.after_add_called = 1
        if self.catalog:
            PortalContent.manage_afterAdd( self, item, container )

    def manage_beforeDelete( self, item, container ):
        self.before_delete_called = 1
        if self.catalog:
            PortalContent.manage_beforeDelete( self, item, container )
    
    def reset( self ):
        self.after_add_called = self.before_delete_called = 0

class PortalFolderTests( unittest.TestCase ):

    def setUp( self ):
        get_transaction().begin()
        self._policy = UnitTestSecurityPolicy()
        SecurityManager.setSecurityPolicy(self._policy)
        self.root = Zope.app()
    
    def tearDown( self ):
        get_transaction().abort()

    def test_deletePropagation( self ):

        test = PortalFolder( 'test', '' )
        self.root._setObject( 'test', test )
        test = self.root.test
        foo = DummyContent( 'foo' )

        foo.reset()
        assert not foo.after_add_called
        assert not foo.before_delete_called
        test._setObject( 'foo', foo )
        assert foo.after_add_called
        assert not foo.before_delete_called

        foo.reset()
        test._delObject( 'foo' )
        assert not foo.after_add_called
        assert foo.before_delete_called

        foo.reset()
        test._setObject( 'foo', foo )
        test._delOb( 'foo' )    # doesn't propagate
        assert foo.after_add_called
        assert not foo.before_delete_called

    def test_manageDelObjects( self ):

        test = PortalFolder( 'test', '' )
        self.root._setObject( 'test', test )
        test = self.root.test
        foo = DummyContent( 'foo' )

        test._setObject( 'foo', foo )
        foo.reset()
        test.manage_delObjects( ids=[ 'foo' ] )
        assert not foo.after_add_called
        assert foo.before_delete_called

    def test_tracker261( self ):

        #
        #   Tracker issue #261 says that content in a deleted folder
        #   is not being uncatalogued.  Try creating a subfolder with
        #   content object, and test.
        #
        self.root._setObject( 'test', PortalFolder( 'test', '' ) )
        test = self.root.test

        self.root._setObject( 'portal_catalog', CatalogTool() )
        catalog = self.root.portal_catalog
        assert len( catalog ) == 0

        test._setObject( 'sub', PortalFolder( 'sub', '' ) )
        sub = test.sub

        sub._setObject( 'foo', DummyContent( 'foo', 1 ) )
        foo = sub.foo

        assert foo.after_add_called
        assert not foo.before_delete_called
        assert len( catalog ) == 1

        foo.reset()
        test.manage_delObjects( ids=[ 'sub' ] )
        assert not foo.after_add_called
        assert foo.before_delete_called
        assert len( catalog ) == 0

    def test_folderMove( self ):
        #
        #   Does the catalog stay synched when folders are moved?
        #
        self.root._setObject( 'test', PortalFolder( 'test', '' ) )
        test = self.root.test

        self.root._setObject( 'portal_catalog', CatalogTool() )
        catalog = self.root.portal_catalog
        assert len( catalog ) == 0

        test._setObject( 'folder', PortalFolder( 'folder', '' ) )
        folder = test.folder

        folder._setObject( 'sub', PortalFolder( 'sub', '' ) )
        sub = folder.sub

        sub._setObject( 'foo', DummyContent( 'foo', 1 ) )
        foo = sub.foo
        assert len( catalog ) == 1
        assert 'foo' in catalog.uniqueValuesFor( 'id' )

        folder.manage_renameObject( id='sub', new_id='new_sub' )
        assert 'foo' in catalog.uniqueValuesFor( 'id' )
        assert len( catalog ) == 1


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite( PortalFolderTests ) )
    return suite

def run():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    run()
