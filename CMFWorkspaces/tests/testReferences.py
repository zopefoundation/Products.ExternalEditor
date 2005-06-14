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
"""Unit tests for BTreeFolder2.

$Id$
"""

import unittest
import Testing
import Zope
Zope.startup()
from Products.CMFWorkspaces.References import ReferenceCollection
from OFS.Folder import Folder
from Acquisition import aq_base, aq_inner, aq_parent
from Products.CMFCore.URLTool import URLTool


class Tests(unittest.TestCase):

    def setUp(self):
        f1 = Folder()
        f1.id = 'f1'
        self.f1 = f1
        f2 = Folder()
        f2.id = 'f2'
        self.f1.f2 = f2
        f3 = Folder()
        f3.id = 'f3'
        self.f1.f2.f3 = f3
        f4 = Folder()
        f4.id = 'f4'
        self.f1.f2.f4 = f4
        f4_1 = Folder()
        f4_1.id = 'f4'
        self.f1.f4 = f4_1
        f1.portal_url = URLTool()
        f1.refs = ReferenceCollection()

    def testAdd(self):
        self.f1.refs.addReference(self.f1.f2.f3)
        self.f1.refs.addReference(self.f1.f2.f4)
        self.assertEqual(len(self.f1.refs), 2)
        
    def testAddSameIds(self):
        self.f1.refs.addReference(self.f1.f2.f4)
        self.f1.refs.addReference(self.f1.f4)
        self.assertEqual(len(self.f1.refs), 2)        

    def testMappingInterface(self):
        self.f1.refs.addReference(self.f1.f2.f3)
        self.assertEqual(len(self.f1.refs), 1)
        self.assertEqual(len(self.f1.refs.keys()), 1)
        self.assertEqual(len(self.f1.refs.values()), 1)
        self.assertEqual(len(self.f1.refs.items()), 1)
        id = self.f1.refs.keys()[0]
        ref = self.f1.refs[id]
        self.assert_(ref is not None)
        self.assert_(self.f1.refs.values()[0] == ref)
        self.assert_(self.f1.refs.items()[0] == (id, ref))

    def testPreventDuplicates(self):
        self.assert_(self.f1.refs._ignore_dups)
        self.f1.refs.addReference(self.f1.f2.f3)
        self.f1.refs.addReference(self.f1.f2.f4)
        self.assertEqual(len(self.f1.refs), 2)
        self.f1.refs.addReference(self.f1.f2.f3)
        self.assertEqual(len(self.f1.refs), 2)

    def testRemove(self):
        self.f1.refs.addReference(self.f1.f2.f3)
        self.f1.refs.addReference(self.f1.f2.f4)
        id = self.f1.refs.keys()[0]
        self.f1.refs.removeReference(id)
        self.assertEqual(len(self.f1.refs), 1)

    def testDereference(self):
        self.f1.refs.addReference(self.f1.f2.f3)
        id = self.f1.refs.keys()[0]
        ref = self.f1.refs[id]
        ob = ref.dereference(self.f1.f2)
        # Check that the correct object was returned.
        self.assert_(aq_base(ob) is aq_base(self.f1.f2.f3))
        # Check for correct wrapping.
        self.assert_(aq_base(ob) is not ob)
        self.assert_(aq_base(aq_parent(ob)) is aq_base(self.f1.f2))
        self.assert_(aq_base(aq_parent(aq_inner(ob))) is aq_base(self.f1.f2))

        # Try the same thing from a different context.
        ob = ref.dereference(self.f1)
        self.assert_(aq_base(ob) is aq_base(self.f1.f2.f3))
        # Check for correct wrapping.
        self.assert_(aq_base(ob) is not ob)
        self.assert_(aq_base(aq_parent(ob)) is aq_base(self.f1))
        self.assert_(aq_base(aq_parent(aq_inner(ob))) is aq_base(self.f1.f2))

    def testDereferenceDeletedObject(self):
        self.f1.refs.addReference(self.f1.f2.f3)
        id = self.f1.refs.keys()[0]
        ref = self.f1.refs[id]
        ob = ref.dereference(self.f1)
        self.assert_(aq_base(ob) is aq_base(self.f1.f2.f3))
        self.f1.f2._delObject('f3')
        self.assertRaises(Exception, ref.dereference, self.f1)

    def testDereferenceDefault(self):
        self.f1.refs.addReference(self.f1.f2.f3)
        id = self.f1.refs.keys()[0]
        ref = self.f1.refs[id]
        ob = ref.dereference(self.f1)
        self.assert_(aq_base(ob) is aq_base(self.f1.f2.f3))
        self.f1.f2._delObject('f3')
        marker = []
        self.assertEqual(ref.dereferenceDefault(self.f1, marker), marker)
        


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Tests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

