import Zope, OFS.SimpleItem, unittest
from Products.CMFDefault.MembershipTool import *
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.Expression import Expression, createExprContext

class DummyMembershipTool:
    def isAnonymousUser(self):
        return 1
  
class DummyContent(PortalContent, OFS.SimpleItem.Item):
    """
    """
    meta_type = 'Dummy'
    url = 'foo_url'

    def __init__(self, id, url=None):
       self.url = url

    def absolute_url(self):
       return self.url

class ActionInformationTests(unittest.TestCase):
    
    def setUp( self ):
        get_transaction().begin()
        self.connection = Zope.DB.open()
        root = self.root = self.connection.root()[ 'Application' ]
        root._setObject('portal', DummyContent('portal', 'url_portal'))
        portal = self.portal = self.root.portal
        portal.portal_membership = DummyMembershipTool()
        self.folder = DummyContent('foo', 'url_foo')
        self.object = DummyContent('bar', 'url_bar')

    def test_basic_construction(self):
        ai = ActionInformation(id='view'
                              )
        self.assertEqual(ai.getId(), 'view')
        self.assertEqual(ai.Title(), 'view')
        self.assertEqual(ai.Description(), '')
        self.assertEqual(ai.getCondition(), '')
        self.assertEqual(ai.getActionExpression(), '')
        self.assertEqual(ai.getVisibility(), 1)
        self.assertEqual(ai.getCategory(), 'object')
        self.assertEqual(ai.getPermissions(), ())

    def test_construction_with_Expressions(self):
        ai = ActionInformation(id='view'
                             , title='View'
                             , action=Expression(
             text='view')
                             , condition=Expression(
             text='member')
                             , category='global'
                             , visible=0)
        self.assertEqual(ai.getId(), 'view')
        self.assertEqual(ai.Title(), 'View')
        self.assertEqual(ai.Description(), '')
        self.assertEqual(ai.getCondition(), 'member')
        self.assertEqual(ai.getActionExpression(), 'view')
        self.assertEqual(ai.getVisibility(), 0)
        self.assertEqual(ai.getCategory(), 'global')
        self.assertEqual(ai.getPermissions(), ())
    
    def test_Condition(self):
        portal = self.portal 
        folder = self.folder
        object = self.object 
        ai = ActionInformation(id='view'
                             , title='View'
                             , action=Expression(
             text='view')
                             , condition=Expression(
             text='member')
                             , category='global'
                             , visible=1)
        ec = createExprContext(folder, portal, object)
        self.failIf(ai.testCondition(ec))
        
    def tearDown( self ):
        get_transaction().abort()
        self.connection.close()
        

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ActionInformationTests))
    return suite

def run():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    run()
