from unittest import TestCase, TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()
  
import cStringIO

from AccessControl import SecurityManager
from Acquisition import Implicit
from Acquisition import aq_base
from DateTime import DateTime
from webdav.WriteLockInterface import WriteLockInterface
from OFS.Application import Application
from OFS.Image import manage_addFile
from OFS.tests.testCopySupport import makeConnection
from Testing.makerequest import makerequest

from Products.CMFCore.CatalogTool import CatalogTool
from Products.CMFCore.interfaces.Dynamic import DynamicType as IDynamicType
from Products.CMFCore.tests.base.dummy import DummyContent
from Products.CMFCore.tests.base.dummy import DummyFactory
from Products.CMFCore.tests.base.security import OmnipotentUser
from Products.CMFCore.tests.base.testcase import newSecurityManager
from Products.CMFCore.tests.base.testcase import noSecurityManager
from Products.CMFCore.tests.base.testcase import SecurityTest
from Products.CMFCore.tests.base.tidata import FTIDATA_DUMMY
from Products.CMFCore.tests.base.utils import has_path
from Products.CMFCore.TypesTool import FactoryTypeInformation as FTI
from Products.CMFCore.TypesTool import TypesTool
from Products.CMFCore.exceptions import BadRequest


def extra_meta_types():
    return [  { 'name' : 'Dummy', 'action' : 'manage_addFolder' } ]


class PortalFolderFactoryTests( SecurityTest ):

    def setUp( self ):
        from Products.CMFCore.PortalFolder import PortalFolder
        SecurityTest.setUp( self )

        self.root._setObject( 'portal_types', TypesTool() )
        types_tool = self.root.portal_types
        types_tool._setObject( 'Folder'
                             , FTI( id='Folder'
                                  , title='Folder or Directory'
                                  , meta_type=PortalFolder.meta_type
                                  , product='CMFCore'
                                  , factory='manage_addPortalFolder'
                                  , filter_content_types=0
                                  )
                             )
        fti = FTIDATA_DUMMY[0].copy()
        types_tool._setObject( 'Dummy Content', FTI(**fti) )

    def _makeOne( self, id ):
        from Products.CMFCore.PortalFolder import PortalFolder
        return PortalFolder( id ).__of__( self.root )

    def test_invokeFactory( self ):

        f = self._makeOne( 'container' )

        self.failIf( 'foo' in f.objectIds() )

        f.manage_addProduct = { 'FooProduct' : DummyFactory(f) }
        f.invokeFactory( type_name='Dummy Content', id='foo' )

        self.failUnless( 'foo' in f.objectIds() )
        foo = f.foo
        self.assertEqual( foo.getId(), 'foo' )
        self.assertEqual( foo.getPortalTypeName(), 'Dummy Content' )
        self.assertEqual( foo.Type(), 'Dummy Content Title' )

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
                         , f.invokeFactory
                         , type_name='Dummy Content', id='foo' )


class PortalFolderTests( SecurityTest ):

    def setUp( self ):
        from Products.CMFCore.PortalFolder import PortalFolder
        SecurityTest.setUp(self)

        root = self.root
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
        from Products.CMFCore.PortalFolder import PortalFolder

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

    def test_tracker215( self ):
        self.failUnless(IDynamicType.isImplementedBy(self.root.test))
        self.failUnless(WriteLockInterface.isImplementedBy(self.root.test))

    def test_folderMove( self ):
        #
        #   Does the catalog stay synched when folders are moved?
        #
        from Products.CMFCore.PortalFolder import PortalFolder

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
        self.failUnless( 'foo' in catalog.uniqueValuesFor('getId') )
        assert has_path( catalog._catalog, '/test/folder/sub/foo' )

        get_transaction().commit(1)
        folder.manage_renameObject(id='sub', new_id='new_sub')

        self.failUnless( 'foo' in catalog.uniqueValuesFor('getId') )
        assert len( catalog ) == 1
        assert has_path( catalog._catalog, '/test/folder/new_sub/foo' )

        folder._setObject( 'bar', DummyContent( 'bar', catalog=1 ) )
        bar = folder.bar
        self.failUnless( 'bar' in catalog.uniqueValuesFor('getId') )
        assert len( catalog ) == 2
        assert has_path( catalog._catalog, '/test/folder/bar' )

        folder._setObject( 'sub2', PortalFolder( 'sub2', '' ) )
        sub2 = folder.sub2
        # Waaa! force sub2 to allow paste of Dummy object.
        sub2.all_meta_types = []
        sub2.all_meta_types.extend( sub2.all_meta_types )
        sub2.all_meta_types.extend( extra_meta_types() )

        get_transaction().commit(1)
        cookie = folder.manage_cutObjects(ids=['bar'])
        sub2.manage_pasteObjects(cookie)

        self.failUnless( 'foo' in catalog.uniqueValuesFor('getId') )
        self.failUnless( 'bar' in catalog.uniqueValuesFor('getId') )
        assert len( catalog ) == 2
        assert has_path( catalog._catalog, '/test/folder/sub2/bar' )

    def test_manageAddFolder( self ):
        #
        #   Does MKDIR/MKCOL intercept work?
        #
        from Products.CMFCore.PortalFolder import PortalFolder

        test = self.root.test
        test._setPortalTypeName( 'Folder' )
        self.root.reindexObject = lambda: 0

        self.root._setObject( 'portal_types', TypesTool() )
        types_tool = self.root.portal_types
        types_tool._setObject( 'Folder'
                             , FTI( id='Folder'
                                  , title='Folder or Directory'
                                  , meta_type=PortalFolder.meta_type
                                  , product='CMFCore'
                                  , factory='manage_addPortalFolder'
                                  , filter_content_types=0
                                  )
                             )
        types_tool._setObject( 'Grabbed'
                             , FTI( 'Grabbed'
                                  , title='Grabbed Content'
                                  , meta_type=PortalFolder.meta_type
                                  , product='CMFCore'
                                  , factory='manage_addPortalFolder'
                                  )
                             )

        # First, test default behavior
        test.manage_addFolder( id='simple', title='Simple' )
        self.assertEqual( test.simple.getPortalTypeName(), 'Folder' )
        self.assertEqual( test.simple.Type(), 'Folder or Directory' )
        self.assertEqual( test.simple.getId(), 'simple' )
        self.assertEqual( test.simple.Title(), 'Simple' )

        # Now, test overridden behavior
        types_tool.Folder.setMethodAliases( {'mkdir': 'grabbed'} )

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
        self.assertEqual( test.indirect.getPortalTypeName(), 'Grabbed' )
        self.assertEqual( test.indirect.Type(), 'Grabbed Content' )
        self.assertEqual( test.indirect.getId(), 'indirect' )
        self.assertEqual( test.indirect.Title(), 'Indirect' )

    def test_contentPaste( self ):
        #
        #   Does copy / paste work?
        #
        from Products.CMFCore.PortalFolder import PortalFolder

        test = self.root.test

        self.root._setObject( 'portal_types', TypesTool() )
        types_tool = self.root.portal_types
        fti = FTIDATA_DUMMY[0].copy()
        types_tool._setObject( 'Dummy Content', FTI(**fti) )

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
        dummy = sub1.dummy

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

        get_transaction().commit(1)
        cookie = sub1.manage_cutObjects( ids = ('dummy',) )
        # Waaa! force sub2 to allow paste of Dummy object.
        sub3.all_meta_types = []
        sub3.all_meta_types.extend(sub3.all_meta_types)
        sub3.all_meta_types.extend( extra_meta_types() )
        sub3.manage_pasteObjects(cookie)

        assert not 'dummy' in sub1.objectIds()
        assert not 'dummy' in sub1.contentIds()
        assert 'dummy' in sub2.objectIds()
        assert 'dummy' in sub2.contentIds()
        assert 'dummy' in sub3.objectIds()
        assert 'dummy' in sub3.contentIds()
        assert not has_path( catalog._catalog, '/test/sub1/dummy' )
        assert has_path( catalog._catalog, '/test/sub2/dummy' )
        assert has_path( catalog._catalog, '/test/sub3/dummy' )

    def test_contentPasteAllowedTypes( self ):
        #
        #   _verifyObjectPaste() should honor allowed content types
        #
        from Products.CMFCore.PortalFolder import PortalFolder

        test = self.root.test

        self.root._setObject( 'portal_types', TypesTool() )
        types_tool = self.root.portal_types

        fti = FTIDATA_DUMMY[0].copy()
        types_tool._setObject( 'Dummy Content', FTI(**fti) )
        types_tool._setObject( 'Folder', FTI(**fti) )

        test._setObject( 'sub1', PortalFolder( 'sub1', '' ) )
        sub1 = test.sub1
        sub1._setObject( 'dummy', DummyContent( 'dummy' ) )

        test._setObject( 'sub2', PortalFolder( 'sub2', '' ) )
        sub2 = test.sub2
        sub2.all_meta_types = extra_meta_types()

        # Allow adding of Dummy Content
        types_tool.Folder.manage_changeProperties(filter_content_types=False)

        # Copy/paste should work fine 
        cookie = sub1.manage_copyObjects( ids = ( 'dummy', ) )
        sub2.manage_pasteObjects( cookie )

        # Disallow adding of Dummy Content
        types_tool.Folder.manage_changeProperties(filter_content_types=True)

        # Now copy/paste should raise a ValueError
        cookie = sub1.manage_copyObjects( ids = ( 'dummy', ) )
        self.assertRaises( ValueError, sub2.manage_pasteObjects, cookie )

    def test_setObjectRaisesBadRequest(self):
        #
        #   _setObject() should raise BadRequest on duplicate id
        #
        test = self.root.test
        test._setObject('foo', DummyContent('foo'))
        self.assertRaises(BadRequest, test._setObject, 'foo', 
                                      DummyContent('foo'))

    def test_checkIdRaisesBadRequest(self):
        #
        #   _checkId() should raise BadRequest on duplicate id
        #
        test = self.root.test
        test._setObject('foo', DummyContent('foo'))
        self.assertRaises(BadRequest, test._checkId, 'foo')

    def test_checkIdAvailableCatchesBadRequest(self):
        #
        #   checkIdAvailable() should catch BadRequest
        #
        test = self.root.test
        test._setObject('foo', DummyContent('foo'))
        self.failIf(test.checkIdAvailable('foo'))


class ContentFilterTests( TestCase ):

    def setUp( self ):
        self.dummy=DummyContent('Dummy')

    def test_empty( self ):

        from Products.CMFCore.PortalFolder import ContentFilter

        cfilter = ContentFilter()
        dummy = self.dummy
        assert cfilter( dummy )
        desc = str( cfilter )
        lines = filter( None, desc.split('; ') )
        assert not lines

    def test_Type( self ):

        from Products.CMFCore.PortalFolder import ContentFilter

        cfilter = ContentFilter( Type='foo' )
        dummy = self.dummy
        assert not cfilter( dummy )
        cfilter = ContentFilter( Type='Dummy Content Title' )
        assert cfilter( dummy )
        desc = str( cfilter )
        lines = desc.split('; ')
        assert len( lines ) == 1
        assert lines[0] == 'Type: Dummy Content Title'

        cfilter = ContentFilter( Type=( 'foo', 'bar' ) )
        dummy = self.dummy
        assert not cfilter( dummy )
        cfilter = ContentFilter( Type=( 'Dummy Content Title',
                                        'something else' ) )
        assert cfilter( dummy )
        desc = str( cfilter )
        lines = desc.split('; ')
        assert len( lines ) == 1
        assert lines[0] == 'Type: Dummy Content Title, something else'

    def test_portal_type( self ):

        from Products.CMFCore.PortalFolder import ContentFilter

        cfilter = ContentFilter( portal_type='some_pt' )
        dummy = self.dummy
        assert not cfilter( dummy )
        dummy.portal_type = 'asdf'
        assert not cfilter( dummy )
        dummy.portal_type = 'some_ptyyy'
        assert not cfilter( dummy )
        dummy.portal_type = 'xxxsome_ptyyy'
        assert not cfilter( dummy )
        dummy.portal_type = 'some_pt'
        assert cfilter( dummy )
        desc = str( cfilter )
        lines = desc.split('; ')
        assert len( lines ) == 1
        assert lines[0] == 'Portal Type: some_pt'

    def test_Title( self ):

        from Products.CMFCore.PortalFolder import ContentFilter

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

        from Products.CMFCore.PortalFolder import ContentFilter

        cfilter = ContentFilter( Creator='moe' )
        dummy = self.dummy
        self.failIf( cfilter(dummy) )
        dummy.creators = ('curly',)
        self.failIf( cfilter(dummy) )
        dummy.creators = ('moe',)
        self.failUnless( cfilter(dummy) )
        dummy.creators = ('moe', 'curly')
        self.failUnless( cfilter(dummy) )
        desc = str( cfilter )
        lines = desc.split('; ')
        self.assertEqual(len( lines ),1)
        self.assertEqual(lines[0],'Creator: moe')

    def test_Description( self ):

        from Products.CMFCore.PortalFolder import ContentFilter

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

        from Products.CMFCore.PortalFolder import ContentFilter

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

        from Products.CMFCore.PortalFolder import ContentFilter

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

        from Products.CMFCore.PortalFolder import ContentFilter

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

        from Products.CMFCore.PortalFolder import ContentFilter

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

        from Products.CMFCore.PortalFolder import ContentFilter

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

        from Products.CMFCore.PortalFolder import ContentFilter

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

        from Products.CMFCore.PortalFolder import ContentFilter

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


#------------------------------------------------------------------------------
#   Tests for security-related CopySupport lifted from the Zope 2.7
#   / head OFS.tests.testCopySupport (see Collector #259).
#------------------------------------------------------------------------------
ADD_IMAGES_AND_FILES = 'Add images and files'
FILE_META_TYPES = ( { 'name'        : 'File'
                    , 'action'      : 'manage_addFile'
                    , 'permission'  : ADD_IMAGES_AND_FILES
                    }
                  ,
                  )
class _SensitiveSecurityPolicy:

    def __init__( self, validate_lambda, checkPermission_lambda ):
        self._lambdas = ( validate_lambda, checkPermission_lambda )

    def validate( self, *args, **kw ):
        return self._lambdas[ 0 ]( *args, **kw )

    def checkPermission( self, *args, **kw ) :
        return self._lambdas[ 1 ]( *args, **kw )

class _AllowedUser( Implicit ):

    def __init__( self, allowed_lambda ):
        self._lambdas = ( allowed_lambda, )

    def getId( self ):
        return 'unit_tester'

    getUserName = getId

    def allowed( self, object, object_roles=None ):
        return self._lambdas[ 0 ]( object, object_roles )

class PortalFolderCopySupportTests( TestCase ):

    _old_policy = None

    def setUp( self ):
        self._scrubSecurity()

    def tearDown( self ):

        self._scrubSecurity()
        self._cleanApp()

    def _initFolders( self ):
        from Products.CMFCore.PortalFolder import PortalFolder

        self.connection = makeConnection()
        try:
            r = self.connection.root()
            a = Application()
            r['Application'] = a
            self.root = a
            responseOut = self.responseOut = cStringIO.StringIO()
            self.app = makerequest( self.root, stdout=responseOut )
            self.app._setObject( 'folder1', PortalFolder( 'folder1' ) )
            self.app._setObject( 'folder2', PortalFolder( 'folder2' ) )
            folder1 = getattr( self.app, 'folder1' )
            folder2 = getattr( self.app, 'folder2' )

            manage_addFile( folder1, 'file'
                          , file='', content_type='text/plain')

            # Hack, we need a _p_mtime for the file, so we make sure that it
            # has one. We use a subtransaction, which means we can rollback
            # later and pretend we didn't touch the ZODB.
            get_transaction().commit()
        except:
            self.connection.close()
            raise
        get_transaction().begin()

        return self.app._getOb( 'folder1' ), self.app._getOb( 'folder2' )

    def _cleanApp( self ):

        get_transaction().abort()
        self.app._p_jar.sync()
        self.connection.close()
        del self.app
        del self.responseOut
        del self.root
        del self.connection

    def _scrubSecurity( self ):

        noSecurityManager()

        if self._old_policy is not None:
            SecurityManager.setSecurityPolicy( self._old_policy )

    def _assertCopyErrorUnauth( self, callable, *args, **kw ):

        import re
        from zExceptions import Unauthorized
        from OFS.CopySupport import CopyError

        ce_regex = kw.get( 'ce_regex' )
        if ce_regex is not None:
            del kw[ 'ce_regex' ]

        try:
            callable( *args, **kw )

        except CopyError, e:

            if ce_regex is not None:
                
                pattern = re.compile( ce_regex, re.DOTALL )
                if pattern.search( e ) is None:
                    self.fail( "Paste failed; didn't match pattern:\n%s" % e )

            else:
                self.fail( "Paste failed; no pattern:\n%s" % e )

        except Unauthorized, e:
            pass

        else:
            self.fail( "Paste allowed unexpectedly." )

    def _initPolicyAndUser( self    
                          , a_lambda=None
                          , v_lambda=None
                          , c_lambda=None
                          ):
        def _promiscuous( *args, **kw ):
            return 1

        if a_lambda is None:
            a_lambda = _promiscuous

        if v_lambda is None:
            v_lambda = _promiscuous

        if c_lambda is None:
            c_lambda = _promiscuous

        scp = _SensitiveSecurityPolicy( v_lambda, c_lambda )
        self._old_policy = SecurityManager.setSecurityPolicy( scp )

        newSecurityManager( None
                          , _AllowedUser( a_lambda ).__of__( self.root ) )

    def test_copy_baseline( self ):

        folder1, folder2 = self._initFolders()
        folder2.all_meta_types = FILE_META_TYPES

        self._initPolicyAndUser()

        self.failUnless( 'file' in folder1.objectIds() )
        self.failIf( 'file' in folder2.objectIds() )

        cookie = folder1.manage_copyObjects( ids=( 'file', ) )
        folder2.manage_pasteObjects( cookie )

        self.failUnless( 'file' in folder1.objectIds() )
        self.failUnless( 'file' in folder2.objectIds() )

    def test_copy_cant_read_source( self ):

        folder1, folder2 = self._initFolders()
        folder2.all_meta_types = FILE_META_TYPES

        a_file = folder1._getOb( 'file' )

        def _validate( a, c, n, v, *args, **kw ):
            return aq_base( v ) is not aq_base( a_file )

        self._initPolicyAndUser( v_lambda=_validate )

        cookie = folder1.manage_copyObjects( ids=( 'file', ) )
        self._assertCopyErrorUnauth( folder2.manage_pasteObjects
                                   , cookie
                                   , ce_regex='Insufficient privileges'
                                   )

    def test_copy_cant_create_target_metatype_not_supported( self ):
        
        from OFS.CopySupport import CopyError

        folder1, folder2 = self._initFolders()
        folder2.all_meta_types = ()

        self._initPolicyAndUser()

        cookie = folder1.manage_copyObjects( ids=( 'file', ) )
        self._assertCopyErrorUnauth( folder2.manage_pasteObjects
                                   , cookie
                                   , ce_regex='Not Supported'
                                   )

    def test_move_baseline( self ):

        folder1, folder2 = self._initFolders()
        folder2.all_meta_types = FILE_META_TYPES

        self.failUnless( 'file' in folder1.objectIds() )
        self.failIf( 'file' in folder2.objectIds() )

        self._initPolicyAndUser()

        cookie = folder1.manage_cutObjects( ids=( 'file', ) )
        folder2.manage_pasteObjects( cookie )

        self.failIf( 'file' in folder1.objectIds() )
        self.failUnless( 'file' in folder2.objectIds() )

    def test_move_cant_read_source( self ):
        
        from OFS.CopySupport import CopyError

        folder1, folder2 = self._initFolders()
        folder2.all_meta_types = FILE_META_TYPES

        a_file = folder1._getOb( 'file' )

        def _validate( a, c, n, v, *args, **kw ):
            return aq_base( v ) is not aq_base( a_file )

        self._initPolicyAndUser( v_lambda=_validate )

        cookie = folder1.manage_cutObjects( ids=( 'file', ) )
        self._assertCopyErrorUnauth( folder2.manage_pasteObjects
                                   , cookie
                                   , ce_regex='Insufficient privileges'
                                   )

    def test_move_cant_create_target_metatype_not_supported( self ):
        
        from OFS.CopySupport import CopyError

        folder1, folder2 = self._initFolders()
        folder2.all_meta_types = ()

        self._initPolicyAndUser()

        cookie = folder1.manage_cutObjects( ids=( 'file', ) )
        self._assertCopyErrorUnauth( folder2.manage_pasteObjects
                                   , cookie
                                   , ce_regex='Not Supported'
                                   )

    def test_move_cant_create_target_metatype_not_allowed( self ):
        
        #
        #   This test can't succeed on Zope's earlier than 2.7.3 because
        #   of the DWIM'y behavior of 'guarded_getattr', which tries to
        #   filter #   acquired-but-inaccessible objects, rather than raising
        #   Unauthorized.
        #
        #   If you are running with such a Zope, this test will error out
        #   with an AttributeError (instead of the expected Unauthorized).
        #
        from OFS.CopySupport import CopyError

        folder1, folder2 = self._initFolders()
        folder2.all_meta_types = FILE_META_TYPES

        def _no_manage_addFile( a, c, n, v, *args, **kw ):
            return n != 'manage_addFile'

        self._initPolicyAndUser( v_lambda=_no_manage_addFile )

        cookie = folder1.manage_cutObjects( ids=( 'file', ) )
        self._assertCopyErrorUnauth( folder2.manage_pasteObjects
                                   , cookie
                                   , ce_regex='Insufficient Privileges'
                                             + '.*%s' % ADD_IMAGES_AND_FILES
                                   )

    def test_move_cant_delete_source( self ):
        
        #
        #   This test fails on Zope's earlier than 2.7.3 because of the
        #   changes required to 'OFS.CopytSupport.manage_pasteObjects'
        #   which must pass 'validate_src' of 2 to '_verifyObjectPaste'
        #   to indicate that the object is being moved, rather than
        #   simply copied.
        #
        #   If you are running with such a Zope, this test will fail,
        #   because the move (which should raise Unauthorized) will be
        #   allowed.
        #
        from AccessControl.Permissions import delete_objects as DeleteObjects
        from OFS.CopySupport import CopyError
        from Products.CMFCore.PortalFolder import PortalFolder
        from Products.CMFCore.permissions import AddPortalFolders

        folder1, folder2 = self._initFolders()
        folder1.manage_permission( DeleteObjects, roles=(), acquire=0 )

        folder1._setObject( 'sub', PortalFolder( 'sub' ) )
        get_transaction().commit() # get a _p_jar for 'sub'

        FOLDER_CTOR = 'manage_addProducts/CMFCore/manage_addPortalFolder'
        folder2.all_meta_types = ( { 'name'        : 'CMF Core Content'
                                   , 'action'      : FOLDER_CTOR
                                   , 'permission'  : AddPortalFolders
                                   }
                                 ,
                                 )

        self.app.portal_types = DummyTypesTool()

        def _no_delete_objects(permission, object, context):
            return permission != DeleteObjects

        self._initPolicyAndUser( c_lambda=_no_delete_objects )

        cookie = folder1.manage_cutObjects( ids=( 'sub', ) )
        self._assertCopyErrorUnauth( folder2.manage_pasteObjects
                                   , cookie
                                   , ce_regex='Insufficient Privileges'
                                             + '.*%s' % DeleteObjects
                                   )

class DummyTypeInfo:

    def allowType( self, portal_type ):
        return True

class DummyTypesTool( Implicit ):

    def getTypeInfo( self, portal_type ):

        return DummyTypeInfo()

def test_suite():
    return TestSuite((
        makeSuite( PortalFolderFactoryTests ),
        makeSuite( PortalFolderTests ),
        makeSuite( ContentFilterTests ),
        makeSuite( PortalFolderCopySupportTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
