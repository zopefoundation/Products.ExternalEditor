from unittest import TestCase, TestSuite, makeSuite, main

import Zope
try:
    from Interface.Verify import verifyClass
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import verify_class_implementation as verifyClass

from Products.CMFCore.tests.base.dummy import DummyFolder as DummyFolderBase
from Products.CMFCore.tests.base.dummy import DummyObject

from Products.CMFDefault.MembershipTool import MembershipTool


class DummyFolder(DummyFolderBase):
    def manage_addPortalFolder(self, id, title=''):
        self._setObject( id, DummyFolder() )
    def changeOwnership(self, user):
        pass
    def manage_setLocalRoles(self, userid, roles):
        pass

class DummyUserFolder(DummyFolderBase):
    def getUsers(self):
        pass
    def getUser(self, name):
        return DummyObject()

class DummyWorkflowTool:
    def notifyCreated(self, ob):
        pass


class MembershipToolTests(TestCase):

    def setUp(self):
        self.site = DummyFolder()
        self.mtool = MembershipTool().__of__(self.site)

    def test_createMemberarea(self):
        mtool = self.mtool
        self.site._setObject( 'Members', DummyFolder() )
        self.site._setObject( 'acl_users', DummyUserFolder() )
        self.site._setObject( 'portal_workflow', DummyWorkflowTool() )
        self.site.bar = 'test attribute'
        mtool.createMemberarea('foo')
        self.failUnless( hasattr(self.site.Members.aq_self, 'foo') )
        mtool.createMemberarea('bar')
        self.failUnless( hasattr(self.site.Members.aq_self, 'bar'),
                         'CMF Collector issue #102'  )


    def test_MembersFolder_methods(self):
        mtool = self.mtool
        self.assertEqual( mtool.getMembersFolder(), None )
        self.site._setObject( 'Members', DummyFolder() )
        self.assertEqual( mtool.getMembersFolder(), self.site.Members )
        mtool.setMembersFolderById(id='foo')
        self.assertEqual( mtool.getMembersFolder(), None )
        self.site._setObject( 'foo', DummyFolder() )
        self.assertEqual( mtool.getMembersFolder(), self.site.foo )
        mtool.setMembersFolderById()
        self.assertEqual( mtool.getMembersFolder(), None )

    def test_interface(self):
        from Products.CMFDefault.interfaces.portal_membership \
                import portal_membership as IMembershipTool
        from Products.CMFCore.interfaces.portal_actions \
                import ActionProvider as IActionProvider

        verifyClass(IMembershipTool, MembershipTool)
        verifyClass(IActionProvider, MembershipTool)


def test_suite():
    return TestSuite((
        makeSuite( MembershipToolTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
