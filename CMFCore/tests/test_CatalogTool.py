from unittest import TestCase, TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()
from Interface.Verify import verifyClass

from DateTime import DateTime
from Products.CMFCore.CatalogTool import CatalogTool
from Products.CMFCore.CatalogTool import IndexableObjectWrapper
from Products.CMFCore.tests.base.dummy import DummyContent
from Products.CMFCore.tests.base.testcase import SecurityTest
from Products.CMFCore.tests.base.security import UserWithRoles
from Products.CMFCore.tests.base.security import OmnipotentUser
from AccessControl.SecurityManagement import newSecurityManager


class IndexableObjectWrapperTests(TestCase):

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_catalog \
                import IndexableObjectWrapper as IIndexableObjectWrapper

        verifyClass(IIndexableObjectWrapper, IndexableObjectWrapper)


class CatalogToolTests(SecurityTest):

    def loginWithRoles(self, *roles):
        user = UserWithRoles(*roles).__of__(self.root)
        newSecurityManager(None, user)

    def loginManager(self):
        user = OmnipotentUser().__of__(self.root)
        newSecurityManager(None, user)

    def test_processActions( self ):
        """
            Tracker #405:  CatalogTool doesn't accept optional third
            argument, 'idxs', to 'catalog_object'.
        """
        tool = CatalogTool()
        dummy = DummyContent(catalog=1)

        tool.catalog_object( dummy, '/dummy' )
        tool.catalog_object( dummy, '/dummy', [ 'SearchableText' ] )

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_catalog \
                import portal_catalog as ICatalogTool
        from Products.CMFCore.interfaces.portal_actions \
                import ActionProvider as IActionProvider
        from Products.ZCatalog.IZCatalog import IZCatalog

        verifyClass(ICatalogTool, CatalogTool)
        verifyClass(IActionProvider, CatalogTool)
        verifyClass(IZCatalog, CatalogTool)

    def test_search_anonymous(self):
        catalog = CatalogTool()
        dummy = DummyContent(catalog=1)
        catalog.catalog_object(dummy, '/dummy')

        self.assertEqual(1, len(catalog._catalog.searchResults()))
        self.assertEqual(0, len(catalog.searchResults()))

    def test_search_inactive(self):
        catalog = CatalogTool()
        now = DateTime()
        dummy = DummyContent(catalog=1)
        dummy._View_Permission = ('Blob',)

        self.loginWithRoles('Blob')

        # not yet effective
        dummy.effective = now+1
        dummy.expires = now+2
        catalog.catalog_object(dummy, '/dummy')
        self.assertEqual(1, len(catalog._catalog.searchResults()))
        self.assertEqual(0, len(catalog.searchResults()))

        # already expired
        dummy.effective = now-2
        dummy.expires = now-1
        catalog.catalog_object(dummy, '/dummy')
        self.assertEqual(1, len(catalog._catalog.searchResults()))
        self.assertEqual(0, len(catalog.searchResults()))

    def test_search_restrict_manager(self):
        catalog = CatalogTool()
        now = DateTime()
        dummy = DummyContent(catalog=1)

        self.loginManager()

        # already expired
        dummy.effective = now-4
        dummy.expires = now-2
        catalog.catalog_object(dummy, '/dummy')
        self.assertEqual(1, len(catalog._catalog.searchResults()))
        self.assertEqual(1, len(catalog.searchResults()))

        self.assertEqual(1, len(catalog.searchResults(
            expires={'query': now-3, 'range': 'min'})))
        self.assertEqual(0, len(catalog.searchResults(
            expires={'query': now-1, 'range': 'min'})))
        self.assertEqual(0, len(catalog.searchResults(
            expires={'query': now-3, 'range': 'max'})))
        self.assertEqual(1, len(catalog.searchResults(
            expires={'query': now-1, 'range': 'max'})))
        self.assertEqual(1, len(catalog.searchResults(
            expires={'query': (now-3, now-1), 'range': 'min:max'})))

    def test_search_restrict_inactive(self):
        catalog = CatalogTool()
        now = DateTime()
        dummy = DummyContent(catalog=1)
        dummy._View_Permission = ('Blob',)

        self.loginWithRoles('Blob')

        # already expired
        dummy.effective = now-4
        dummy.expires = now-2
        catalog.catalog_object(dummy, '/dummy')
        self.assertEqual(1, len(catalog._catalog.searchResults()))
        self.assertEqual(0, len(catalog.searchResults()))

        self.assertEqual(0, len(catalog.searchResults(
            expires={'query': now-3, 'range': 'min'})))
        self.assertEqual(0, len(catalog.searchResults(
            expires={'query': now-3, 'range': 'max'})))
        self.assertEqual(0, len(catalog.searchResults(
            expires={'query': now+3, 'range': 'min'})))
        self.assertEqual(0, len(catalog.searchResults(
            expires={'query': now+3, 'range': 'max'})))
        self.assertEqual(0, len(catalog.searchResults(
            expires={'query': (now-3, now-1), 'range': 'min:max'})))

    def test_search_restrict_visible(self):
        catalog = CatalogTool()
        now = DateTime()
        dummy = DummyContent(catalog=1)
        dummy._View_Permission = ('Blob',)

        self.loginWithRoles('Blob')

        # visible
        dummy.effective = now-2
        dummy.expires = now+2
        catalog.catalog_object(dummy, '/dummy')
        self.assertEqual(1, len(catalog._catalog.searchResults()))
        self.assertEqual(1, len(catalog.searchResults()))

        self.assertEqual(0, len(catalog.searchResults(
            effective={'query': now-1, 'range': 'min'})))
        self.assertEqual(1, len(catalog.searchResults(
            effective={'query': now-1, 'range': 'max'})))
        self.assertEqual(0, len(catalog.searchResults(
            effective={'query': now+1, 'range': 'min'})))
        self.assertEqual(1, len(catalog.searchResults(
            effective={'query': now+1, 'range': 'max'})))
        self.assertEqual(0, len(catalog.searchResults(
            effective={'query': (now-1, now+1), 'range': 'min:max'})))

        self.assertEqual(1, len(catalog.searchResults(
            effective={'query': now-3, 'range': 'min'})))
        self.assertEqual(0, len(catalog.searchResults(
            effective={'query': now-3, 'range': 'max'})))
        self.assertEqual(0, len(catalog.searchResults(
            effective={'query': now+3, 'range': 'min'})))
        self.assertEqual(1, len(catalog.searchResults(
            effective={'query': now+3, 'range': 'max'})))
        self.assertEqual(1, len(catalog.searchResults(
            effective={'query': (now-3, now+3), 'range': 'min:max'})))

        self.assertEqual(1, len(catalog.searchResults(
            expires={'query': now-1, 'range': 'min'})))
        self.assertEqual(0, len(catalog.searchResults(
            expires={'query': now-1, 'range': 'max'})))
        self.assertEqual(1, len(catalog.searchResults(
            expires={'query': now+1, 'range': 'min'})))
        self.assertEqual(0, len(catalog.searchResults(
            expires={'query': now+1, 'range': 'max'})))
        self.assertEqual(0, len(catalog.searchResults(
            expires={'query': (now-1, now+1), 'range': 'min:max'})))

        self.assertEqual(1, len(catalog.searchResults(
            expires={'query': now-3, 'range': 'min'})))
        self.assertEqual(0, len(catalog.searchResults(
            expires={'query': now-3, 'range': 'max'})))
        self.assertEqual(0, len(catalog.searchResults(
            expires={'query': now+3, 'range': 'min'})))
        self.assertEqual(1, len(catalog.searchResults(
            expires={'query': now+3, 'range': 'max'})))
        self.assertEqual(1, len(catalog.searchResults(
            expires={'query': (now-3, now+3), 'range': 'min:max'})))

        self.assertEqual(1, len(catalog.searchResults(
            effective={'query': now-1, 'range': 'max'},
            expires={'query': now+1, 'range': 'min'})))

        self.assertEqual(0, len(catalog.searchResults(
            effective={'query': now+1, 'range': 'max'},
            expires={'query': now+3, 'range': 'min'})))

    def test_convertQuery(self):
        convert = CatalogTool()._convertQuery

        kw = {}
        convert(kw)
        self.assertEqual(kw, {})

        kw = {'expires': 5, 'expires_usage': 'brrr:min'}
        self.assertRaises(ValueError, convert, kw)

        kw = {'foo': 'bar'}
        convert(kw)
        self.assertEqual(kw, {'foo': 'bar'})

        kw = {'expires': 5, 'expires_usage': 'range:min'}
        convert(kw)
        self.assertEqual(kw, {'expires': {'query': 5, 'range': 'min'}})

        kw = {'expires': 5, 'expires_usage': 'range:max'}
        convert(kw)
        self.assertEqual(kw, {'expires': {'query': 5, 'range': 'max'}})

        kw = {'expires': (5,7), 'expires_usage': 'range:min:max'}
        convert(kw)
        self.assertEqual(kw, {'expires': {'query': (5,7), 'range': 'min:max'}})


def test_suite():
    return TestSuite((
        makeSuite( IndexableObjectWrapperTests ),
        makeSuite( CatalogToolTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
