##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Unit tests for the versions tool.

$Id$
"""

import unittest

import Testing
import Zope
Zope.startup()

from Acquisition import aq_base
from OFS.Folder import Folder
from AccessControl.User import SimpleUser
from AccessControl.SecurityManagement \
     import newSecurityManager, noSecurityManager
from Products.ZopeVersionControl.Utility import VersionControlError
from Products.CMFStaging.VersionsTool import VersionsTool
from Products.CMFStaging.tests.testLockTool import TestUser


class Tests(unittest.TestCase):

    def setUp(self):
        app = Zope.app()
        self.app = app
        if hasattr(app, 'testroot'):
            app._delObject('testroot')
        app.manage_addProduct['OFSP'].manage_addFolder('testroot')
        self.root = app.testroot
        zvc = self.root.manage_addProduct['ZopeVersionControl']
        zvc.addRepository('VersionRepository')

        setattr(self.root, VersionsTool.id, VersionsTool())
        self.tool = getattr(self.root, VersionsTool.id)
        self.root.content = Folder()
        self.root.content.id = 'content'

        user = TestUser('sally')
        newSecurityManager(None, user.__of__(self.root.acl_users))


    def tearDown(self):
        app = self.app
        if hasattr(app, 'testroot'):
            app._delObject('testroot')
        self.app._p_jar.close()
        noSecurityManager()


    def testCheckinCheckout(self):
        vt = self.tool
        content = self.root.content
        vt.checkin(content)
        self.assert_(not vt.isCheckedOut(content))
        vt.checkout(content)
        self.assert_(vt.isCheckedOut(content))


    def testGetVersionId(self):
        vt = self.tool
        content = self.root.content
        self.assertEqual(vt.getVersionId(content), '')
        vt.checkin(content)
        old_id = vt.getVersionId(content)
        self.assertNotEqual(old_id, '')
        vt.checkout(content)
        vt.checkin(content)
        new_id = vt.getVersionId(content)
        self.assertNotEqual(new_id, '')
        self.assertNotEqual(old_id, new_id)


    def testRevertToVersion(self):
        vt = self.tool
        content = self.root.content
        vt.checkin(content)
        old_id = vt.getVersionId(content)
        vt.checkout(content)
        vt.checkin(content)
        new_id = vt.getVersionId(content)
        self.assertNotEqual(new_id, old_id)
        vt.revertToVersion(content, old_id)
        content = self.root.content  # XXX ZopeVersionControl requires this
        current_id = vt.getVersionId(content)
        self.assertNotEqual(new_id, current_id)
        self.assertEqual(old_id, current_id)


    def testRevertToStickyThenCheckout(self):
        # Test that the versions tool automatically unsticks objects
        vt = self.tool
        content = self.root.content
        vt.checkin(content)
        old_id = vt.getVersionId(content)
        vt.checkout(content)
        vt.checkin(content)
        new_id = vt.getVersionId(content)
        vt.revertToVersion(content, old_id)
        content = self.root.content  # XXX ZopeVersionControl requires this

        vt.auto_copy_forward = 0
        # Can't check out when the object is in the current state
        # but there's a sticky tag.
        vt.revertToVersion(content, new_id)
        self.assertRaises(VersionControlError, vt.checkout, content)
        
        vt.auto_copy_forward = 1
        vt.revertToVersion(content, old_id)
        # Now we can check out, since the tool will remove the sticky tag
        # without losing data.
        vt.checkout(content)
        content = self.root.content  # XXX ZopeVersionControl requires this

        current_id = vt.getVersionId(content)
        self.assertNotEqual(current_id, old_id)
        self.assertNotEqual(current_id, new_id)


    def testRevertToOldThenCheckout(self):
        # Test that the versions tool automatically copies old states forward
        vt = self.tool
        content = self.root.content
        vt.checkin(content)
        old_id = vt.getVersionId(content)
        vt.checkout(content)
        vt.checkin(content)
        new_id = vt.getVersionId(content)
        vt.revertToVersion(content, old_id)
        content = self.root.content  # XXX ZopeVersionControl requires this
        del content.__vc_info__.sticky  # Simulate non-sticky

        vt.auto_copy_forward = 0
        # Can't normally check out when the object is in an old state
        self.assertRaises(VersionControlError, vt.checkout, content)

        vt.auto_copy_forward = 1
        # Now we can check out, since the tool will copy the old state forward
        # before checking out.
        vt.checkout(content)
        content = self.root.content  # XXX ZopeVersionControl requires this

        current_id = vt.getVersionId(content)
        self.assertNotEqual(current_id, old_id)
        self.assertNotEqual(current_id, new_id)


    def testGetLogEntries(self):
        vt = self.tool
        content = self.root.content
        log = vt.getLogEntries(content)
        self.assertEqual(tuple(log), ())

        vt.checkin(content)
        vt.checkout(content)
        vt.checkin(content)

        log = vt.getLogEntries(content, only_checkins=1)
        self.assert_(len(log) == 2)
        
        log = vt.getLogEntries(content, only_checkins=0)
        for entry in log:
            for key in ('timestamp', 'version_id', 'action', 'message',
                        'user_id', 'path'):
                self.assert_(entry.has_key(key))


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Tests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

