from unittest import TestCase, TestSuite, makeSuite, main

import Zope
try:
    Zope.startup()
except AttributeError:
    # for Zope versions before 2.6.1
    pass
try:
    from Interface.Verify import verifyClass
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import verify_class_implementation as verifyClass

from AccessControl import Unauthorized
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.SecurityManager import setSecurityPolicy
from Acquisition import aq_base
from webdav.NullResource import NullResource
from Products.PythonScripts.PythonScript import PythonScript
from Products.PythonScripts.standard import url_quote

from Products.CMFCore.TypesTool import FactoryTypeInformation as FTI
from Products.CMFCore.TypesTool import ScriptableTypeInformation as STI
from Products.CMFCore.TypesTool import TypesTool
from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.utils import _getViewFor

from Products.CMFCore.tests.base.security import OmnipotentUser
from Products.CMFCore.tests.base.security import UserWithRoles
from Products.CMFCore.tests.base.dummy import DummyFactory
from Products.CMFCore.tests.base.dummy import DummyFolder
from Products.CMFCore.tests.base.dummy import DummyObject
from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.dummy import DummyUserFolder
from Products.CMFCore.tests.base.tidata import FTIDATA_ACTIONS
from Products.CMFCore.tests.base.tidata import FTIDATA_CMF14
from Products.CMFCore.tests.base.tidata import FTIDATA_CMF14_FOLDER
from Products.CMFCore.tests.base.tidata import FTIDATA_CMF14_SPECIAL
from Products.CMFCore.tests.base.tidata import FTIDATA_CMF15
from Products.CMFCore.tests.base.tidata import FTIDATA_DUMMY
from Products.CMFCore.tests.base.tidata import STI_SCRIPT
from Products.CMFCore.tests.base.testcase import SecurityTest


class TypesToolTests(SecurityTest):

    def setUp( self ):
        SecurityTest.setUp(self)
        self.site = DummySite('site').__of__(self.root)
        self.acl_users = self.site._setObject( 'acl_users', DummyUserFolder() )
        self.ttool = self.site._setObject( 'portal_types', TypesTool() )
        fti = FTIDATA_DUMMY[0].copy()
        del fti['id']
        self.ttool._setObject( 'Dummy Content', apply( FTI, ('Dummy Content',), fti) )
 
    def test_processActions( self ):
        """
        Are the correct, permitted methods returned for actions?
        """
        site = self.site
        portal = site._setObject( 'portal', PortalFolder(id='portal') )
        portal.manage_addProduct = { 'FooProduct' : DummyFactory(portal) }
        portal.invokeFactory( 'Dummy Content', 'actions_dummy' )
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
        tool = self.ttool
        meta_types={}
        # Seems we get NullResource if the method couldn't be traverse to
        # so we check for that. If we've got it, something is b0rked.
        for factype in tool.all_meta_types():
            meta_types[factype['name']]=1
            # The url_quote below is necessary 'cos of the one in
            # main.dtml. Could be removed once that is gone.
            act = tool.unrestrictedTraverse(url_quote(factype['action']))
            self.failIf(type(aq_base(act)) is NullResource)

        # Check the ones we're expecting are there
        self.failUnless(meta_types.has_key('Scriptable Type Information'))
        self.failUnless(meta_types.has_key('Factory-based Type Information'))

    def test_constructContent(self):
        site = self.site
        acl_users = self.acl_users
        ttool = self.ttool
        setSecurityPolicy(self._oldPolicy)
        newSecurityManager(None, acl_users.all_powerful_Oz)
        self.site._owner = (['acl_users'], 'all_powerful_Oz')
        sti_baz = STI('Baz',
                      permission='Add portal content',
                      constructor_path='addBaz')
        ttool._setObject('Baz', sti_baz)
        ttool._setObject( 'addBaz',  PythonScript('addBaz') )
        s = ttool.addBaz
        s.write(STI_SCRIPT)

        f = site._setObject( 'folder', PortalFolder(id='folder') )
        f.manage_addProduct = { 'FooProduct' : DummyFactory(f) }
        f._owner = (['acl_users'], 'user_foo')
        self.assertEqual( f.getOwner(), acl_users.user_foo )

        ttool.constructContent('Dummy Content', container=f, id='page1')
        try:
            ttool.constructContent('Baz', container=f, id='page2')
        except Unauthorized:
            self.fail('CMF Collector issue #165 (Ownership bug): '
                      'Unauthorized raised' )

def test_interface(self):
        from Products.CMFCore.interfaces.portal_types \
                import portal_types as ITypesTool
        from Products.CMFCore.interfaces.portal_actions \
                import ActionProvider as IActionProvider

        verifyClass(ITypesTool, TypesTool)
        verifyClass(IActionProvider, TypesTool)


class TypeInfoTests(TestCase):
    
    def test_construction( self ):
        ti = self._makeInstance( 'Foo'
                               , description='Description'
                               , meta_type='Foo'
                               , icon='foo.gif'
                               )
        self.assertEqual( ti.getId(), 'Foo' )
        self.assertEqual( ti.Title(), 'Foo' )
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
        taf = self._makeAndSetInstance( 'Allowing Folder'
                                      , allowed_content_types=( 'Hidden'
                                                              ,'Not Hidden'))
        tih = self._makeAndSetInstance( 'Hidden', global_allow=0)
        tnh = self._makeAndSetInstance( 'Not Hidden')
        # make sure we're normally hidden but everything else is visible
        self.failIf     ( tnf.allowType( 'Hidden' ) )
        self.failUnless ( tnf.allowType( 'Not Hidden') )
        # make sure we're available where we should be
        self.failUnless ( taf.allowType( 'Hidden' ) )
        self.failUnless ( taf.allowType( 'Not Hidden') )
        # make sure we're available in a non-content-type-filtered type
        # where we have been explicitly allowed
        taf2 = self._makeAndSetInstance( 'Allowing Folder2'
                                       , allowed_content_types=( 'Hidden'
                                                               , 'Not Hidden'
                                                               )
                                       , filter_content_types=0
                                       )
        self.failUnless ( taf2.allowType( 'Hidden' ) )
        self.failUnless ( taf2.allowType( 'Not Hidden') )
        

    def test_allowDiscussion( self ):
        ti = self._makeInstance( 'Foo' )
        self.failIf( ti.allowDiscussion() )

        ti = self._makeInstance( 'Foo', allow_discussion=1 )
        self.failUnless( ti.allowDiscussion() )

    def test_listActions( self ):
        ti = self._makeInstance( 'Foo' )
        self.failIf( ti.listActions() )

        ti = self._makeInstanceByFTIData(FTIDATA_ACTIONS)
        actions = ti.listActions()
        self.failUnless( actions )

        ids = [ x.getId() for x in actions ]
        self.failUnless( 'view' in ids )
        self.failUnless( 'edit' in ids )
        self.failUnless( 'objectproperties' in ids )
        self.failUnless( 'slot' in ids )

        names = [ x.Title() for x in actions ]
        self.failUnless( 'View' in names )
        self.failUnless( 'Edit' in names )
        self.failUnless( 'Object Properties' in names )
        self.failIf( 'slot' in names )
        self.failUnless( 'Slot' in names )
        
        visible = [ x.getId() for x in actions if x.getVisibility() ]
        self.failUnless( 'view' in visible )
        self.failUnless( 'edit' in visible )
        self.failUnless( 'objectproperties' in visible )
        self.failIf( 'slot' in visible )

    def test_getActionById( self ):

        ti = self._makeInstance( 'Foo' )
        marker = []
        self.assertEqual( id( ti.getActionById( 'view', marker ) )
                        , id( marker ) )
        self.assertRaises( ValueError, ti.getActionById, 'view' )

        ti = self._makeInstanceByFTIData(FTIDATA_ACTIONS)
        self.assertEqual( id( ti.getActionById( 'foo', marker ) )
                        , id( marker ) )
        self.assertRaises( ValueError, ti.getActionById, 'foo' )
        
        action = ti.getActionById( 'view' )
        self.assertEqual( action, '' )
        
        action = ti.getActionById( 'edit' )
        self.assertEqual( action, 'foo_edit' )
        
        action = ti.getActionById( 'objectproperties' )
        self.assertEqual( action, 'foo_properties' )
        
        action = ti.getActionById( 'slot' )
        self.assertEqual( action, 'foo_slot' )

    def test__convertActions_from_dict( self ):

        from Products.CMFCore.ActionInformation import ActionInformation

        ti = self._makeInstance( 'Foo' )
        ti._actions = ( { 'id' : 'bar'
                        , 'name' : 'Bar'
                        , 'action' : 'bar_action'
                        , 'permissions' : ( 'Bar permission', )
                        , 'category' : 'baz'
                        , 'visible' : 0
                        }
                      ,
                      )

        actions = ti.listActions()
        self.assertEqual( len( actions ), 1 )

        action = actions[0]

        self.failUnless( isinstance( action, ActionInformation ) )
        self.assertEqual( action.getId(), 'bar' )
        self.assertEqual( action.Title(), 'Bar' )
        self.assertEqual( action.getActionExpression(),
                          'string:${object_url}/bar_action' )
        self.assertEqual( action.getCondition(), '' )
        self.assertEqual( action.getPermissions(), ( 'Bar permission', ) )
        self.assertEqual( action.getCategory(), 'baz' )
        self.assertEqual( action.getVisibility(), 0 )

        self.failUnless( isinstance( ti._actions[0], ActionInformation ) )

    def test_MethodAliases_methods(self):
        ti = self._makeInstanceByFTIData(FTIDATA_CMF15)
        self.assertEqual( ti.getMethodAliases(), FTIDATA_CMF15[0]['aliases'] )
        self.assertEqual( ti.getMethodPath('view'), ('dummy_view',) )
        self.assertEqual( ti.getMethodPath('view.html'), ('dummy_view',) )
        self.assertEqual( ti.getMethodURL('view'), 'dummy_view' )
        self.assertEqual( ti.getMethodURL('view.html'), 'dummy_view' )

        ti.setMethodAliases( ti.getMethodAliases() )
        self.assertEqual( ti.getMethodAliases(), FTIDATA_CMF15[0]['aliases'] )

    def test_MethodAliases_content_migration(self):
        wanted = { 'view':('dummy_view',),
                   '(Default)':('dummy_view',) }

        # use old FTI Data
        ti = self._makeInstanceByFTIData(FTIDATA_CMF14)
        self.assertEqual(ti._aliases, wanted)

        # simulate old FTI
        del ti._aliases
        self.failIf( hasattr(ti, '_aliases') )

        # migrate FTI
        ti.getMethodPath('view')
        self.assertEqual(ti._aliases, wanted)

    def test_MethodAliases_folder_migration(self):
        wanted = { 'view':('(Default)',), }

        # use old FTI Data
        ti = self._makeInstanceByFTIData(FTIDATA_CMF14_FOLDER)
        self.assertEqual(ti._aliases, wanted)

        # simulate old FTI
        del ti._aliases
        self.failIf( hasattr(ti, '_aliases') )

        # migrate FTI
        ti.getMethodPath('view')
        self.assertEqual(ti._aliases, wanted)

    def test_MethodAliases_special_migration(self):
        wanted = { 'view':('dummy_view',), 'mkdir':('dummy_mkdir',) }

        # use old FTI Data
        ti = self._makeInstanceByFTIData(FTIDATA_CMF14_SPECIAL)
        self.assertEqual(ti._aliases, wanted)

        # simulate old FTI
        del ti._aliases
        self.failIf( hasattr(ti, '_aliases') )

        # migrate FTI
        ti.getMethodPath('view')
        self.assertEqual(ti._aliases, wanted)


class FTIDataTests( TypeInfoTests ):

    def _makeInstance( self, id, **kw ):
        return apply( FTI, ( id, ), kw )

    def _makeInstanceByFTIData(self, ftidata):
        fti = ftidata[0].copy()
        id = fti['id']
        del fti['id']
        return apply( FTI, ( id, ), fti )

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

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_types \
                import ContentTypeInformation as ITypeInformation

        verifyClass(ITypeInformation, FTI)
        

class STIDataTests( TypeInfoTests ):

    def _makeInstance( self, id, **kw ):
        return apply( STI, ( id, ), kw )

    def _makeInstanceByFTIData(self, ftidata):
        fti = ftidata[0].copy()
        id = fti['id']
        del fti['id']
        return apply( STI, ( id, ), fti )

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

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_types \
                import ContentTypeInformation as ITypeInformation

        verifyClass(ITypeInformation, STI)
        

class FTIConstructionTests(TestCase):

    def setUp( self ):
        noSecurityManager()

    def _makeInstance( self, id, **kw ):
        return apply( FTI, ( id, ), kw )

    def _makeFolder( self, fake_product=0 ):
        return DummyFolder( fake_product )

    def test_isConstructionAllowed_wo_Container( self ):

        ti = self._makeInstance( 'foo' )

        self.failIf( ti.isConstructionAllowed( None ) )

        ti = self._makeInstance( 'Foo'
                               , product='FooProduct'
                               , factory='addFoo'
                               )

        self.failIf( ti.isConstructionAllowed( None ) )

    def test_isConstructionAllowed_wo_ProductFactory( self ):

        ti = self._makeInstance( 'foo' )

        folder = self._makeFolder()
        self.failIf( ti.isConstructionAllowed( folder ) )

        folder = self._makeFolder( fake_product=1 )
        self.failIf( ti.isConstructionAllowed( folder ) )

    def test_isConstructionAllowed_wo_Security( self ):

        ti = self._makeInstance( 'Foo'
                               , product='FooProduct'
                               , factory='addFoo'
                               )
        folder = self._makeFolder( fake_product=1 )

        self.failIf( ti.isConstructionAllowed( folder ) )

class FTIConstructionTests_w_Roles(TestCase):

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
