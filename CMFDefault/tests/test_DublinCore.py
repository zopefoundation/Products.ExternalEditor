from unittest import TestSuite, makeSuite, main

import Testing
import Zope
try:
    Zope.startup()
except AttributeError:
    # for Zope versions before 2.6.1
    pass
try:
    from Interface.Verify import verifyClass
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import verify_class_implementation as verifyClass

from AccessControl.SecurityManagement import newSecurityManager

from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.dummy import DummyUserFolder
from Products.CMFCore.tests.base.testcase import SecurityTest
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
from Products.CMFDefault.MembershipTool import MembershipTool


class DummyContent(PortalContent, DefaultDublinCoreImpl):
    pass


class DublinCoreTests(SecurityTest):

    def setUp(self):
        SecurityTest.setUp(self)
        self.site = DummySite('site').__of__(self.root)
        self.site._setObject( 'portal_membership', MembershipTool() )

    def _makeDummyContent(self, id, *args, **kw):
        return self.site._setObject( id, DummyContent(id, *args, **kw) )

    def test_notifyModified(self):
        acl_users = self.site._setObject( 'acl_users', DummyUserFolder() )
        newSecurityManager(None, acl_users.user_foo)
        item = self._makeDummyContent('item')
        self.assertEqual( item.listCreators(), () )
        item.setModificationDate(0)
        initial_date = item.ModificationDate()

        item.notifyModified()
        self.assertEqual( item.listCreators(), ('user_foo',) )
        self.assertNotEqual( item.ModificationDate(), initial_date )

    def test_creators_methods(self):
        acl_users = self.site._setObject( 'acl_users', DummyUserFolder() )
        newSecurityManager(None, acl_users.user_foo)
        item = self._makeDummyContent('item')
        self.assertEqual( item.listCreators(), () )

        item.addCreator()
        self.assertEqual( item.listCreators(), ('user_foo',) )
        newSecurityManager(None, acl_users.user_bar)
        item.addCreator()
        self.assertEqual( item.listCreators(), ('user_foo', 'user_bar') )
        item.addCreator()
        self.assertEqual( item.listCreators(), ('user_foo', 'user_bar') )
        item.addCreator('user_baz')
        self.assertEqual( item.listCreators(),
                          ('user_foo', 'user_bar', 'user_baz') )

    def test_interface(self):
        from Products.CMFCore.interfaces.DublinCore \
                import DublinCore as IDublinCore
        from Products.CMFCore.interfaces.DublinCore \
                import CatalogableDublinCore as ICatalogableDublinCore
        from Products.CMFCore.interfaces.DublinCore \
                import MutableDublinCore as IMutableDublinCore

        verifyClass(IDublinCore, DefaultDublinCoreImpl)
        verifyClass(ICatalogableDublinCore, DefaultDublinCoreImpl)
        verifyClass(IMutableDublinCore, DefaultDublinCoreImpl)


def test_suite():
    return TestSuite((
        makeSuite( DublinCoreTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
