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
"""Tests for CMFStaging.

$Id$
"""

import unittest

from Products.CMFStaging.tests.testLockTool import test_suite as lock_tests
from Products.CMFStaging.tests.testVersions import test_suite as version_tests
from Products.CMFStaging.tests.testStaging import test_suite as staging_tests

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(lock_tests())
    suite.addTest(version_tests())
    suite.addTest(staging_tests())
    return suite
    
if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
