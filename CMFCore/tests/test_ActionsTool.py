import Zope
from unittest import TestCase,TestSuite,makeSuite,main
from Products.CMFCore.ActionsTool import ActionsTool
from Products.CMFCore.TypesTool import TypesTool
from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFDefault.URLTool import URLTool
from Products.CMFDefault.RegistrationTool import RegistrationTool
from Products.CMFDefault.MembershipTool import MembershipTool
from AccessControl import SecurityManager
from AccessControl.SecurityManagement import newSecurityManager
import ZPublisher.HTTPRequest
from Testing.makerequest import makerequest
from Acquisition import Implicit

class UnitTestUser( Implicit ):
    """
        Stubbed out manager for unit testing purposes.
    """
    id = 'unit_tester'
    
    def getId( self ):
        return self.id
    
    getUserName = getId

    def allowed( self, object, object_roles=None ):
        return 1

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
        return 1

class ActionsToolTests( TestCase ):

    def setUp( self ):
        get_transaction().begin()
        self._policy = UnitTestSecurityPolicy()
        self._oldPolicy = SecurityManager.setSecurityPolicy(self._policy)
        self.connection = Zope.DB.open()
        self.root = root = self.connection.root()[ 'Application' ]
        newSecurityManager( None, UnitTestUser().__of__( self.root ) )
        
        root = self.root = makerequest(root)
        
        root._setObject( 'portal_actions', ActionsTool() )
        root._setObject('foo', URLTool() )
        self.tool = root.portal_actions
        self.ut = root.foo
        self.tool.action_providers = ('portal_actions',)


    def tearDown(self):
        SecurityManager.setSecurityPolicy( self._oldPolicy )
        get_transaction().abort()
        self.connection.close()
        
    def test_actionProviders(self):
        tool = self.tool
        self.assertEqual(tool.listActionProviders(), ('portal_actions',))

    def test_addActionProvider(self):
        tool = self.tool
        tool.addActionProvider('foo')
        self.assertEqual(tool.listActionProviders(),
                          ('portal_actions', 'foo'))

    def test_delActionProvider(self):
        tool = self.tool
        tool.deleteActionProvider('foo')
        self.assertEqual(tool.listActionProviders(),
                          ('portal_actions',))

    def test_listActionInformationActions(self):
        """
        Check that listFilteredActionsFor works for objects
        that return ActionInformation objects
        """
        root = self.root
        tool = self.tool
        root._setObject('portal_registration', RegistrationTool())
        root._setObject('portal_membership', MembershipTool())
        root._setObject('portal_types', TypesTool())
        self.tool.action_providers = ('portal_actions','portal_registration')
        self.assertEqual(tool.listFilteredActionsFor(root.portal_registration),
                         {'workflow': [],
                          'user': [],
                          'object': [{'permissions': ('List folder contents',),
                                      'id': 'folderContents',
                                      'url': ' http://foo/folder_contents',
                                      'name': 'Folder contents',
                                      'visible': 1,
                                      'category': 'object'}],
                          'folder': [],
                          'global': []})
        
    def test_listDictionaryActions(self):
        """
        Check that listFilteredActionsFor works for objects
        that return dictionaries
        """
        root = self.root
        tool = self.tool
        root._setObject('donkey', PortalFolder('donkey'))
        root._setObject('portal_membership', MembershipTool())
        root._setObject('portal_types', TypesTool())
        self.assertEqual(tool.listFilteredActionsFor(root.donkey),
                         {'workflow': [],
                          'user': [],
                          'object': [],
                          'folder': [{'permissions': ('List folder contents',),
                                      'id': 'folderContents',
                                      'url': ' http://foo/donkey/folder_contents',
                                      'name': 'Folder contents',
                                      'visible': 1,
                                      'category': 'folder'}],
                          'global': []})

def test_suite():
    return TestSuite((
        makeSuite(ActionsToolTests),
        ))

def run():
    main(defaultTest='test_suite')

if __name__ == '__main__':
    run()
