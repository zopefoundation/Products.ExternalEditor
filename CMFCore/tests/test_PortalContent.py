from unittest import TestCase, TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()
from Interface.Verify import verifyClass

from Acquisition import aq_base
from Products.CMFCore.tests.base.testcase import RequestTest
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.User import UnrestrictedUser
from Products.CMFCore.PortalContent import PortalContent


class PortalContentTests(TestCase):

    def test_interface(self):
        from Products.CMFCore.interfaces.Dynamic \
                import DynamicType as IDynamicType
        from Products.CMFCore.interfaces.Contentish \
                import Contentish as IContentish

        verifyClass(IDynamicType, PortalContent)
        verifyClass(IContentish, PortalContent)

class TestContentCopyPaste(RequestTest):

    # Tests related to http://www.zope.org/Collectors/CMF/205
    # Copy/pasting a content item must set ownership to pasting user

    def setUp(self):
        RequestTest.setUp(self)
        try:
            newSecurityManager(None, UnrestrictedUser('manager', '', ['Manager'], []))
            self.root.manage_addProduct['CMFDefault'].manage_addCMFSite('cmf')
            self.site = self.root.cmf
            get_transaction().commit(1) # Make sure we have _p_jars
        except:
            self.tearDown()
            raise

    def tearDown(self):
        noSecurityManager()
        RequestTest.tearDown(self)

    def test_CopyPasteSetsOwnership(self):
        # Copy/pasting a File should set new ownership including local roles

        # First, add two users to the user folder, a member and a manager
        # and create a member area for the member
        uf = self.site.acl_users
        uf._doAddUser('member', 'secret', ['Member'], [])
        uf._doAddUser('manager1', 'secret', ['Manager'], [])
        member = uf.getUser('member').__of__(uf)
        manager1 = uf.getUser('manager1').__of__(uf)
        self.site.portal_membership.createMemberArea('member')
        member_area = self.site.Members.member


        # Switch to the manager user context and plant a content item into 
        # the member user's member area
        newSecurityManager(None, manager1)
        member_area.invokeFactory('File', id='test_file')
        self.site.portal_workflow.doActionFor(member_area.test_file, 'publish')

        # Switch to "member" context now and try to copy and paste the 
        # content item created by "manager1"
        newSecurityManager(None, member)
        cb = member_area.manage_copyObjects(['test_file'])
        member_area.manage_pasteObjects(cb)

        # Now test executable ownership and "owner" local role
        # "member" should have both.
        file_ob = member_area.copy_of_test_file
        self.assertEqual(aq_base(file_ob.getOwner()), aq_base(member))
        self.assert_('Owner' in file_ob.get_local_roles_for_userid('member'))


def test_suite():
    return TestSuite((
        makeSuite( PortalContentTests ),
        makeSuite( TestContentCopyPaste),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
