from unittest import TestCase, TestSuite, makeSuite, main
import Zope

from DateTime import DateTime

from Products.CMFCore.tests.base.dummy import DummyContent
from Products.CMFCore.tests.base.dummy import DummyFTI
from Products.CMFCore.tests.base.testcase import SecurityTest
from Products.CMFCore.tests.base.testcase import newSecurityManager
from Products.CMFCore.tests.base.utils import has_path
from Products.CMFCore.tests.base.security import OmnipotentUser

from Products.CMFCore.TypesTool import TypesTool
from Products.CMFCore.TypesTool import FactoryTypeInformation as FTI
from Products.CMFCore.CatalogTool import CatalogTool
from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.PortalFolder import ContentFilter

def extra_meta_types():
    return [  { 'name' : 'Dummy', 'action' : 'manage_addFolder' } ]

class PortalFolderFactoryTests( SecurityTest ):

    def setUp( self ):
        SecurityTest.setUp( self )

        self.root._setObject( 'portal_types', TypesTool() )
        types_tool = self.root.portal_types
        types_tool._setObject( 'Folder'
                             , FTI( id='Folder'
                                  , meta_type=PortalFolder.meta_type
                                  , product='CMFCore'
                                  , factory='manage_addPortalFolder'
                                  , filter_content_types=0
                                  )
                             )
        types_tool._setObject( 'Dummy', DummyFTI )

    def _makeOne( self, id ):
        return PortalFolder( id ).__of__( self.root )

    def test_invokeFactory( self ):

        f = self._makeOne( 'container' )

        self.failIf( 'foo' in f.objectIds() )

        f.invokeFactory( type_name='Dummy', id='foo' )

        self.failUnless( 'foo' in f.objectIds() )
        foo = f.foo
        self.assertEqual( foo.getId(), 'foo' )
        self.assertEqual( foo.Type(), 'Dummy' )

    def test_invokeFactory_disallowed_type( self ):

        f = self._makeOne( 'container' )

        ftype = self.root.portal_types.Folder
        ftype.filter_content_types = 1

        self.assertRaises( ValueError
                         , f.invokeFactory, type_name='Folder', id='sub' )

        ftype.allowed_content_types = ( 'Folder', )
        f.invokeFactory( type_name='Folder', id='sub' )
        self.failUnless( 'sub' in f.objectIds() )

        self.assertRaises( ValueError
                         , f.invokeFactory, type_name='Dummy', id='foo' )


class PortalFolderTests( SecurityTest ):

    def setUp( self ):
        SecurityTest.setUp(self)

        root = self.root
        try: root._delObject('test')
        except AttributeError: pass
        root._setObject( 'test', PortalFolder( 'test','' ) )
    
    def test_deletePropagation( self ):

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
        test = self.root.test

        self.root._setObject( 'portal_types', TypesTool() )
        types_tool = self.root.portal_types

        self.root._setObject( 'portal_catalog', CatalogTool() )
        catalog = self.root.portal_catalog
        assert len( catalog ) == 0

        test._setObject( 'foo', DummyContent( 'foo' , catalog=1 ) )
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
        test = self.root.test

        self.root._setObject( 'portal_types', TypesTool() )
        types_tool = self.root.portal_types

        self.root._setObject( 'portal_catalog', CatalogTool() )
        catalog = self.root.portal_catalog
        assert len( catalog ) == 0

        test._setObject( 'sub', PortalFolder( 'sub', '' ) )
        sub = test.sub

        sub._setObject( 'foo', DummyContent( 'foo', catalog=1 ) )
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

        sub._setObject( 'foo', DummyContent( 'foo', catalog=1 ) )
        foo = sub.foo
        assert len( catalog ) == 1
        assert 'foo' in catalog.uniqueValuesFor( 'id' )
        assert has_path( catalog._catalog, '/test/folder/sub/foo' )

        folder.manage_renameObject( id='sub', new_id='new_sub' )
        assert 'foo' in catalog.uniqueValuesFor( 'id' )
        assert len( catalog ) == 1
        assert has_path( catalog._catalog, '/test/folder/new_sub/foo' )

        folder._setObject( 'bar', DummyContent( 'bar', catalog=1 ) )
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

    def test_manageAddFolder( self ):
        #
        #   Does MKDIR/MKCOL intercept work?
        #
        test = self.root.test
        test._setPortalTypeName( 'Folder' )
        self.root.reindexObject = lambda: 0

        self.root._setObject( 'portal_types', TypesTool() )
        types_tool = self.root.portal_types
        types_tool._setObject( 'Folder'
                             , FTI( id='Folder'
                                  , meta_type=PortalFolder.meta_type
                                  , product='CMFCore'
                                  , factory='manage_addPortalFolder'
                                  , filter_content_types=0
                                  )
                             )
        types_tool._setObject( 'Grabbed'
                             , FTI( 'Grabbed'
                                  , meta_type=PortalFolder.meta_type
                                  , product='CMFCore'
                                  , factory='manage_addPortalFolder'
                                  )
                             )

        # First, test default behavior
        test.manage_addFolder( id='simple', title='Simple' )
        self.assertEqual( test.simple.Type(), 'Folder' )
        self.assertEqual( test.simple.getId(), 'simple' )
        self.assertEqual( test.simple.Title(), 'Simple' )

        # Now, test overridden behavior
        types_tool.Folder.addAction( id = 'mkdir'
                                   , name = 'MKDIR handler'
                                   , action = 'grabbed'
                                   , permission = ''
                                   , category = 'folder'
                                   , visible = 0
                                   )
        class Grabbed:

            _grabbed_with = None

            def __init__( self, context ):
                self._context = context

            def __call__( self, id ):
                self._grabbed_with = id
                self._context._setOb( id, PortalFolder( id ) )
                self._context._getOb( id )._setPortalTypeName( 'Grabbed' )

        self.root.grabbed = Grabbed( test )

        test.manage_addFolder( id='indirect', title='Indirect' )
        self.assertEqual( test.indirect.Type(), 'Grabbed' )
        self.assertEqual( test.indirect.getId(), 'indirect' )
        self.assertEqual( test.indirect.Title(), 'Indirect' )

    def test_contentPaste( self ):
        #
        #   Does copy / paste work?
        #
        #import pdb; pdb.set_trace()
        test = self.root.test

        self.root._setObject( 'portal_types', TypesTool() )
        types_tool = self.root.portal_types
        types_tool._setObject( 'Dummy', DummyFTI )

        self.root._setObject( 'portal_catalog', CatalogTool() )
        catalog = self.root.portal_catalog
        assert len( catalog ) == 0

        test._setObject( 'sub1', PortalFolder( 'sub1', '' ) )
        sub1 = test.sub1

        test._setObject( 'sub2', PortalFolder( 'sub2', '' ) )
        sub2 = test.sub2

        test._setObject( 'sub3', PortalFolder( 'sub3', '' ) )
        sub3 = test.sub3

        sub1._setObject( 'dummy', DummyContent( 'dummy', catalog=1 ) )
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

class ContentFilterTests( TestCase ):

    def setUp( self ):
        self.dummy=DummyContent('Dummy')

    def test_empty( self ):
        cfilter = ContentFilter()
        dummy = self.dummy
        assert cfilter( dummy )
        desc = str( cfilter )
        lines = filter( None, desc.split('; ') )
        assert not lines

    def test_Type( self ):
        cfilter = ContentFilter( Type='foo' )
        dummy = self.dummy
        assert not cfilter( dummy )
        cfilter = ContentFilter( Type='Dummy Content' )
        assert cfilter( dummy )
        desc = str( cfilter )
        lines = desc.split('; ')
        assert len( lines ) == 1
        assert lines[0] == 'Type: Dummy Content'

        cfilter = ContentFilter( Type=( 'foo', 'bar' ) )
        dummy = self.dummy
        assert not cfilter( dummy )
        cfilter = ContentFilter( Type=( 'Dummy Content', 'something else' ) )
        assert cfilter( dummy )
        desc = str( cfilter )
        lines = desc.split('; ')
        assert len( lines ) == 1
        assert lines[0] == 'Type: Dummy Content, something else'

    def test_Title( self ):
        cfilter = ContentFilter( Title='foo' )
        dummy = self.dummy
        assert not cfilter( dummy )
        dummy.title = 'asdf'
        assert not cfilter( dummy )
        dummy.title = 'foolish'
        assert cfilter( dummy )
        dummy.title = 'ohsofoolish'
        assert cfilter( dummy )
        desc = str( cfilter )
        lines = desc.split('; ')
        assert len( lines ) == 1
        assert lines[0] == 'Title: foo'
    
    def test_Creator( self ):
        cfilter = ContentFilter( Creator='moe' )
        dummy = self.dummy
        assert not cfilter( dummy )
        dummy.creator = 'curly'
        assert not cfilter( dummy )
        dummy.creator = 'moe'
        self.failUnless(cfilter( dummy ))
        dummy.creator = 'shmoe'
        assert cfilter( dummy )
        desc = str( cfilter )
        lines = desc.split('; ')
        self.assertEqual(len( lines ),1)
        self.assertEqual(lines[0],'Creator: moe')
    
    def test_Description( self ):
        cfilter = ContentFilter( Description='funny' )
        dummy = self.dummy
        assert not cfilter( dummy )
        dummy.description = 'sad'
        assert not cfilter( dummy )
        dummy.description = 'funny'
        assert cfilter( dummy )
        dummy.description = 'it is funny you should mention it...'
        assert cfilter( dummy )
        desc = str( cfilter )
        lines = desc.split('; ')
        assert len( lines ) == 1
        assert lines[0] == 'Description: funny'
    
    def test_Subject( self ):
        cfilter = ContentFilter( Subject=('foo',) )
        dummy = self.dummy
        assert not cfilter( dummy )
        dummy.subject = ( 'bar', )
        assert not cfilter( dummy )
        dummy.subject = ( 'foo', )
        assert cfilter( dummy )
        dummy.subject = ( 'foo', 'bar', )
        assert cfilter( dummy )
        desc = str( cfilter )
        lines = desc.split('; ')
        assert len( lines ) == 1
        assert lines[0] == 'Subject: foo'

    def test_Subject2( self ):
        # Now test with mutli-valued
        cfilter = ContentFilter( Subject=('foo', 'bar' ) )
        dummy = self.dummy
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
        lines = desc.split('; ')
        assert len( lines ) == 1
        assert lines[0] == 'Subject: foo, bar'
    
    def test_created( self ):
        cfilter = ContentFilter( created=DateTime( '2001/01/01' )
                               , created_usage='range:min' )
        dummy = self.dummy
        assert not cfilter( dummy )
        dummy.created_date = DateTime( '2000/12/31' )
        assert not cfilter( dummy )
        dummy.created_date = DateTime( '2001/12/31' )
        assert cfilter( dummy )
        dummy.created_date = DateTime( '2001/01/01' )
        assert cfilter( dummy )
        desc = str( cfilter )
        lines = desc.split('; ')
        assert len( lines ) == 1
        assert lines[0] == 'Created since: 2001/01/01'

    def test_created2( self ):
        
        cfilter = ContentFilter( created=DateTime( '2001/01/01' )
                               , created_usage='range:max' )

        dummy = self.dummy
        assert not cfilter( dummy )
        dummy.created_date = DateTime( '2000/12/31' )
        assert cfilter( dummy )
        dummy.created_date = DateTime( '2001/12/31' )
        assert not cfilter( dummy )
        dummy.created_date = DateTime( '2001/01/01' )
        assert cfilter( dummy )
        desc = str( cfilter )
        lines = desc.split('; ')
        assert len( lines ) == 1
        assert lines[0] == 'Created before: 2001/01/01'
    
    def test_modified( self ):
        cfilter = ContentFilter( modified=DateTime( '2001/01/01' )
                               , modified_usage='range:min' )
        dummy = self.dummy
        assert not cfilter( dummy )
        dummy.modified_date = DateTime( '2000/12/31' )
        assert not cfilter( dummy )
        dummy.modified_date = DateTime( '2001/12/31' )
        assert cfilter( dummy )
        dummy.modified_date = DateTime( '2001/01/01' )
        assert cfilter( dummy )
        desc = str( cfilter )
        lines = desc.split('; ')
        assert len( lines ) == 1
        assert lines[0] == 'Modified since: 2001/01/01'

    def test_modified2( self ):
        cfilter = ContentFilter( modified=DateTime( '2001/01/01' )
                               , modified_usage='range:max' )        
        dummy = self.dummy
        assert not cfilter( dummy )
        dummy.modified_date = DateTime( '2000/12/31' )
        assert cfilter( dummy )
        dummy.modified_date = DateTime( '2001/12/31' )
        assert not cfilter( dummy )
        dummy.modified_date = DateTime( '2001/01/01' )
        assert cfilter( dummy )
        desc = str( cfilter )
        lines = desc.split('; ')
        assert len( lines ) == 1
        assert lines[0] == 'Modified before: 2001/01/01'
 
    def test_mixed( self ):
        cfilter = ContentFilter( created=DateTime( '2001/01/01' )
                               , created_usage='range:max'
                               , Title='foo'
                               )

        dummy = self.dummy
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
        lines = desc.split('; ')
        assert len( lines ) == 2, lines
        assert 'Created before: 2001/01/01' in lines
        assert 'Title: foo' in lines

def test_suite():
    return TestSuite((
        makeSuite( PortalFolderFactoryTests ),
        makeSuite( PortalFolderTests ),
        makeSuite( ContentFilterTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
