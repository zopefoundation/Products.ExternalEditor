import Zope
import unittest
import OFS.Folder, OFS.SimpleItem
import Acquisition
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl import SecurityManager
from Products.CMFCore.TypesTool import *
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.CMFCorePermissions import AddPortalContent
from Products.CMFCore.CMFCorePermissions import ModifyPortalContent
from Products.CMFCore.PortalFolder import *
from Products.CMFCore import utils
import ZPublisher.HTTPRequest

class UnitTestSecurityPolicy:
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

class UnitTestUser( Acquisition.Implicit ):
    """
        Stubbed out manager for unit testing purposes.
    """
    def getId( self ):
        return 'unit_tester'
    
    getUserName = getId

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

class TypesToolTests( unittest.TestCase ):

    def setUp( self ):
        get_transaction().begin()
        self._policy = UnitTestSecurityPolicy()
        SecurityManager.setSecurityPolicy(self._policy)
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

        assert default_view == 'view'
        assert custom_view == 'view2'
        assert unpermitted_view != 'edit'
        assert unpermitted_view == 'view'

class TypeInfoTests( unittest.TestCase ):
    
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

    def test_allowType( self ):
        ti = self._makeInstance( 'Foo' )
        self.failIf( ti.allowType( 'Foo' ) )
        self.failIf( ti.allowType( 'Bar' ) )

        ti = self._makeInstance( 'Foo', allowed_content_types=( 'Bar', ) )
        self.failUnless( ti.allowType( 'Bar' ) )

        ti = self._makeInstance( 'Foo', filter_content_types=0 )
        self.failUnless( ti.allowType( 'Foo' ) )

    def test_allowDiscussion( self ):
        ti = self._makeInstance( 'Foo' )
        self.failIf( ti.allowDiscussion() )

        ti = self._makeInstance( 'Foo', allow_discussion=1 )
        self.failUnless( ti.allowDiscussion() )

    def _ripActionValues( self, key, actions ):
        return filter( None, map( lambda x, key=key: x.get( key, None )
                                , actions
                                ) )

    def testActions( self ):
        ti = self._makeInstance( 'Foo' )
        self.failIf( ti.getActions() )

        action_list = \
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

        ti = self._makeInstance( 'Foo', actions=action_list )

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

class FTITests( TypeInfoTests ):

    def _makeInstance( self, id, **kw ):
        return apply( FactoryTypeInformation, ( id, ), kw )

    def test_ConstructInstance( self ):
        pass

class STITests( TypeInfoTests ):

    def _makeInstance( self, id, **kw ):
        return apply( ScriptableTypeInformation, ( id, ), kw )

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite( TypesToolTests ) )
    suite.addTest( unittest.makeSuite( FTITests ) )
    suite.addTest( unittest.makeSuite( STITests ) )
    return suite

def run():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    run()
