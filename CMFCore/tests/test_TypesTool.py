import Zope
import OFS.Folder, OFS.SimpleItem
from unittest import TestCase, TestSuite, makeSuite, main
from Acquisition import Implicit
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl import SecurityManager
from Products.CMFCore.TypesTool import *
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.CMFCorePermissions import AddPortalContent
from Products.CMFCore.CMFCorePermissions import ModifyPortalContent
from Products.CMFCore.PortalFolder import *
from Products.CMFCore import utils
import ZPublisher.HTTPRequest
from Products.PythonScripts.standard import url_quote
from webdav.NullResource import NullResource
from Acquisition import aq_base

class PermissiveSecurityPolicy:
    """
        Stub out the existing security policy for unit testing purposes.
    """
    #
    #   Standard SecurityPolicy interface
    #
    def validate( self
                , accessed=None
                , container=None
                , name=None
                , value=None
                , context=None
                , roles=None
                , *args
                , **kw):
        return 1
    
    def checkPermission( self, permission, object, context) :
        if permission == 'forbidden permission':
            return 0
        return 1

class OmnipotentUser( Implicit ):
    """
        Stubbed out manager for unit testing purposes.
    """
    def getId( self ):
        return 'all_powerful_Oz'
    
    getUserName = getId

    def allowed( self, object, object_roles=None ):
        return 1

class UserWithRoles( Implicit ):
    """
        Stubbed out manager for unit testing purposes.
    """
    def __init__( self, *roles ):
        self._roles = roles

    def getId( self ):
        return 'high_roller'
    
    getUserName = getId

    def allowed( self, object, object_roles=None ):
        for orole in object_roles:
            if orole in self._roles:
                return 1
        return 0

class UnitTestUser( Implicit ):
    """
        Stubbed out manager for unit testing purposes.
    """
    def getId( self ):
        return 'unit_tester'
    
    getUserName = getId

    def has_permission(self, permission, obj):
        # For types tool tests dealing with filtered_meta_types
        return 1

    def allowed( self, object, object_roles=None ):
        # for testing permissions on actions
        if object.getId() == 'actions_dummy':
            if 'Anonymous' in object_roles:
                return 1
            else:
                return 0
        return 1

class DummyMethod:
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return self.name
    def __call__(self):
        return self.name

class DummyContent( PortalContent, OFS.SimpleItem.Item ):
    """
    """
    meta_type = 'Dummy'

def addDummy( self, id ):
    """
    """
    self._setObject( id, DummyContent() )

def extra_meta_types():
    return (  { 'name' : 'Dummy', 'action' : 'manage_addFolder' }, )

class DummyTypeInfo(TypeInformation):
    """ new class of type info object """
    meta_type = "Dummy Test Type Info"

class TypesToolTests( TestCase ):

    def setUp( self ):
        get_transaction().begin()
        self._policy = PermissiveSecurityPolicy()
        self._oldPolicy = SecurityManager.setSecurityPolicy(self._policy)
        self.connection = Zope.DB.open()
        root = self.root = self.connection.root()[ 'Application' ]
        newSecurityManager( None, UnitTestUser().__of__( self.root ) )

        env = { 'SERVER_NAME' : 'http://localhost'
              , 'SERVER_PORT' : '80'
              }
        root.REQUEST = ZPublisher.HTTPRequest.HTTPRequest( None, env, None )
        
        root.addDummy = addDummy

        root._setObject( 'portal_types', TypesTool() )
        tool = root.portal_types
        FTI = FactoryTypeInformation
        tool._setObject( 'Dummy'
                       , FTI( 'Dummy'
                            , meta_type=DummyContent.meta_type
                            , product='CMFDefault'
                            , factory='addDocument'
                            , actions= ( { 'name'          : 'View'
                                           , 'action'        : 'view'
                                           , 'permissions'   : ('View', ) },
                                         { 'name'          : 'View2'
                                           , 'action'        : 'view2'
                                           , 'permissions'   : ('View', ) },
                                         { 'name'          : 'Edit'
                                           , 'action'        : 'edit'
                                           , 'permissions'   : ('forbidden permission',)
                                           }
                                         )
                              )
                         )
    
    def tearDown( self ):
        get_transaction().abort()
        self.connection.close()
        noSecurityManager()
        SecurityManager.setSecurityPolicy(self._oldPolicy)

    def off_test_otherFolderTypes( self ):
        """
            Does 'invokeFactory' work when invoked from non-PortalFolder?
            Currently tests a bug which hasn't been fixed (remove 'off_'
            from name to activate)            
        """
        self.root._setObject( 'portal', PortalFolder( 'portal', '' ) )
        portal = self.root.portal
        portal._setObject( 'normal', OFS.Folder.Folder( 'normal', '' ) )
        normal = portal.normal
        normal.invokeFactory( 'Dummy', 'dummy' )
        assert 'dummy' not in portal.objectIds()
        assert 'dummy' in normal.objectIds()

    def test_processActions( self ):
        """
        Are the correct, permitted methods returned for actions?
        """
        self.root._setObject( 'portal', PortalFolder( 'portal', '' ) )
        portal = self.root.portal
        portal.invokeFactory( 'Dummy', 'actions_dummy' )
        dummy = portal._getOb( 'actions_dummy' )

        # so we can traverse to it:
        dummy.view = DummyMethod("view")
        dummy.view2 = DummyMethod("view2")
        dummy.edit = DummyMethod("edit")

        default_view = dummy()
        custom_view = utils._getViewFor( dummy, view='view2' )()
        unpermitted_view = utils._getViewFor( dummy, view='edit' )()

        self.failUnlessEqual(default_view, 'view')
        self.failUnlessEqual(custom_view, 'view2')
        self.failIf(unpermitted_view == 'edit')
        self.failUnlessEqual(unpermitted_view, 'view')

    def test_AddingOtherTypeInfos(self):
        addTypeFactory(DummyTypeInfo)
        tool = self.root.portal_types
        type_type = DummyTypeInfo.meta_type

        fmt = [ mt['name'] for mt in tool.filtered_meta_types() ]
        self.failUnless(DummyTypeInfo.meta_type in fmt,
                        "Subfactory meta type not registered")

        atif = tool.manage_addTypeInfoForm(self.root.REQUEST,
                                           type_type=type_type)
        self.failUnless(atif.find(type_type) > -1,
                        "'%s' not found in type info form" % type_type)

        tool.manage_addTypeInformation(id='foo_default', type_type=None)
        fd = tool.foo_default
        self.failUnless(isinstance(fd, FactoryTypeInformation))
        self.failIf(isinstance(fd, DummyTypeInfo))

        tool.manage_addTypeInformation(id='foo_sub', type_type=type_type)
        fs = tool.foo_sub
        self.failUnless(isinstance(fs, DummyTypeInfo), fs.__class__)

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
        self.failUnless(meta_types.has_key('Dummy Test Type Info'))
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
        return apply( FactoryTypeInformation, ( id, ), kw )

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
        return apply( ScriptableTypeInformation, ( id, ), kw )

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


class Foo:
    """
        Shim content object.
    """
    def __init__( self, id, *args, **kw ):
        self.id = id
        self._args = args
        self._kw = {}
        self._kw.update( kw )

class FauxFactory:
    """
        Shim product factory.
    """
    def __init__( self, folder ):
        self._folder = folder

    def addFoo( self, id, *args, **kw ):
        if self._folder._prefix:
            id = '%s_%s' % ( self._folder._prefix, id )
        foo = apply( Foo, ( id, ) + args, kw )
        self._folder._setOb( id, foo )
        if self._folder._prefix:
            return id

    __roles__ = ( 'FooAdder', )
    __allow_access_to_unprotected_subobjects__ = { 'addFoo' : 1 }

class FauxFolder( Implicit ):
    """
        Shim container
    """
    def __init__( self, fake_product=0, prefix='' ):
        self._prefix = prefix

        if fake_product:
            self.manage_addProduct = { 'FooProduct' : FauxFactory( self ) }

        self._objects = {}

    def _setOb( self, id, obj ):
        self._objects[id] = obj

    def _getOb( self, id ):
        return self._objects[id]

class FTIConstructionTests( TestCase ):

    def setUp( self ):
        noSecurityManager()

    def _makeInstance( self, id, **kw ):
        return apply( FactoryTypeInformation, ( id, ), kw )

    def _makeFolder( self, fake_product=0 ):
        return FauxFolder( fake_product )

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

        ti = FactoryTypeInformation( 'Foo'
                                   , product='FooProduct'
                                   , factory='addFoo'
                                   )
        folder = FauxFolder( fake_product=1, prefix=prefix )
        
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

def run():
    main(defaultTest='test_suite')

if __name__ == '__main__':
    run()
