##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
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
__version__ = "$Revision$"

from unittest import TestCase, TestSuite, makeSuite, main
#import Testing
#import Zope
#Zope.startup()

from Products.CMFUid.interfaces \
    import IUniqueIdGenerator, IAnnotatedUniqueId
from Products.CMFUid.UniqueIdGeneratorTool import UniqueIdGeneratorTool


UID_ATTRNAME = 'uid'

class DummyItem:
    def getUidObject(self):
        return getattr(self, UID_ATTRNAME)
    def setUid(self, uid):
        setattr(self, UID_ATTRNAME, uid)

def addDummyItemWithUid(remove_on_add=None, remove_on_clone=None):
    generator = UniqueIdGeneratorTool()
    item = DummyItem()
    setattr(item, UID_ATTRNAME, generator())
    uid = getattr(item, UID_ATTRNAME)
    if remove_on_add is not None:
        uid.remove_on_add = remove_on_add
    if remove_on_clone is not None:
        uid.remove_on_clone = remove_on_clone
    uid.setId(UID_ATTRNAME)
    return item, uid

class UniqueIdGeneratorTests(TestCase):

    def test_interface(self):
        generator = UniqueIdGeneratorTool()
        IUniqueIdGenerator.isImplementedBy(generator)
        IAnnotatedUniqueId.isImplementedBy(generator())
        
    def test_returnedUidsAreDifferent(self):
        generator = UniqueIdGeneratorTool()
        uid1 = generator()
        uid2 = generator()
        self.failIfEqual(uid1, uid2)
        self.failIfEqual(uid1(), uid2())
        self.failIfEqual(uid1(), None)
        
    def test_getIdOfUidObject(self):
        generator = UniqueIdGeneratorTool()
        uid1 = generator()
        uid1.setId('blah')
        self.assertEqual(uid1.getId(), 'blah')
        
    # copy/rename/add events: Just to remember
    #
    # add/import obj:
    #   obj.manage_afterAdd(obj, obj, folder)
    #
    # move/rename obj:
    #   obj.manage_beforeDelete(obj, obj, source_folder)
    #   obj.manage_afterAdd(obj_at_target, obj_at_target, target_folder)
    #
    # copy and paste (clone) obj:
    #   obj.manage_afterAdd(obj_at_target, obj_at_target, target_folder)
    #   obj.manage_afterClone(obj_at_target, obj_at_target)
        
    def test_simulateItemAddRemovingUid(self):
        item, uid = addDummyItemWithUid()
        uid.manage_afterAdd(item, None)
        self.assertRaises(AttributeError, getattr, item, UID_ATTRNAME)
        
    def test_simulateItemAddDoesNotTouchUid(self):
        item, uid = addDummyItemWithUid(remove_on_add=False)
        uid.manage_afterAdd(item, None)
        self.assertEqual(getattr(item, UID_ATTRNAME)(), 1)
        
    def test_simulateItemRename(self):
        item, uid = addDummyItemWithUid()
        uid.manage_beforeDelete(item, None)
        uid.manage_afterAdd(item, None)
        self.assertEqual(getattr(item, UID_ATTRNAME)(), 1)
        
    def test_simulateItemCloneRemovingUid1(self):
        item, uid = addDummyItemWithUid()
        uid.manage_afterAdd(item, None)
        uid.manage_afterClone(item)
        self.assertRaises(AttributeError, getattr, item, UID_ATTRNAME)
        
    def test_simulateItemCloneRemovingUid2(self):
        item, uid = addDummyItemWithUid(remove_on_add=False)
        uid.manage_afterAdd(item, None)
        uid.manage_afterClone(item)
        self.assertRaises(AttributeError, getattr, item, UID_ATTRNAME)
        
    def test_simulateItemCloneDoesNotTouchUid(self):
        item, uid = addDummyItemWithUid(remove_on_clone=False)
        uid.manage_afterAdd(item, None)
        uid.manage_afterClone(item)
        self.assertEqual(getattr(item, UID_ATTRNAME)(), 1)

def test_suite():
    return TestSuite((
        makeSuite(UniqueIdGeneratorTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
