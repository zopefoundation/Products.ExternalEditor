import Zope, unittest, OFS.SimpleItem, Acquisition
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl import SecurityManager
from Products.CMFCore.ActionsTool import *
from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.Expression import Expression, createExprContext
import ZPublisher.HTTPRequest

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

class DummyMembershipTool:
    def __init__(self, anon=1):
        self.anon = anon 

    def isAnonymousUser(self):
        return self.anon 

    def getAuthenticatedMember(self):
        return "member"
  
class DummyContent(PortalContent, OFS.SimpleItem.Item):
    """
    """
    meta_type = 'Dummy'
    url = 'foo_url'

    def __init__(self, id, url=None):
       self.id = id
       self.url = url

    def absolute_url(self):
       return self.url

class ExpressionTests( unittest.TestCase ):

    def setUp( self ):
        get_transaction().begin()
        self._policy = PermissiveSecurityPolicy()
        self._oldPolicy = SecurityManager.setSecurityPolicy(self._policy)
        self.connection = Zope.DB.open()
        root = self.root = self.connection.root()[ 'Application' ]
        newSecurityManager(None, UnitTestUser().__of__( self.root ))
        root._setObject('portal', DummyContent('portal', 'url_portal'))
        portal = self.portal = self.root.portal
        self.folder = DummyContent('foo', 'url_foo')
        self.object = DummyContent('bar', 'url_bar')
        self.ai = ActionInformation(id='view'
                                  , title='View'
                                  , action=Expression(
                  text='view')
                                  , condition=Expression(
                  text='member')
                                  , category='global'
                                  , visible=1)

    def test_anonymous_ec(self):
        self.portal.portal_membership = DummyMembershipTool()
        ec = createExprContext(self.folder, self.portal, self.object)
        member = ec.global_vars['member']
        self.failIf(member)


    def test_authenticatedUser_ec(self):
        self.portal.portal_membership = DummyMembershipTool(anon=0)
        ec = createExprContext(self.folder, self.portal, self.object)
        member = ec.global_vars['member']
        self.assertEqual(member, 'member')

    def test_ec_context(self):
        self.portal.portal_membership = DummyMembershipTool()
        ec = createExprContext(self.folder, self.portal, self.object)
        object = ec.global_vars['object']
        portal = ec.global_vars['portal']
        folder = ec.global_vars['folder']
        self.failUnless(object)
        self.assertEqual(object.id, 'bar')
        self.assertEqual(object.absolute_url(), 'url_bar')
        self.failUnless(portal)
        self.assertEqual(portal.id, 'portal')
        self.assertEqual(portal.absolute_url(), 'url_portal')
        self.failUnless(folder)
        self.assertEqual(folder.id, 'foo')
        self.assertEqual(folder.absolute_url(), 'url_foo')
        


    def tearDown( self ):
        get_transaction().abort()
        self.connection.close()
        noSecurityManager()
        SecurityManager.setSecurityPolicy(self._oldPolicy)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ExpressionTests))
    return suite

def run():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    run()
