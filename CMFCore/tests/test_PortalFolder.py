import Zope
import unittest
import re, new
import OFS.Folder, OFS.SimpleItem
from AccessControl import SecurityManager
from AccessControl.SecurityManagement import newSecurityManager
import Acquisition
from DateTime import DateTime
from Products.CMFCore.TypesTool import TypesTool, FactoryTypeInformation
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

class UnitTestUser( Acquisition.Implicit ):
    """
        Stubbed out manager for unit testing purposes.
    """
    def getId( self ):
        return 'unit_tester'
    
    getUserName = getId

    def allowed( self, object, object_roles=None ):
        return 1

class DummyContent( PortalContent, OFS.SimpleItem.Item ):
    """
    """
    meta_type = 'Dummy'
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

    # WAAAAAAAAA!  we don't want the Database export/import crap in the way.
    def _getCopy( self, container ):
        return DummyContent( self.id, self.catalog )



def extra_meta_types():
    return (  { 'name' : 'Dummy', 'action' : 'manage_addFolder' }, )

class PortalFolderTests( unittest.TestCase ):

    def setUp( self ):
        get_transaction().begin()
        self._policy = UnitTestSecurityPolicy()
        SecurityManager.setSecurityPolicy(self._policy)
        self.connection = Zope.DB.open()
        self.root = self.connection.root()[ 'Application' ]
        newSecurityManager( None, UnitTestUser().__of__( self.root ) )
    
    def tearDown( self ):
        get_transaction().abort()
        self.connection.close()

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

    def test_catalogUnindexAndIndex( self ):
        #
        # Test is a new object does get cataloged upon _setObject
        # and uncataloged upon manage_deleteObjects
        #
        self.root._setObject( 'test', PortalFolder( 'test', '' ) )
        test = self.root.test

        self.root._setObject( 'portal_types', TypesTool() )
        types_tool = self.root.portal_types

        self.root._setObject( 'portal_catalog', CatalogTool() )
        catalog = self.root.portal_catalog
        assert len( catalog ) == 0

        test._setObject( 'foo', DummyContent( 'foo' , 1 ) )
        foo = test.foo
        assert foo.after_add_called
        assert not foo.before_delete_called
        assert len( catalog ) == 1

        foo.reset()
        test._delObject( 'foo' )
        assert not foo.after_add_called
        assert foo.before_delete_called
        assert len( catalog ) == 0

    def test_tracker261( self ):

        #
        #   Tracker issue #261 says that content in a deleted folder
        #   is not being uncatalogued.  Try creating a subfolder with
        #   content object, and test.
        #
        self.root._setObject( 'test', PortalFolder( 'test', '' ) )
        test = self.root.test

        self.root._setObject( 'portal_types', TypesTool() )
        types_tool = self.root.portal_types

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

        self.root._setObject( 'portal_types', TypesTool() )
        types_tool = self.root.portal_types

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
        assert has_path( catalog._catalog, '/test/folder/sub/foo' )

        #import pdb; pdb.set_trace()
        folder.manage_renameObject( id='sub', new_id='new_sub' )
        assert 'foo' in catalog.uniqueValuesFor( 'id' )
        assert len( catalog ) == 1
        assert has_path( catalog._catalog, '/test/folder/new_sub/foo' )

        folder._setObject( 'bar', DummyContent( 'bar', 1 ) )
        bar = folder.bar
        assert 'bar' in catalog.uniqueValuesFor( 'id' )
        assert len( catalog ) == 2
        assert has_path( catalog._catalog, '/test/folder/bar' )

        folder._setObject( 'sub2', PortalFolder( 'sub2', '' ) )
        sub2 = folder.sub2
        # Waaa! force sub2 to allow paste of Dummy object.
        sub2.all_meta_types = []
        sub2.all_meta_types.extend( sub2.all_meta_types )
        sub2.all_meta_types.extend( extra_meta_types() )

        cookie = folder.manage_cutObjects( ids=['bar'] )
        sub2.manage_pasteObjects( cookie )

        assert 'foo' in catalog.uniqueValuesFor( 'id' )
        assert 'bar' in catalog.uniqueValuesFor( 'id' )
        assert len( catalog ) == 2
        assert has_path( catalog._catalog, '/test/folder/sub2/bar' )

    def test_contentPaste( self ):
        #
        #   Does copy / paste work?
        #
        #import pdb; pdb.set_trace()
        test = PortalFolder( 'test', '' )
        self.root._setObject( 'test', test )
        test = self.root.test

        self.root._setObject( 'portal_types', TypesTool() )
        types_tool = self.root.portal_types
        FTI = FactoryTypeInformation
        types_tool._setObject( 'Dummy'
                             , FTI( 'Dummy'
                                  , meta_type=DummyContent.meta_type
                                  , product='OFSP'
                                  , factory='addDTMLDocument'
                                  )
                             )

        self.root._setObject( 'portal_catalog', CatalogTool() )
        catalog = self.root.portal_catalog
        assert len( catalog ) == 0

        test._setObject( 'sub1', PortalFolder( 'sub1', '' ) )
        sub1 = test.sub1

        test._setObject( 'sub2', PortalFolder( 'sub2', '' ) )
        sub2 = test.sub2

        test._setObject( 'sub3', PortalFolder( 'sub3', '' ) )
        sub3 = test.sub3

        sub1._setObject( 'dummy', DummyContent( 'dummy', 1 ) )
        assert 'dummy' in sub1.objectIds()
        assert 'dummy' in sub1.contentIds()
        assert not 'dummy' in sub2.objectIds()
        assert not 'dummy' in sub2.contentIds()
        assert not 'dummy' in sub3.objectIds()
        assert not 'dummy' in sub3.contentIds()
        assert has_path( catalog._catalog, '/test/sub1/dummy' )
        assert not has_path( catalog._catalog, '/test/sub2/dummy' )
        assert not has_path( catalog._catalog, '/test/sub3/dummy' )

        cookie = sub1.manage_copyObjects( ids = ( 'dummy', ) )
        # Waaa! force sub2 to allow paste of Dummy object.
        #import pdb; pdb.set_trace()
        sub2.all_meta_types = []
        sub2.all_meta_types.extend( sub2.all_meta_types )
        sub2.all_meta_types.extend( extra_meta_types() )
        sub2.manage_pasteObjects( cookie )
        assert 'dummy' in sub1.objectIds()
        assert 'dummy' in sub1.contentIds()
        assert 'dummy' in sub2.objectIds()
        assert 'dummy' in sub2.contentIds()
        assert not 'dummy' in sub3.objectIds()
        assert not 'dummy' in sub3.contentIds()
        assert has_path( catalog._catalog, '/test/sub1/dummy' )
        assert has_path( catalog._catalog, '/test/sub2/dummy' )
        assert not has_path( catalog._catalog, '/test/sub3/dummy' )

        cookie = sub1.manage_cutObjects( ids = ( 'dummy', ) )
        # Waaa! force sub2 to allow paste of Dummy object.
        sub3.all_meta_types = []
        sub3.all_meta_types.extend( sub3.all_meta_types )
        sub3.all_meta_types.extend( extra_meta_types() )
        sub3.manage_pasteObjects( cookie )
        assert not 'dummy' in sub1.objectIds()
        assert not 'dummy' in sub1.contentIds()
        assert 'dummy' in sub2.objectIds()
        assert 'dummy' in sub2.contentIds()
        assert 'dummy' in sub3.objectIds()
        assert 'dummy' in sub3.contentIds()
        assert not has_path( catalog._catalog, '/test/sub1/dummy' )
        assert has_path( catalog._catalog, '/test/sub2/dummy' )
        assert has_path( catalog._catalog, '/test/sub3/dummy' )


def has_path( catalog, path ):
    """
        Verify that catalog has an object at path.
    """
    rids = map( lambda x: x.data_record_id_, catalog.searchResults() )
    for rid in rids:
        if catalog.getpath( rid ) == path:
            return 1
    return 0

class LimitedUnitTestUser( Acquisition.Implicit ):
    """
        Stubbed out mmember for unit testing purposes.
    """
    def getId( self ):
        return 'unit_test_member'
    
    getUserName = getId

    def allowed( self, object, object_roles=None ):
        if object_roles is None:
            object_roles = ()
        return 'Member' in object_roles

class PortalFolderPermissionTests( unittest.TestCase ):

    def setUp( self ):
        get_transaction().begin()
        self._policy = UnitTestSecurityPolicy()
        SecurityManager.setSecurityPolicy(self._policy)
        self.connection = Zope.DB.open()
        self.root = self.connection.root()[ 'Application' ]
        self.manager = UnitTestUser().__of__( self.root )
        self.member = LimitedUnitTestUser().__of__( self.root )
        self.root._setObject( 'folder', PortalFolder( 'folder', '' ) )
        self.folder = self.root.folder
        self.folder._setObject( 'doc1', DummyContent( 'doc1' ) )
        self.folder._setObject( 'doc2', DummyContent( 'doc2' ) )
        self.folder._setObject( 'doc3', DummyContent( 'doc3' ) )
    
    def tearDown( self ):
        get_transaction().abort()
        self.connection.close()

    def test_listFolderContentsPerms( self ):
        pass

class DummyContentWithMetadata( DummyContent ):

    def Title( self ):
        return self.title

    def Creator( self ):
        return self.creator

    def Subject( self ):
        return self.subject

    def Description( self ):
        return self.description

    def created( self ):
        return self.created_date

    def modified( self ):
        return self.modified_date
    
    def Type( self ):
        return 'Dummy Content'

class ContentFilterTests( unittest.TestCase ):

    def setUp( self ):
        get_transaction().begin()

    def tearDown( self ):
        get_transaction().abort()

    def test_empty( self ):
        cfilter = ContentFilter()
        dummy = DummyContentWithMetadata( 'Dummy' )
        assert cfilter( dummy )
        desc = str( cfilter )
        lines = filter( None, string.split( desc, '; ' ) )
        assert not lines

    def test_Type( self ):
        cfilter = ContentFilter( Type='foo' )
        dummy = DummyContentWithMetadata( 'Dummy' )
        assert not cfilter( dummy )
        cfilter = ContentFilter( Type='Dummy Content' )
        assert cfilter( dummy )
        desc = str( cfilter )
        lines = string.split( desc, '; ' )
        assert len( lines ) == 1
        assert lines[0] == 'Type: Dummy Content'

        cfilter = ContentFilter( Type=( 'foo', 'bar' ) )
        dummy = DummyContentWithMetadata( 'Dummy' )
        assert not cfilter( dummy )
        cfilter = ContentFilter( Type=( 'Dummy Content', 'something else' ) )
        assert cfilter( dummy )
        desc = str( cfilter )
        lines = string.split( desc, '; ' )
        assert len( lines ) == 1
        assert lines[0] == 'Type: Dummy Content, something else'

    def test_Title( self ):
        cfilter = ContentFilter( Title='foo' )
        dummy = DummyContentWithMetadata( 'Dummy' )
        assert not cfilter( dummy )
        dummy.title = 'asdf'
        assert not cfilter( dummy )
        dummy.title = 'foolish'
        assert cfilter( dummy )
        dummy.title = 'ohsofoolish'
        assert cfilter( dummy )
        desc = str( cfilter )
        lines = string.split( desc, '; ' )
        assert len( lines ) == 1
        assert lines[0] == 'Title: foo'
    
    def test_Creator( self ):
        cfilter = ContentFilter( Creator='moe' )
        dummy = DummyContentWithMetadata( 'Dummy' )
        assert not cfilter( dummy )
        dummy.creator = 'curly'
        assert not cfilter( dummy )
        dummy.creator = 'moe'
        assert cfilter( dummy )
        dummy.creator = 'shmoe'
        assert cfilter( dummy )
        desc = str( cfilter )
        lines = string.split( desc, '; ' )
        assert len( lines ) == 1
        assert lines[0] == 'Creator: moe'
    
    def test_Description( self ):
        cfilter = ContentFilter( Description='funny' )
        dummy = DummyContentWithMetadata( 'Dummy' )
        assert not cfilter( dummy )
        dummy.description = 'sad'
        assert not cfilter( dummy )
        dummy.description = 'funny'
        assert cfilter( dummy )
        dummy.description = 'it is funny you should mention it...'
        assert cfilter( dummy )
        desc = str( cfilter )
        lines = string.split( desc, '; ' )
        assert len( lines ) == 1
        assert lines[0] == 'Description: funny'
    
    def test_Subject( self ):
        cfilter = ContentFilter( Subject=('foo',) )
        dummy = DummyContentWithMetadata( 'Dummy' )
        assert not cfilter( dummy )
        dummy.subject = ( 'bar', )
        assert not cfilter( dummy )
        dummy.subject = ( 'foo', )
        assert cfilter( dummy )
        dummy.subject = ( 'foo', 'bar', )
        assert cfilter( dummy )
        desc = str( cfilter )
        lines = string.split( desc, '; ' )
        assert len( lines ) == 1
        assert lines[0] == 'Subject: foo'

        # Now test with mutli-valued
        cfilter = ContentFilter( Subject=('foo', 'bar' ) )
        dummy = DummyContentWithMetadata( 'Dummy' )
        assert not cfilter( dummy )
        dummy.subject = ( 'baz', )
        assert not cfilter( dummy )
        dummy.subject = ( 'bar', )
        assert cfilter( dummy )
        dummy.subject = ( 'foo', )
        assert cfilter( dummy )
        dummy.subject = ( 'foo', 'bar', )
        assert cfilter( dummy )
        desc = str( cfilter )
        lines = string.split( desc, '; ' )
        assert len( lines ) == 1
        assert lines[0] == 'Subject: foo, bar'
    
    def test_created( self ):
        cfilter = ContentFilter( created=DateTime( '2001/01/01' )
                               , created_usage='range:min' )
        dummy = DummyContentWithMetadata( 'Dummy' )
        assert not cfilter( dummy )
        dummy.created_date = DateTime( '2000/12/31' )
        assert not cfilter( dummy )
        dummy.created_date = DateTime( '2001/12/31' )
        assert cfilter( dummy )
        dummy.created_date = DateTime( '2001/01/01' )
        assert cfilter( dummy )
        desc = str( cfilter )
        lines = string.split( desc, '; ' )
        assert len( lines ) == 1
        assert lines[0] == 'Created since: 2001/01/01'

        cfilter = ContentFilter( created=DateTime( '2001/01/01' )
                               , created_usage='range:max' )

        dummy = DummyContentWithMetadata( 'Dummy' )
        assert not cfilter( dummy )
        dummy.created_date = DateTime( '2000/12/31' )
        assert cfilter( dummy )
        dummy.created_date = DateTime( '2001/12/31' )
        assert not cfilter( dummy )
        dummy.created_date = DateTime( '2001/01/01' )
        assert cfilter( dummy )
        desc = str( cfilter )
        lines = string.split( desc, '; ' )
        assert len( lines ) == 1
        assert lines[0] == 'Created before: 2001/01/01'
    
    def test_modified( self ):
        cfilter = ContentFilter( modified=DateTime( '2001/01/01' )
                               , modified_usage='range:min' )
        dummy = DummyContentWithMetadata( 'Dummy' )
        assert not cfilter( dummy )
        dummy.modified_date = DateTime( '2000/12/31' )
        assert not cfilter( dummy )
        dummy.modified_date = DateTime( '2001/12/31' )
        assert cfilter( dummy )
        dummy.modified_date = DateTime( '2001/01/01' )
        assert cfilter( dummy )
        desc = str( cfilter )
        lines = string.split( desc, '; ' )
        assert len( lines ) == 1
        assert lines[0] == 'Modified since: 2001/01/01'

        cfilter = ContentFilter( modified=DateTime( '2001/01/01' )
                               , modified_usage='range:max' )

        dummy = DummyContentWithMetadata( 'Dummy' )
        assert not cfilter( dummy )
        dummy.modified_date = DateTime( '2000/12/31' )
        assert cfilter( dummy )
        dummy.modified_date = DateTime( '2001/12/31' )
        assert not cfilter( dummy )
        dummy.modified_date = DateTime( '2001/01/01' )
        assert cfilter( dummy )
        desc = str( cfilter )
        lines = string.split( desc, '; ' )
        assert len( lines ) == 1
        assert lines[0] == 'Modified before: 2001/01/01'
 
    def test_mixed( self ):
        cfilter = ContentFilter( created=DateTime( '2001/01/01' )
                               , created_usage='range:max'
                               , Title='foo'
                               )

        dummy = DummyContentWithMetadata( 'Dummy' )
        assert not cfilter( dummy )
        dummy.created_date = DateTime( '2000/12/31' )
        assert not cfilter( dummy )
        dummy.created_date = DateTime( '2001/12/31' )
        assert not cfilter( dummy )
        dummy.created_date = DateTime( '2001/01/01' )
        assert not cfilter( dummy )

        dummy.title = 'ohsofoolish'
        del dummy.created_date
        assert not cfilter( dummy )
        dummy.created_date = DateTime( '2000/12/31' )
        assert cfilter( dummy )
        dummy.created_date = DateTime( '2001/12/31' )
        assert not cfilter( dummy )
        dummy.created_date = DateTime( '2001/01/01' )
        assert cfilter( dummy )

        desc = str( cfilter )
        lines = string.split( desc, '; ' )
        assert len( lines ) == 2, lines
        assert 'Created before: 2001/01/01' in lines
        assert 'Title: foo' in lines

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite( PortalFolderTests ) )
    suite.addTest( unittest.makeSuite( PortalFolderPermissionTests ) )
    suite.addTest( unittest.makeSuite( ContentFilterTests ) )
    return suite

def run():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    run()
