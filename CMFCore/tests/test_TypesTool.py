import Zope
from unittest import TestCase, TestSuite, makeSuite, main

from Products.CMFCore.TypesTool import\
     FactoryTypeInformation as FTI,\
     ScriptableTypeInformation as STI,\
     TypesTool,Unauthorized

from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.utils import _getViewFor

from Products.CMFCore.tests.base.testcase import \
     SecurityRequestTest
from Products.CMFCore.tests.base.security import \
     OmnipotentUser, UserWithRoles
from Products.CMFCore.tests.base.dummy import \
     DummyObject, addDummy, DummyTypeInfo,\
     DummyFolder, DummyFTI

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager

from Products.PythonScripts.standard import url_quote
from webdav.NullResource import NullResource
from Acquisition import aq_base

class TypesToolTests( SecurityRequestTest ):

    def setUp( self ):
        SecurityRequestTest.setUp(self)
        root = self.root
        root.addDummy = addDummy

        root._setObject( 'portal_types', TypesTool() )
        tool = root.portal_types
        tool._setObject( 'Dummy', DummyFTI ) 
    
    def test_processActions( self ):
        """
        Are the correct, permitted methods returned for actions?
        """
        self.root._setObject( 'portal', PortalFolder( 'portal', '' ) )
        portal = self.root.portal
        portal.invokeFactory( 'Dummy', 'actions_dummy' )
        dummy = portal._getOb( 'actions_dummy' )

        # so we can traverse to it:
        dummy.view = DummyObject("view")
        dummy.view2 = DummyObject("view2")
        dummy.edit = DummyObject("edit")

        default_view = dummy()
        custom_view = _getViewFor( dummy, view='view2' )()
        unpermitted_view = _getViewFor( dummy, view='edit' )()

        self.failUnlessEqual(default_view, 'view')
        self.failUnlessEqual(custom_view, 'view2')
        self.failIf(unpermitted_view == 'edit')
        self.failUnlessEqual(unpermitted_view, 'view')

    def test_allMetaTypes(self):
        """
        Test that everything returned by allMetaTypes can be
        traversed to.
        """
        tool = self.root.portal_types
        meta_types={}
        # Seems we get NullResource if the method couldn't be traverse to
        # so we check for that. If we've got it, something is b0rked.
        for factype in tool.all_meta_types():
            meta_types[factype['name']]=1
            # The url_quote below is necessary 'cos of the one in
            # main.dtml. Could be removed once that is gone.
            self.failIf(type(aq_base(tool.unrestrictedTraverse(url_quote(factype['action'])))) is NullResource)

        # Check the ones we're expecting are there
        self.failUnless(meta_types.has_key('Scriptable Type Information'))
        self.failUnless(meta_types.has_key('Factory-based Type Information'))

class TypeInfoTests( TestCase ):
    
    def test_construction( self ):
        ti = self._makeInstance( 'Foo'
                               , description='Description'
                               , meta_type='Foo'
                               , icon='foo.gif'
                               )
        self.assertEqual( ti.getId(), 'Foo' )
        self.assertEqual( ti.Type(), 'Foo' )
        self.assertEqual( ti.Description(), 'Description' )
        self.assertEqual( ti.Metatype(), 'Foo' )
        self.assertEqual( ti.getIcon(), 'foo.gif' )
        self.assertEqual( ti.immediate_view, '' )

        ti = self._makeInstance( 'Foo'
                               , immediate_view='foo_view'
                               )
        self.assertEqual( ti.immediate_view, 'foo_view' )

    def _makeAndSetInstance( self,id,**kw ):
        tool = self.tool
        t = apply( self._makeInstance, (id,), kw )
        tool._setObject(id,t)
        return tool[id]
              
    def test_allowType( self ):
        self.tool = TypesTool()        
        ti = self._makeAndSetInstance( 'Foo' )
        self.failIf( ti.allowType( 'Foo' ) )
        self.failIf( ti.allowType( 'Bar' ) )

        ti = self._makeAndSetInstance( 'Foo2', allowed_content_types=( 'Bar', ) )
        self.failUnless( ti.allowType( 'Bar' ) )

        ti = self._makeAndSetInstance( 'Foo3', filter_content_types=0 )
        self.failUnless( ti.allowType( 'Foo3' ) )

    
    def test_GlobalHide( self ):
        self.tool = TypesTool()        
        tnf = self._makeAndSetInstance( 'Folder', filter_content_types=0)
        taf = self._makeAndSetInstance( 'Allowing Folder',
                                  allowed_content_types=('Hidden','Not Hidden'))
        tih = self._makeAndSetInstance( 'Hidden'     ,global_allow=0)
        tnh = self._makeAndSetInstance( 'Not Hidden')
        # make sure we're normally hidden but everything else is visible
        self.failIf     ( tnf.allowType( 'Hidden' ) )
        self.failUnless ( tnf.allowType( 'Not Hidden') )
        # make sure we're available where we should be
        self.failUnless ( taf.allowType( 'Hidden' ) )
        self.failUnless ( taf.allowType( 'Not Hidden') )
        # make sure we're available in a non-content-type-filtered type
        # where we have been explicitly allowed
        taf2 = self._makeAndSetInstance( 'Allowing Folder2',
                                   allowed_content_types=('Hidden','Not Hidden'),
                                   filter_content_types=0)
        self.failUnless ( taf2.allowType( 'Hidden' ) )
        self.failUnless ( taf2.allowType( 'Not Hidden') )
        

    def test_allowDiscussion( self ):
        ti = self._makeInstance( 'Foo' )
        self.failIf( ti.allowDiscussion() )

        ti = self._makeInstance( 'Foo', allow_discussion=1 )
        self.failUnless( ti.allowDiscussion() )

    ACTION_LIST = \
    ( { 'id'            : 'view'
      , 'name'          : 'View'
      , 'action'        : 'foo_view'
      , 'permissions'   : ( 'View', )
      , 'category'      : 'object'
      , 'visible'       : 1
      }
    , { 'name'          : 'Edit'                # Note: No ID passed
      , 'action'        : 'foo_edit'
      , 'permissions'   : ( 'Modify', )
      , 'category'      : 'object'
      , 'visible'       : 1
      }
    , { 'name'          : 'Object Properties'   # Note: No ID passed
      , 'action'        : 'foo_properties'
      , 'permissions'   : ( 'Modify', )
      , 'category'      : 'object'
      , 'visible'       : 1
      }
    , { 'id'            : 'slot'
      , 'action'        : 'foo_slot'
      , 'category'      : 'object'
      , 'visible'       : 0
      }
    )

    def _ripActionValues( self, key, actions ):
        return filter( None, map( lambda x, key=key: x.get( key, None )
                                , actions
                                ) )

    def test_listActions( self ):
        ti = self._makeInstance( 'Foo' )
        self.failIf( ti.getActions() )

        ti = self._makeInstance( 'Foo', actions=self.ACTION_LIST )

        actions = ti.getActions()
        self.failUnless( actions )

        ids = self._ripActionValues( 'id', actions )
        self.failUnless( 'view' in ids )
        self.failUnless( 'edit' in ids )
        self.failUnless( 'objectproperties' in ids )
        self.failUnless( 'slot' in ids )

        names = self._ripActionValues( 'name', actions )
        self.failUnless( 'View' in names )
        self.failUnless( 'Edit' in names )
        self.failUnless( 'Object Properties' in names )
        self.failIf( 'slot' in names )
        self.failIf( 'Slot' in names )
        
        visible = filter( None, map( lambda x:
                                        x.get( 'visible', 0 ) and x['id']
                                   , actions ) )
        self.failUnless( 'view' in visible )
        self.failUnless( 'edit' in visible )
        self.failUnless( 'objectproperties' in visible )
        self.failIf( 'slot' in visible )

    def test_getActionById( self ):

        ti = self._makeInstance( 'Foo' )
        marker = []
        self.assertEqual( id( ti.getActionById( 'view', marker ) )
                        , id( marker ) )
        self.assertRaises( TypeError, ti.getActionById, 'view' )

        ti = self._makeInstance( 'Foo', actions=self.ACTION_LIST )
        self.assertEqual( id( ti.getActionById( 'foo', marker ) )
                        , id( marker ) )
        self.assertRaises( TypeError, ti.getActionById, 'foo' )
        
        action = ti.getActionById( 'view' )
        self.assertEqual( action, 'foo_view' )
        
        action = ti.getActionById( 'edit' )
        self.assertEqual( action, 'foo_edit' )
        
        action = ti.getActionById( 'objectproperties' )
        self.assertEqual( action, 'foo_properties' )
        
        action = ti.getActionById( 'slot' )
        self.assertEqual( action, 'foo_slot' )
        

class FTIDataTests( TypeInfoTests ):

    def _makeInstance( self, id, **kw ):
        return apply( FTI, ( id, ), kw )

    def test_properties( self ):
        ti = self._makeInstance( 'Foo' )
        self.assertEqual( ti.product, '' )
        self.assertEqual( ti.factory, '' )

        ti = self._makeInstance( 'Foo'
                               , product='FooProduct'
                               , factory='addFoo'
                               )
        self.assertEqual( ti.product, 'FooProduct' )
        self.assertEqual( ti.factory, 'addFoo' )


class STIDataTests( TypeInfoTests ):

    def _makeInstance( self, id, **kw ):
        return apply( STI, ( id, ), kw )

    def test_properties( self ):
        ti = self._makeInstance( 'Foo' )
        self.assertEqual( ti.permission, '' )
        self.assertEqual( ti.constructor_path, '' )

        ti = self._makeInstance( 'Foo'
                               , permission='Add Foos'
                               , constructor_path='foo_add'
                               )
        self.assertEqual( ti.permission, 'Add Foos' )
        self.assertEqual( ti.constructor_path, 'foo_add' )

class FTIConstructionTests( TestCase ):

    def setUp( self ):
        noSecurityManager()

    def _makeInstance( self, id, **kw ):
        return apply( FTI, ( id, ), kw )

    def _makeFolder( self, fake_product=0 ):
        return DummyFolder( fake_product )

    def test_isConstructionAllowed_wo_Container( self ):

        ti = self._makeInstance( 'foo' )

        self.failIf( ti.isConstructionAllowed( None ) )
        self.failIf( ti.isConstructionAllowed( None, raise_exc=1 ) )

        ti = self._makeInstance( 'Foo'
                               , product='FooProduct'
                               , factory='addFoo'
                               )

        self.failIf( ti.isConstructionAllowed( None ) )
        self.assertRaises( Exception, ti.isConstructionAllowed
                         , None, raise_exc=1 )

    def test_isConstructionAllowed_wo_ProductFactory( self ):

        ti = self._makeInstance( 'foo' )

        folder = self._makeFolder()
        self.failIf( ti.isConstructionAllowed( folder ) )
        self.failIf( ti.isConstructionAllowed( folder, raise_exc=1 ) )

        folder = self._makeFolder( fake_product=1 )
        self.failIf( ti.isConstructionAllowed( folder ) )
        self.failIf( ti.isConstructionAllowed( folder, raise_exc=1 ) )

    def test_isConstructionAllowed_wo_Security( self ):

        ti = self._makeInstance( 'Foo'
                               , product='FooProduct'
                               , factory='addFoo'
                               )
        folder = self._makeFolder( fake_product=1 )

        self.failIf( ti.isConstructionAllowed( folder ) )
        self.assertRaises( Unauthorized, ti.isConstructionAllowed
                         , folder, raise_exc=1 )

class FTIConstructionTests_w_Roles( TestCase ):

    def tearDown( self ):
        noSecurityManager()

    def _makeStuff( self, prefix='' ):

        ti = FTI( 'Foo'
                  , product='FooProduct'
                  , factory='addFoo'
                  )
        folder = DummyFolder( fake_product=1,prefix=prefix )
        
        return ti, folder

    def test_isConstructionAllowed_for_Omnipotent( self ):

        ti, folder = self._makeStuff()
        newSecurityManager( None
                          , OmnipotentUser().__of__( folder ) )
        self.failUnless( ti.isConstructionAllowed( folder ) )

    def test_isConstructionAllowed_w_Role( self ):

        ti, folder = self._makeStuff()

        newSecurityManager( None
                          , UserWithRoles( 'FooAdder' ).__of__( folder ) )
        self.failUnless( ti.isConstructionAllowed( folder ) )

    def test_isConstructionAllowed_wo_Role( self ):

        ti, folder = self._makeStuff()

        newSecurityManager( None
                          , UserWithRoles( 'FooViewer' ).__of__( folder ) )
        self.assertRaises( Unauthorized, ti.isConstructionAllowed
                         , folder, raise_exc=1 )

    def test_constructInstance_wo_Roles( self ):

        ti, folder = self._makeStuff()

        newSecurityManager( None
                          , UserWithRoles( 'FooViewer' ).__of__( folder ) )

        self.assertRaises( Unauthorized
                         , ti.constructInstance, folder, 'foo' )

    def test_constructInstance( self ):

        ti, folder = self._makeStuff()

        newSecurityManager( None
                          , UserWithRoles( 'FooAdder' ).__of__( folder ) )

        ti.constructInstance( folder, 'foo' )
        foo = folder._getOb( 'foo' )
        self.assertEqual( foo.id, 'foo' )

    def test_constructInstance_w_args_kw( self ):

        ti, folder = self._makeStuff()

        newSecurityManager( None
                          , UserWithRoles( 'FooAdder' ).__of__( folder ) )

        ti.constructInstance( folder, 'bar', 0, 1 )
        bar = folder._getOb( 'bar' )
        self.assertEqual( bar.id, 'bar' )
        self.assertEqual( bar._args, ( 0, 1 ) )

        ti.constructInstance( folder, 'baz', frickle='natz' )
        baz = folder._getOb( 'baz' )
        self.assertEqual( baz.id, 'baz' )
        self.assertEqual( baz._kw[ 'frickle' ], 'natz' )

        ti.constructInstance( folder, 'bam', 0, 1, frickle='natz' )
        bam = folder._getOb( 'bam' )
        self.assertEqual( bam.id, 'bam' )
        self.assertEqual( bam._args, ( 0, 1 ) )
        self.assertEqual( bam._kw[ 'frickle' ], 'natz' )

    def test_constructInstance_w_id_munge( self ):

        ti, folder = self._makeStuff( 'majyk' )

        newSecurityManager( None
                          , UserWithRoles( 'FooAdder' ).__of__( folder ) )

        ti.constructInstance( folder, 'dust' )
        majyk_dust = folder._getOb( 'majyk_dust' )
        self.assertEqual( majyk_dust.id, 'majyk_dust' )


def test_suite():
    return TestSuite((
        makeSuite(TypesToolTests),
        makeSuite(FTIDataTests),
        makeSuite(STIDataTests),
        makeSuite(FTIConstructionTests),
        makeSuite(FTIConstructionTests_w_Roles),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
