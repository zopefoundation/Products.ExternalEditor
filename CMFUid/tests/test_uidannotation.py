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
"""Test the unique id annotation.

$Id$
"""
__version__ = "$Revision$"

from unittest import TestCase, TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()

from Interface.Verify import verifyObject

from Products.CMFCore.tests.base.dummy import DummyContent

from Products.CMFCore.tests.base.testcase import SecurityTest

from Products.CMFUid.interfaces import IUniqueIdAnnotation
from Products.CMFUid.interfaces import IUniqueIdAnnotationManagement
from Products.CMFUid.UniqueIdAnnotationTool import UniqueIdAnnotationTool


UID_ATTRNAME = 'cmf_uid'

class UniqueIdAnnotationTests(SecurityTest):

    def setUp(self):
        SecurityTest.setUp(self)
        self.root._setObject('portal_uidannotation', UniqueIdAnnotationTool())
        self.root._setObject('dummy', DummyContent(id='dummy'))
    
    def test_interface(self):
        dummy = self.root.dummy
        anno_tool = self.root.portal_uidannotation
        annotation = anno_tool(dummy, UID_ATTRNAME)
        
        verifyObject(IUniqueIdAnnotationManagement, anno_tool)
        verifyObject(IUniqueIdAnnotation, annotation)
        
    def test_setAndGetUid(self):
        dummy = self.root.dummy
        annotation = self.root.portal_uidannotation(dummy, UID_ATTRNAME)
        
        self.assertEqual(annotation(), None)
        annotation.setUid(13)
        self.assertEqual(annotation(), 13)
        
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
        dummy = self.root.dummy
        annotation = self.root.portal_uidannotation(dummy, UID_ATTRNAME)
        
        annotation.manage_afterAdd(dummy, None)
        self.assertRaises(AttributeError, getattr, dummy, UID_ATTRNAME)
        
    def test_simulateItemAddDoesNotTouchUid(self):
        dummy = self.root.dummy
        annotation = self.root.portal_uidannotation(dummy, UID_ATTRNAME)
        
        self.root.portal_uidannotation.remove_on_add = False
        annotation.manage_afterAdd(dummy, None)
        self.assertEqual(getattr(dummy, UID_ATTRNAME), annotation)
        
    def test_simulateItemRename(self):
        dummy = self.root.dummy
        annotation = self.root.portal_uidannotation(dummy, UID_ATTRNAME)
        
        annotation.manage_beforeDelete(dummy, None)
        annotation.manage_afterAdd(dummy, None)
        self.assertEqual(getattr(dummy, UID_ATTRNAME), annotation)
        
    def test_simulateItemCloneRemovingUid1(self):
        dummy = self.root.dummy
        annotation = self.root.portal_uidannotation(dummy, UID_ATTRNAME)
        
        annotation.manage_afterAdd(dummy, None)
        annotation.manage_afterClone(dummy)
        self.assertRaises(AttributeError, getattr, dummy, UID_ATTRNAME)
        
    def test_simulateItemCloneRemovingUid2(self):
        dummy = self.root.dummy
        annotation = self.root.portal_uidannotation(dummy, UID_ATTRNAME)
        
        self.root.portal_uidannotation.remove_on_add = False
        annotation.manage_afterAdd(dummy, None)
        annotation.manage_afterClone(dummy)
        self.assertRaises(AttributeError, getattr, dummy, UID_ATTRNAME)
        
    def test_simulateItemCloneDoesNotTouchUid(self):
        dummy = self.root.dummy
        annotation = self.root.portal_uidannotation(dummy, UID_ATTRNAME)
        
        self.root.portal_uidannotation.remove_on_clone = False
        annotation.manage_afterAdd(dummy, None)
        annotation.manage_afterClone(dummy)
        self.assertEqual(getattr(dummy, UID_ATTRNAME), annotation)


def test_suite():
    return TestSuite((
        makeSuite(UniqueIdAnnotationTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
