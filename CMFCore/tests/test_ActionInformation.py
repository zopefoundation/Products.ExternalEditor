import Zope
from unittest import TestSuite, makeSuite, main

from Products.CMFCore.tests.base.testcase import \
     TransactionalTest

from Products.CMFCore.tests.base.dummy import \
     DummyContent, DummyTool as DummyMembershipTool

from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.Expression import Expression, createExprContext

class ActionInformationTests(TransactionalTest):
    
    def setUp( self ):

        TransactionalTest.setUp( self )

        root = self.root
        root._setObject('portal', DummyContent('portal', 'url_portal'))
        portal = self.portal = root.portal
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
        
def test_suite():
    return TestSuite((
        makeSuite(ActionInformationTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
