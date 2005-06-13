##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Unit tests for PortalContent module.

$Id$
"""

from unittest import TestCase, TestSuite, makeSuite, main
import Testing
try:
    import Zope2
except ImportError:
    # BBB: for Zope 2.7
    import Zope as Zope2
Zope2.startup()

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.User import UnrestrictedUser
from Acquisition import aq_base
try:
    import transaction
except ImportError:
    # BBB: for Zope 2.7
    from Products.CMFCore.utils import transaction

from Products.CMFCore.tests.base.testcase import RequestTest
from Products.CMFDefault.Portal import PortalGenerator


class PortalContentTests(TestCase):

    def test_z2interfaces(self):
        from Interface.Verify import verifyClass
        from Products.CMFCore.interfaces.Contentish \
                import Contentish as IContentish
        from Products.CMFCore.interfaces.Dynamic \
                import DynamicType as IDynamicType
        from Products.CMFCore.PortalContent import PortalContent

        verifyClass(IContentish, PortalContent)
        verifyClass(IDynamicType, PortalContent)

    def test_z3interfaces(self):
        try:
            from zope.interface.verify import verifyClass
        except ImportError:
            # BBB: for Zope 2.7
            return
        from Products.CMFCore.interfaces import IContentish
        from Products.CMFCore.interfaces import IDynamicType
        from Products.CMFCore.PortalContent import PortalContent

        verifyClass(IContentish, PortalContent)
        verifyClass(IDynamicType, PortalContent)


class TestContentCopyPaste(RequestTest):

    # Tests related to http://www.zope.org/Collectors/CMF/205
    # Copy/pasting a content item must set ownership to pasting user

    def setUp(self):
        RequestTest.setUp(self)
        try:
            newSecurityManager(None, UnrestrictedUser('manager', '', ['Manager'], []))
            site_generator = PortalGenerator()
            site_generator.create(self.root, 'cmf', 1)
            self.site = self.root.cmf
            transaction.commit(1) # Make sure we have _p_jars
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
        makeSuite(PortalContentTests),
        makeSuite(TestContentCopyPaste),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
