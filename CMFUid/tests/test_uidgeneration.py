##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Test the unique id generation.

$Id$
"""

from unittest import TestCase, TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()

from Interface.Verify import verifyObject

from Products.CMFCore.tests.base.dummy import DummyContent

from Products.CMFCore.tests.base.testcase import SecurityTest

from Products.CMFUid.interfaces import IUniqueIdGenerator
from Products.CMFUid.UniqueIdGeneratorTool import UniqueIdGeneratorTool


class UniqueIdGeneratorTests(SecurityTest):

    def setUp(self):
        SecurityTest.setUp(self)
        self.root._setObject('portal_uidgenerator', UniqueIdGeneratorTool())
    
    def test_interface(self):
        generator = self.root.portal_uidgenerator
        verifyObject(IUniqueIdGenerator, generator)
        
    def test_returnedUidsAreValidAndDifferent(self):
        generator = self.root.portal_uidgenerator
        uid1 = generator()
        uid2 = generator()
        self.failIfEqual(uid1, uid2)
        self.failIfEqual(uid1, None)

def test_suite():
    return TestSuite((
        makeSuite(UniqueIdGeneratorTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
