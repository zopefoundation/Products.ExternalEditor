import Zope
from unittest import TestCase,TestSuite,makeSuite,main

from Products.CMFCore.tests.base.testcase import \
     SecurityRequestTest

from Products.CMFCore.ActionsTool import ActionsTool
from Products.CMFCore.TypesTool import TypesTool
from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.Expression import Expression
from Products.CMFDefault.URLTool import URLTool
from Products.CMFDefault.RegistrationTool import RegistrationTool
from Products.CMFDefault.MembershipTool import MembershipTool

class ActionsToolTests( SecurityRequestTest ):

    def setUp( self ):
        
        SecurityRequestTest.setUp(self)
        
        root = self.root
        root._setObject( 'portal_actions', ActionsTool() )
        root._setObject('foo', URLTool() )
        root._setObject('portal_membership', MembershipTool())
        root._setObject('portal_types', TypesTool())
        self.tool = root.portal_actions
        self.ut = root.foo
        self.tool.action_providers = ('portal_actions',)

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

    def test_DuplicateActions(self):
        """
        Check that listFilteredActionsFor
        filters out duplicate actions.
        """
        root = self.root
        tool = self.tool
        action = ActionInformation(id='test',
                                   title='Test',
                                   action=Expression(
                                          text='string: a_url'
                                          ),
                                   condition='',
                                   permissions=(),
                                   category='object',
                                   visible=1
                                   )
        tool._actions = [action,action]
        self.tool.action_providers = ('portal_actions',)
        self.assertEqual(tool.listFilteredActionsFor(root)['object'],
                          [{'permissions': (),
                            'id': 'test',
                            'url': ' a_url',
                            'name': 'Test',
                            'visible': 1,
                            'category': 'object'}])

def test_suite():
    return TestSuite((
        makeSuite(ActionsToolTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
