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
"""Test the unique id handling.

$Id$
"""
__version__ = "$Revision$"

from unittest import TestCase, TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()

from Interface.Verify import verifyObject

from Products.CMFCore.tests.base.testcase import SecurityTest

from Products.CMFCore.tests.base.dummy import DummyContent
from Products.CMFCore.tests.base.dummy import DummyFolder
from Products.CMFCore.tests.base.dummy import DummySite

from Products.CMFCore.CatalogTool import CatalogTool

from Products.CMFUid.interfaces import IUniqueIdHandler
from Products.CMFUid.UniqueIdGeneratorTool import UniqueIdGeneratorTool
from Products.CMFUid.UniqueIdAnnotationTool import UniqueIdAnnotationTool
from Products.CMFUid.UniqueIdHandlerTool import UniqueIdHandlerTool

def removeUnnecessaryIndexes(catalog):
    indexes = [id[0] for id in catalog.enumerateIndexes()]
    columns = catalog.enumerateColumns()
    catalog.manage_delIndex(indexes)
    catalog.manage_delColumn(columns)

class UniqueIdHandlerTests(SecurityTest):

    def setUp(self):
        SecurityTest.setUp(self)
        self.root._setObject('portal_catalog', CatalogTool())
        self.root._setObject('portal_uidgenerator', UniqueIdGeneratorTool())
        self.root._setObject('portal_uidannotation', UniqueIdAnnotationTool())
        self.root._setObject('portal_uidhandler', UniqueIdHandlerTool())
        self.root._setObject('dummy', DummyContent(id='dummy'))
        
        removeUnnecessaryIndexes(self.root.portal_catalog)
    
    def test_interface(self):
        handler = self.root.portal_uidhandler
        verifyObject(IUniqueIdHandler, handler)
    
    def test_getUidOfNotYetRegisteredObject(self):
        handler = self.root.portal_uidhandler
        dummy = self.root.dummy
        UniqueIdError = handler.UniqueIdError
        
        self.assertEqual(handler.queryUid(dummy, None), None)
        self.assertRaises(UniqueIdError, handler.getUid, dummy)
    
    def test_getInvalidUid(self):
        handler = self.root.portal_uidhandler
        dummy = self.root.dummy
        UniqueIdError = handler.UniqueIdError
        
        self.assertEqual(handler.queryObject(100, None), None)
        self.assertRaises(UniqueIdError, handler.getObject, 100)
    
        uid = handler.register(dummy)
        self.assertEqual(handler.queryObject(uid+1, None), None)
        self.assertRaises(UniqueIdError, handler.getObject, uid+1)
    
    def test_getUidOfRegisteredObject(self):
        handler = self.root.portal_uidhandler
        dummy = self.root.dummy
        
        uid = handler.register(dummy)
        self.assertEqual(handler.getUid(dummy), uid)
    
    def test_getRegisteredObjectByUid(self):
        handler = self.root.portal_uidhandler
        dummy = self.root.dummy
        
        uid = handler.register(dummy)
        self.assertEqual(handler.getObject(uid), dummy)
    
    def test_getUnregisteredObject(self):
        handler = self.root.portal_uidhandler
        dummy = self.root.dummy
        UniqueIdError = handler.UniqueIdError
        
        uid = handler.register(dummy)
        handler.unregister(dummy)
        self.assertEqual(handler.queryObject(uid, None), None)
        self.assertRaises(UniqueIdError, handler.getObject, uid)

    def test_getUidOfUnregisteredObject(self):
        handler = self.root.portal_uidhandler
        dummy = self.root.dummy
        UniqueIdError = handler.UniqueIdError
        
        uid = handler.register(dummy)
        handler.unregister(dummy)
        self.assertEqual(handler.queryUid(dummy, None), None)
        self.assertRaises(UniqueIdError, handler.getUid, dummy)

    def test_reregisterObject(self):
        handler = self.root.portal_uidhandler
        dummy = self.root.dummy
        
        uid1_reg = handler.register(dummy)
        uid1_get = handler.getUid(dummy)
        uid2_reg = handler.register(dummy)
        uid2_get = handler.getUid(dummy)
        self.assertEqual(uid1_reg, uid2_reg)
        self.assertEqual(uid1_get, uid2_get)
        self.assertEqual(uid1_reg, uid1_get)
    
    def test_unregisterObjectWithoutUid(self):
        handler = self.root.portal_uidhandler
        dummy = self.root.dummy
        UniqueIdError = handler.UniqueIdError
        
        self.assertRaises(UniqueIdError, handler.unregister, dummy)


def test_suite():
    return TestSuite((
        makeSuite(UniqueIdHandlerTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
