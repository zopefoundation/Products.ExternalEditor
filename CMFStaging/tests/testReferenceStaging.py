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
"""Unit tests for staging reference objects.

$Id$
"""

import unittest
import Testing
import Zope
Zope.startup()

has_refs = 1
try:
    from Products.References.PathReference import PathReference
except ImportError:
    has_refs = 0

from Products.CMFStaging.tests.testStaging import StagingTests

class ReferenceStagingTests(StagingTests):

    def _addContent(self):
        # Unlike the standard StagingTests, adds references instead of
        # standard folders.
        self.dev_stage.manage_addProduct['OFSP'].manage_addFolder('real_c1')
        self.dev_stage.manage_addProduct['OFSP'].manage_addFolder('real_c2')
        # XXX this uses PathReference internals to create a relative
        # rather than absolute path
        c1 = PathReference("c1", self.dev_stage.real_c1)
        c1.path = ("real_c1",)
        self.dev_stage._setObject(c1.id, c1)
        c2 = PathReference("c2", self.dev_stage.real_c2)
        c2.path = ("real_c2",)
        self.dev_stage._setObject(c2.id, c2)
        repo = self.root.VersionRepository
        repo.applyVersionControl(self.dev_stage.real_c1)
        repo.applyVersionControl(self.dev_stage.real_c2)


def test_suite():
    suite = unittest.TestSuite()
    if has_refs:
        suite.addTest(unittest.makeSuite(ReferenceStagingTests))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

