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
"""Unit tests for the staging tool.

$Id$
"""

import unittest
import Testing
import Zope
Zope.startup()
from Acquisition import aq_base
from OFS.Folder import Folder
from AccessControl.SecurityManagement import newSecurityManager, \
     noSecurityManager

from Products.CMFStaging.StagingTool import StagingTool, StagingError
from Products.CMFStaging.tests.testLockTool import TestUser
from Products.ZopeVersionControl.Utility import VersionControlError


class StagingTests(unittest.TestCase):

    def setUp(self):
        # Set up an application with a repository, 3 stages, the tools,
        # and a little content in the repository.
        # Note that you don't actually need a CMF site to use staging! ;-)
        app = Zope.app()
        self.app = app
        self.conn = app._p_jar
        if hasattr(app, 'testroot'):
            app._delObject('testroot')
        app.manage_addProduct['OFSP'].manage_addFolder('testroot')
        self.root = app.testroot
        zvc = self.root.manage_addProduct['ZopeVersionControl']
        zvc.addRepository('VersionRepository')
        self.root.manage_addProduct['OFSP'].manage_addFolder('Stages')
        self.stages = self.root.Stages
        self.stages.manage_addProduct['OFSP'].manage_addFolder('Development')
        self.stages.manage_addProduct['OFSP'].manage_addFolder('Review')
        self.stages.manage_addProduct['OFSP'].manage_addFolder('Production')
        self.root.manage_addProduct['CMFStaging'].manage_addTool(
            StagingTool.meta_type)
        self.root.portal_staging._stages = (
            ('dev',    'Development', 'Stages/Development'),
            ('review', 'Review',      'Stages/Review'),
            ('prod',   'Production',  'Stages/Production'),
            )

        dev_stage = self.stages.Development
        dev_stage.manage_addProduct['OFSP'].manage_addFolder('nonv')
        self.dev_stage = dev_stage
        self.review_stage = self.stages.Review
        self.prod_stage = self.stages.Production
        self._addContent()

        user = TestUser('sally')
        newSecurityManager(None, user.__of__(self.root.acl_users))


    def _addContent(self):
        # This method is overridden by the reference staging tests.
        self.dev_stage.manage_addProduct['OFSP'].manage_addFolder('c1')
        self.dev_stage.manage_addProduct['OFSP'].manage_addFolder('c2')
        repo = self.root.VersionRepository
        repo.applyVersionControl(self.dev_stage.c1)
        repo.applyVersionControl(self.dev_stage.c2)


    def tearDown(self):
        noSecurityManager()
        app = self.app
        try:
            if hasattr(app, 'testroot'):
                app._delObject('testroot')
                get_transaction().commit()
            else:
                get_transaction().abort()
        finally:
            self.conn.close()


    def testStageable(self):
        st = self.root.portal_staging
        self.assert_(st.isStageable(self.dev_stage.c1))


    def testGetVersionIds(self):
        st = self.root.portal_staging
        versions = st.getVersionIds(self.dev_stage.c1)
        self.assert_(versions['dev'])
        self.assert_(not versions['review'])
        self.assert_(not versions['prod'])

        # Can't get version IDs of something not located in any stage
        self.assertRaises(StagingError, st.getVersionIds, self.root)


    def testUpdateStages(self):
        st = self.root.portal_staging
        self.assert_('c1' not in self.review_stage.objectIds())

        st.updateStages2(self.dev_stage.c1, ['review'])
        versions = st.getVersionIds(self.dev_stage.c1)
        self.assert_(versions['dev'])
        self.assert_(versions['review'])
        self.assert_(not versions['prod'])
        self.assert_('c1' in self.review_stage.objectIds())
        self.assert_('c1' not in self.prod_stage.objectIds())

        st.updateStages2(self.dev_stage.c2, ['review', 'prod'])
        versions = st.getVersionIds(self.dev_stage.c2)
        self.assert_(versions['dev'])
        self.assert_(versions['review'])
        self.assert_(versions['prod'])

        st.updateStages2(self.dev_stage.c1, ['prod'])
        versions = st.getVersionIds(self.dev_stage.c1)
        self.assert_(versions['dev'])
        self.assert_(versions['review'])
        self.assert_(versions['prod'])
        self.assert_('c1' in self.prod_stage.objectIds())


    def testUpdateStagesExceptions(self):
        st = self.root.portal_staging
        # "nonv" is not under version control.
        self.assertRaises(VersionControlError, st.updateStages2,
                          self.dev_stage.nonv, ['review'])
        # Put something in the way and make sure it doesn't get overwritten.
        self.review_stage.manage_addProduct['OFSP'].manage_addFolder('c1')
        self.assertRaises(
            StagingError, st.updateStages2, self.dev_stage.c1, ['review'])
        # Put the blocker under version control and verify it still doesn't
        # get overwritten, since it is backed by a different version history.
        repo = self.root.VersionRepository
        repo.applyVersionControl(self.review_stage.c1)
        self.assertRaises(
            StagingError, st.updateStages2, self.dev_stage.c1, ['review'])
        # Move the blocker out of the way and verify updates can occur again.
        self.review_stage._delObject('c1')
        st.updateStages2(self.dev_stage.c1, ['review'])


    def testRemoveStages(self):
        st = self.root.portal_staging
        self.assert_('c1' not in self.review_stage.objectIds())
        st.updateStages2(self.dev_stage.c1, ['review'])
        self.assert_('c1' in self.review_stage.objectIds())
        st.removeStages(self.dev_stage.c1, ['review'])
        self.assert_('c1' not in self.review_stage.objectIds())
        

    def testCheckContainer(self):
        st = self.root.portal_staging
        self.dev_stage.c1.manage_addProduct['OFSP'].manage_addFolder(
            'test')
        self.assert_('c1' not in self.review_stage.objectIds())
        # c1 is ok
        st.checkContainers(self.dev_stage.c1, ['review'])
        # c1 doesn't exist on the review stage yet, so updates
        # to c1.test can't work yet.
        self.assertRaises(StagingError, st.checkContainers,
                          self.dev_stage.c1.test, ['review'])


    def testGetURLForStage(self):
        st = self.root.portal_staging
        url = st.getURLForStage(self.dev_stage.c1, 'dev', 1)
        self.assert_(url.find('/Stages/Development/c1') >= 0)


    def testCompleteSetup(self):
        # Create a lock tool and versions tool then perform
        # some complete development and staging activities.
        from Products.CMFStaging.LockTool import LockTool
        from Products.CMFStaging.VersionsTool import VersionsTool

        self.root.manage_addProduct['CMFStaging'].manage_addTool(
            LockTool.meta_type)
        self.root.manage_addProduct['CMFStaging'].manage_addTool(
            VersionsTool.meta_type)

        lt = self.root.portal_lock
        vt = self.root.portal_versions
        st = self.root.portal_staging

        # The automation features need to be turned on.
        self.assert_(lt.auto_version)
        self.assert_(st.auto_checkin)

        user = TestUser('andre')
        newSecurityManager(None, user.__of__(self.root.acl_users))

        # Put c1 in the review stage.
        # Lock with auto checkout
        lt.lock(self.dev_stage.c1)
        # Update with auto unlock and checkin
        st.updateStages2(self.dev_stage.c1, ['review'])
        versions = st.getVersionIds(self.dev_stage.c1)
        self.assertEqual(versions['dev'], versions['review'])
        self.assert_(not versions['prod'])

        # Make a change in the dev stage.
        # Lock with auto checkout
        lt.lock(self.dev_stage.c1)
        # Unlock with auto checkin
        lt.unlock(self.dev_stage.c1)
        versions = st.getVersionIds(self.dev_stage.c1)
        self.assertNotEqual(versions['dev'], versions['review'])
        wanted_published = versions['dev'] # This version should be published.

        # Publish c1.
        # Unlocked and checked in already
        st.updateStages2(self.dev_stage.c1, ['review', 'prod'])
        versions = st.getVersionIds(self.dev_stage.c1)
        self.assertEqual(versions['dev'], wanted_published)
        self.assertEqual(versions['dev'], versions['review'])
        self.assertEqual(versions['dev'], versions['prod'])



def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(StagingTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

