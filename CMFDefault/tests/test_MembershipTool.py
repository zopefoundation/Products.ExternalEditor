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
from AccessControl.SecurityManagement import newSecurityManager

from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.tests.base.dummy import DummyFolder as DummyFolderBase
from Products.CMFCore.tests.base.dummy import DummyTool
from Products.CMFCore.tests.base.dummy import DummyUserFolder
from Products.CMFCore.tests.base.testcase import SecurityTest

from Products.CMFDefault.MembershipTool import MembershipTool


class DummyFolder(DummyFolderBase):
    def manage_addPortalFolder(self, id, title=''):
        self._setObject( id, DummyFolder() )
    def changeOwnership(self, user):
        pass
    def manage_setLocalRoles(self, userid, roles):
        pass
    def getPhysicalRoot(self):
        return self
    def unrestrictedTraverse(self, path, default=None, restricted=0):
        return self.acl_users

class MembershipToolTests(TestCase):

    def setUp(self):
        self.site = DummyFolder()
        self.mtool = MembershipTool().__of__(self.site)

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


class MembershipToolSecurityTests(SecurityTest):

    def setUp(self):
        SecurityTest.setUp(self)
        self.site = DummyFolder()
        self.site.id = 'testSite'
        self.mtool = MembershipTool().__of__(self.site)

    def test_createMemberarea(self):
        mtool = self.mtool
        members = self.site._setObject( 'Members', PortalFolder('Members') )
        acl_users = self.site._setObject( 'acl_users', DummyUserFolder() )
        wtool = self.site._setObject( 'portal_workflow', DummyTool() )

        # permission
        mtool.createMemberarea('user_foo')
        self.failIf( hasattr(members.aq_self, 'user_foo') )
        newSecurityManager(None, acl_users.user_bar)
        mtool.createMemberarea('user_foo')
        self.failIf( hasattr(members.aq_self, 'user_foo') )
        newSecurityManager(None, acl_users.user_foo)
        mtool.setMemberareaCreationFlag()
        mtool.createMemberarea('user_foo')
        self.failIf( hasattr(members.aq_self, 'user_foo') )
        mtool.setMemberareaCreationFlag()
        mtool.createMemberarea('user_foo')
        self.failUnless( hasattr(members.aq_self, 'user_foo') )

        # default content
        f = members.user_foo
        ownership = acl_users.user_foo
        localroles = ( ( 'user_foo', ('Owner',) ), )
        self.assertEqual( f.Title(), "user_foo's Home" )
        self.assertEqual( f.getOwner(), ownership )
        self.assertEqual( f.get_local_roles(), localroles,
                          'CMF Collector issue #162 (LocalRoles broken): %s'
                          % str( f.get_local_roles() ) )
        self.assertEqual( f.index_html.getOwner(), ownership,
                          'CMF Collector issue #162 (Ownership broken): %s'
                          % str( f.index_html.getOwner() ) )
        self.assertEqual( f.index_html.get_local_roles(), localroles,
                          'CMF Collector issue #162 (LocalRoles broken): %s'
                          % str( f.index_html.get_local_roles() ) )
        self.assertEqual( wtool.test_notified, f.index_html )

        # acquisition
        self.site.user_bar = 'test attribute'
        newSecurityManager(None, acl_users.user_bar)
        mtool.createMemberarea('user_bar')
        self.failUnless( hasattr(members.aq_self, 'user_bar'),
                         'CMF Collector issue #102 (acquisition bug)' )


def test_suite():
    return TestSuite((
        makeSuite( MembershipToolTests ),
        makeSuite( MembershipToolSecurityTests )
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
