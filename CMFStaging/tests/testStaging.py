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
from Acquisition import aq_base
from OFS.Folder import Folder
from OFS.Application import Application

from Products.CMFStaging.StagingTool import StagingTool


class Tests(unittest.TestCase):

    def setUp(self):
        # Set up an application with a repository, 3 stages, the tools,
        # and a little content in the repository.
        # Note that you don't actually need a CMF site. ;-)
        app = Zope.app()
        self.app = app
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
        dev_stage = self.stages.Development
        dev_stage.manage_addProduct['OFSP'].manage_addFolder('c1')
        dev_stage.manage_addProduct['OFSP'].manage_addFolder('c2')
        self.dev_stage = dev_stage

        repo = self.root.VersionRepository
        repo.applyVersionControl(dev_stage.c1)
        repo.applyVersionControl(dev_stage.c2)

    def tearDown(self):
        self.app._p_jar.close()

    def testStageable(self):
        st = self.root.portal_staging
        self.assert_(st.isStageable(self.dev_stage.c1))

    def testGetVersionIds(self):
        st = self.root.portal_staging
        versions = st.getVersionIds(self.dev_stage.c1)
        self.assert_(versions['dev'])
        self.assert_(not versions['review'])
        self.assert_(not versions['prod'])

    def testUpdateStages(self):
        st = self.root.portal_staging

        st.updateStages(self.dev_stage.c1, 'dev', ['review'])
        versions = st.getVersionIds(self.dev_stage.c1)
        self.assert_(versions['dev'])
        self.assert_(versions['review'])
        self.assert_(not versions['prod'])

        st.updateStages(self.dev_stage.c2, 'dev', ['review', 'prod'])
        versions = st.getVersionIds(self.dev_stage.c2)
        self.assert_(versions['dev'])
        self.assert_(versions['review'])
        self.assert_(versions['prod'])
        
        st.updateStages(self.dev_stage.c1, 'dev', ['prod'])
        versions = st.getVersionIds(self.dev_stage.c1)
        self.assert_(versions['dev'])
        self.assert_(versions['review'])
        self.assert_(versions['prod'])
        


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Tests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

