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

from Products.CMFCore.MemberDataTool import MemberDataTool
from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.dummy import DummyTool
from Products.CMFCore.tests.base.dummy import DummyUserFolder
from Products.CMFCore.tests.base.testcase import SecurityTest

from Products.CMFCore.MembershipTool import MembershipTool


class MembershipToolTests(TestCase):

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_membership \
                import portal_membership as IMembershipTool
        from Products.CMFCore.interfaces.portal_actions \
                import ActionProvider as IActionProvider

        verifyClass(IMembershipTool, MembershipTool)
        verifyClass(IActionProvider, MembershipTool)


class MembershipToolSecurityTests(SecurityTest):

    def setUp(self):
        SecurityTest.setUp(self)
        self.site = DummySite('site').__of__(self.root)
        self.mtool = MembershipTool().__of__(self.site)

    def test_getCandidateLocalRoles(self):
        mtool = self.mtool
        acl_users = self.site._setObject( 'acl_users', DummyUserFolder() )

        newSecurityManager(None, acl_users.user_foo)
        rval = mtool.getCandidateLocalRoles(mtool)
        self.assertEqual( rval, ('Dummy',) )
        newSecurityManager(None, acl_users.all_powerful_Oz)
        rval = mtool.getCandidateLocalRoles(mtool)
        self.assertEqual( rval, ('Manager', 'Member', 'Owner', 'Reviewer') )

    def test_createMemberArea(self):
        mtool = self.mtool
        members = self.site._setObject( 'Members', PortalFolder('Members') )
        acl_users = self.site._setObject( 'acl_users', DummyUserFolder() )
        wtool = self.site._setObject( 'portal_workflow', DummyTool() )

        # permission
        mtool.createMemberArea('user_foo')
        self.failIf( hasattr(members.aq_self, 'user_foo') )
        newSecurityManager(None, acl_users.user_bar)
        mtool.createMemberArea('user_foo')
        self.failIf( hasattr(members.aq_self, 'user_foo') )
        newSecurityManager(None, acl_users.user_foo)
        mtool.setMemberareaCreationFlag()
        mtool.createMemberArea('user_foo')
        self.failIf( hasattr(members.aq_self, 'user_foo') )
        newSecurityManager(None, acl_users.all_powerful_Oz)
        mtool.setMemberareaCreationFlag()
        mtool.createMemberArea('user_foo')
        self.failUnless( hasattr(members.aq_self, 'user_foo') )

        # default content
        f = members.user_foo
        ownership = acl_users.user_foo
        localroles = ( ( 'user_foo', ('Owner',) ), )
        self.assertEqual( f.getOwner(), ownership )
        self.assertEqual( f.get_local_roles(), localroles,
                          'CMF Collector issue #162 (LocalRoles broken): %s'
                          % str( f.get_local_roles() ) )

    def test_deleteMembers(self):
        mtool = self.mtool
        members = self.site._setObject( 'Members', PortalFolder('Members') )
        acl_users = self.site._setObject( 'acl_users', DummyUserFolder() )
        utool = self.site._setObject( 'portal_url', DummyTool() )
        wtool = self.site._setObject( 'portal_workflow', DummyTool() )
        mdtool = self.site._setObject( 'portal_memberdata', MemberDataTool() )
        newSecurityManager(None, acl_users.all_powerful_Oz)

        self.assertEqual( acl_users.getUserById('user_foo'),
                          acl_users.user_foo )
        mtool.createMemberArea('user_foo')
        self.failUnless( hasattr(members.aq_self, 'user_foo') )
        mdtool.registerMemberData('Dummy', 'user_foo')
        self.failUnless( mdtool._members.has_key('user_foo') )

        rval = mtool.deleteMembers( ('user_foo', 'user_baz') )
        self.assertEqual( rval, ('user_foo',) )
        self.failIf( acl_users.getUserById('user_foo', None) )
        self.failIf( mdtool._members.has_key('user_foo') )
        self.failIf( hasattr(members.aq_self, 'user_foo') )

def test_suite():
    return TestSuite((
        makeSuite( MembershipToolTests ),
        makeSuite( MembershipToolSecurityTests )
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
