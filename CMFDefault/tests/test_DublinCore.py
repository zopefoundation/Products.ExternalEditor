from unittest import TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()

from Acquisition import Implicit
from Interface.Verify import verifyClass

from AccessControl.SecurityManagement import newSecurityManager

from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.dummy import DummyUserFolder
from Products.CMFCore.tests.base.testcase import SecurityTest
from Products.CMFDefault.MembershipTool import MembershipTool



def _DateIndexConvert(value):
    # Duplicate date conversion done by DateIndex._convert
    t_tup = value.toZone('UTC').parts()
    yr = t_tup[0]
    mo = t_tup[1]
    dy = t_tup[2]
    hr = t_tup[3]
    mn = t_tup[4]
    t_val = ((((yr * 12 + mo) * 31 + dy) * 24 + hr) * 60 + mn)

    if isinstance(t_val, long):
        # t_val must be IntType, not LongType
        raise OverflowError("Date too big: %s" % `value`)

    return t_val

class DummyMetadataTool(Implicit):

    def __init__(self, publisher):
        self._publisher = publisher

    def getPublisher(self):
        return self._publisher

class DublinCoreTests(SecurityTest):

    def xxx_setUp(self):
        SecurityTest.setUp(self)

    def test_interface(self):
        from Products.CMFCore.interfaces.DublinCore \
                import DublinCore as IDublinCore
        from Products.CMFCore.interfaces.DublinCore \
                import CatalogableDublinCore as ICatalogableDublinCore
        from Products.CMFCore.interfaces.DublinCore \
                import MutableDublinCore as IMutableDublinCore
        from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl

        verifyClass(IDublinCore, DefaultDublinCoreImpl)
        verifyClass(ICatalogableDublinCore, DefaultDublinCoreImpl)
        verifyClass(IMutableDublinCore, DefaultDublinCoreImpl)

    def _makeDummyContent(self, id, *args, **kw):

        from Products.CMFCore.PortalContent import PortalContent
        from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl

        class DummyContent(PortalContent, DefaultDublinCoreImpl):
            pass

        return DummyContent(id, *args, **kw)

    def test_notifyModified(self):
        site = DummySite('site').__of__(self.root)
        acl_users = site._setObject( 'acl_users', DummyUserFolder() )
        site._setObject( 'portal_membership', MembershipTool() )
        newSecurityManager(None, acl_users.user_foo)
        item = self._makeDummyContent('item').__of__(site)
        self.assertEqual( item.listCreators(), () )
        item.setModificationDate(0)
        initial_date = item.ModificationDate()

        item.notifyModified()
        self.assertEqual( item.listCreators(), ('user_foo',) )
        self.assertNotEqual( item.ModificationDate(), initial_date )

    def test_creators_methods(self):
        site = DummySite('site').__of__(self.root)
        acl_users = site._setObject( 'acl_users', DummyUserFolder() )
        site._setObject( 'portal_membership', MembershipTool() )
        newSecurityManager(None, acl_users.user_foo)
        item = self._makeDummyContent('item').__of__(site)
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
        item.setCreators('user_bar')
        self.assertEqual( item.listCreators(), ('user_bar',) )
        item.setCreators( ('user_baz',) )
        self.assertEqual( item.listCreators(), ('user_baz',) )

    def test_ceiling_parsable(self):
        # Test that a None ceiling date will be parsable by a DateIndex
        site = DummySite('site').__of__(self.root)
        item = self._makeDummyContent('item').__of__(site)
        self.assertEqual(item.expiration_date, None)
        self.assert_(_DateIndexConvert(item.expires()))

    def test_publisher_no_metadata_tool(self):
        site = DummySite('site').__of__(self.root)
        item = self._makeDummyContent('item').__of__(site)
        self.assertEqual(item.Publisher(), 'No publisher')

    def test_publisher_with_metadata_tool(self):
        PUBLISHER = 'Some Publisher'
        site = DummySite('site').__of__(self.root)
        site.portal_metadata = DummyMetadataTool(publisher=PUBLISHER)
        item = self._makeDummyContent('item').__of__(site)
        self.assertEqual(item.Publisher(), PUBLISHER)

def test_suite():
    return TestSuite((
        makeSuite( DublinCoreTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
