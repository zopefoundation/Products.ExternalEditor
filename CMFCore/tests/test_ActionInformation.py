from unittest import TestCase, TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()
from Interface.Verify import verifyClass

from Products.PythonScripts.PythonScript import manage_addPythonScript

from Products.CMFCore.Expression import createExprContext
from Products.CMFCore.Expression import Expression
from Products.CMFCore.tests.base.dummy import DummyContent
from Products.CMFCore.tests.base.dummy import DummyTool as DummyMembershipTool
from Products.CMFCore.tests.base.testcase import TransactionalTest


class ActionInfoTests(TestCase):

    def _makeOne(self, *args, **kw):
        from Products.CMFCore.ActionInformation import ActionInfo

        return ActionInfo(*args, **kw)

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_actions \
                import ActionInfo as IActionInfo
        from Products.CMFCore.ActionInformation import ActionInfo

        verifyClass(IActionInfo, ActionInfo)

    def test_create_from_ActionInformation(self):
        from Products.CMFCore.ActionInformation import ActionInformation

        wanted =  {'allowed': True, 'available': True, 'category': 'object',
                   'id': 'foo', 'name': 'foo', 'permissions': (),
                   'title': 'foo', 'url': '', 'visible': True}

        action = ActionInformation(id='foo')
        ec = None
        ai = self._makeOne(action, ec)

        self.assertEqual( ai['id'], wanted['id'] )
        self.assertEqual( ai['title'], wanted['title'] )
        self.assertEqual( ai['url'], wanted['url'] )
        self.assertEqual( ai['permissions'], wanted['permissions'] )
        self.assertEqual( ai['category'], wanted['category'] )
        self.assertEqual( ai['visible'], wanted['visible'] )
        self.assertEqual( ai['available'], wanted['available'] )
        self.assertEqual( ai['allowed'], wanted['allowed'] )
        self.assertEqual( ai, wanted )

    def test_create_from_dict(self):
        wanted =  {'allowed': True, 'available': True, 'category': 'object',
                   'id': 'foo', 'name': 'foo', 'permissions': (),
                   'title': 'foo', 'url': '', 'visible': True}

        action = {'name': 'foo', 'url': ''}
        ec = None
        ai = self._makeOne(action, ec)

        self.assertEqual( ai['id'], wanted['id'] )
        self.assertEqual( ai['title'], wanted['title'] )
        self.assertEqual( ai['url'], wanted['url'] )
        self.assertEqual( ai['permissions'], wanted['permissions'] )
        self.assertEqual( ai['category'], wanted['category'] )
        self.assertEqual( ai['visible'], wanted['visible'] )
        self.assertEqual( ai['available'], wanted['available'] )
        self.assertEqual( ai['allowed'], wanted['allowed'] )
        self.assertEqual( ai, wanted )


class ActionInformationTests(TransactionalTest):

    def setUp( self ):

        TransactionalTest.setUp( self )

        root = self.root
        root._setObject('portal', DummyContent('portal', 'url_portal'))
        portal = self.portal = root.portal
        portal.portal_membership = DummyMembershipTool()
        self.folder = DummyContent('foo', 'url_foo')
        self.object = DummyContent('bar', 'url_bar')

    def _makeOne(self, *args, **kw):
        from Products.CMFCore.ActionInformation import ActionInformation

        return ActionInformation(*args, **kw)

    def test_basic_construction(self):
        ai = self._makeOne(id='view')

        self.assertEqual(ai.getId(), 'view')
        self.assertEqual(ai.Title(), 'view')
        self.assertEqual(ai.Description(), '')
        self.assertEqual(ai.getCondition(), '')
        self.assertEqual(ai.getActionExpression(), '')
        self.assertEqual(ai.getVisibility(), 1)
        self.assertEqual(ai.getCategory(), 'object')
        self.assertEqual(ai.getPermissions(), ())
        
    def test_editing(self):
        ai = self._makeOne(id='view', category='folder')
        ai.edit(id='new_id', title='blah')

        self.assertEqual(ai.getId(), 'new_id')
        self.assertEqual(ai.Title(), 'blah')
        self.assertEqual(ai.Description(), '')
        self.assertEqual(ai.getCondition(), '')
        self.assertEqual(ai.getActionExpression(), '')
        self.assertEqual(ai.getVisibility(), 1)
        self.assertEqual(ai.getCategory(), 'folder')
        self.assertEqual(ai.getPermissions(), ())

    def test_construction_with_Expressions(self):
        ai = self._makeOne( id='view',
                            title='View',
                            action=Expression(text='view'),
                            condition=Expression(text='member'),
                            category='global',
                            visible=False )

        self.assertEqual(ai.getId(), 'view')
        self.assertEqual(ai.Title(), 'View')
        self.assertEqual(ai.Description(), '')
        self.assertEqual(ai.getCondition(), 'member')
        self.assertEqual(ai.getActionExpression(), 'string:${object_url}/view')
        self.assertEqual(ai.getVisibility(), 0)
        self.assertEqual(ai.getCategory(), 'global')
        self.assertEqual(ai.getPermissions(), ())

    def test_Condition(self):
        portal = self.portal
        folder = self.folder
        object = self.object
        ai = self._makeOne( id='view',
                            title='View',
                            action=Expression(text='view'),
                            condition=Expression(text='member'),
                            category='global',
                            visible=True )
        ec = createExprContext(folder, portal, object)

        self.failIf(ai.testCondition(ec))

    def test_Condition_PathExpression(self):
        portal = self.portal
        folder = self.folder
        object = self.object
        manage_addPythonScript(self.root, 'test_script')
        script = self.root.test_script
        script.ZPythonScript_edit('', 'return context.getId()')
        ai = self._makeOne( id='view',
                            title='View',
                            action=Expression(text='view'),
                            condition=Expression(text='portal/test_script'),
                            category='global',
                            visible=True )
        ec = createExprContext(folder, portal, object)

        self.failUnless(ai.testCondition(ec))



def test_suite():
    return TestSuite((
        makeSuite(ActionInfoTests),
        makeSuite(ActionInformationTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
