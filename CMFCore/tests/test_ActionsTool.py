from unittest import TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()
from Interface.Verify import verifyClass

from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.ActionsTool import ActionsTool
from Products.CMFCore.Expression import Expression
from Products.CMFCore.MembershipTool import MembershipTool
from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.RegistrationTool import RegistrationTool
from Products.CMFCore.tests.base.testcase import SecurityRequestTest
from Products.CMFCore.TypesTool import TypesTool
from Products.CMFCore.URLTool import URLTool


class ActionsToolTests( SecurityRequestTest ):

    def setUp( self ):

        SecurityRequestTest.setUp(self)

        root = self.root
        root._setObject( 'portal_actions', ActionsTool() )
        root._setObject( 'portal_url', URLTool() )
        root._setObject( 'foo', URLTool() )
        root._setObject('portal_membership', MembershipTool())
        root._setObject('portal_types', TypesTool())
        self.tool = root.portal_actions
        self.tool.action_providers = ('portal_actions',)

    def test_actionProviders(self):
        tool = self.tool
        self.assertEqual(tool.listActionProviders(), ('portal_actions',))

    def test_addActionProvider(self):
        tool = self.tool
        tool.addActionProvider('foo')
        self.assertEqual(tool.listActionProviders(),
                          ('portal_actions', 'foo'))
        tool.addActionProvider('portal_url')
        tool.addActionProvider('foo')
        self.assertEqual(tool.listActionProviders(),
                          ('portal_actions', 'foo', 'portal_url'))

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
        self.tool.action_providers = ('portal_actions',)
        self.assertEqual(tool.listFilteredActionsFor(root.portal_registration),
                         {'workflow': [],
                          'user': [],
                          'object': [],
                          'folder': [{'permissions': ('List folder contents',),
                                      'id': 'folderContents',
                                      'url': 'http://foo/folder_contents',
                                      'title': 'Folder contents',
                                      'name': 'Folder contents',
                                      'visible': True,
                                      'available': True,
                                      'allowed': True,
                                      'category': 'folder'}],
                          'global': []})

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_actions \
                import portal_actions as IActionsTool
        from Products.CMFCore.interfaces.portal_actions \
                import ActionProvider as IActionProvider

        verifyClass(IActionsTool, ActionsTool)
        verifyClass(IActionProvider, ActionsTool)


def test_suite():
    return TestSuite((
        makeSuite(ActionsToolTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
