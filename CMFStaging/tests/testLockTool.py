##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Unit tests for the lock tool.

$Id$
"""

import unittest
import Testing
from Acquisition import aq_base
import Zope
Zope.startup()
from OFS.Folder import Folder
from AccessControl.SecurityManagement \
     import newSecurityManager, noSecurityManager
from AccessControl.User import SimpleUser

from Products.CMFStaging.LockTool import LockTool, LockingError


class TestUser(SimpleUser):

    def __init__(self, id):
        SimpleUser.__init__(self, id, '', (), ())

    def has_permission(self, *arg, **kw):
        return 1

    def allowed(self, *arg, **kw):
        return 1


class Tests(unittest.TestCase):

    def setUp(self):
        app = Zope.app()
        self.app = app
        if hasattr(app, 'testroot'):
            app._delObject('testroot')
        app.manage_addProduct['OFSP'].manage_addFolder('testroot')
        self.root = app.testroot

        setattr(self.root, LockTool.id, LockTool())
        self.tool = getattr(self.root, LockTool.id)
        self.root.content = Folder()
        self.root.content.id = 'content'
        user = TestUser('sally')
        newSecurityManager(None, user.__of__(self.root.acl_users))
        self.user = user

    def tearDown(self):
        noSecurityManager()
        app = self.app
        if hasattr(app, 'testroot'):
            app._delObject('testroot')
        self.app._p_jar.close()

    def testNotInitiallyLocked(self):
        self.assert_(not self.tool.locked(self.root.content))

    def testLock(self):
        self.tool.lock(self.root.content)
        self.assert_(self.tool.locked(self.root.content))

    def testUnlock(self):
        self.tool.lock(self.root.content)
        self.assert_(self.tool.locked(self.root.content))
        self.tool.unlock(self.root.content)
        self.assert_(not self.tool.locked(self.root.content))
        # Double-check: do it twice.
        self.tool.lock(self.root.content)
        self.tool.unlock(self.root.content)
        self.assert_(not self.tool.locked(self.root.content))

    def testTheftPrevention(self):
        self.tool.lock(self.root.content)
        self.assert_(self.tool.locked(self.root.content))
        # Another user can't steal the lock.
        user2 = TestUser('sue')
        newSecurityManager(None, user2.__of__(self.root.acl_users))
        self.assertRaises(LockingError, self.tool.unlock, self.root.content)
        self.assertRaises(LockingError, self.tool.lock, self.root.content)
        # But the original user can unlock.
        newSecurityManager(None, self.user.__of__(self.root.acl_users))
        self.tool.unlock(self.root.content)
        self.assert_(not self.tool.locked(self.root.content))

    def testLocker(self):
        self.tool.lock(self.root.content)
        self.assert_(self.tool.locker(self.root.content) == 'sally')

    def testIsLockedOut(self):
        # Not locked out if the object is not locked or the
        # current user holds the lock.
        self.assert_(not self.tool.isLockedOut(self.root.content))
        self.tool.lock(self.root.content)
        self.assert_(not self.tool.isLockedOut(self.root.content))
        user2 = TestUser('sue')
        newSecurityManager(None, user2.__of__(self.root.acl_users))
        self.assert_(self.tool.isLockedOut(self.root.content))
        # Go back to original user to double-check (might fail if
        # the computation depends on stored state)
        newSecurityManager(None, self.user.__of__(self.root.acl_users))
        self.assert_(not self.tool.isLockedOut(self.root.content))
        


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Tests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

