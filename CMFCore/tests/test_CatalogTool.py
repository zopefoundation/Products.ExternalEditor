from unittest import TestCase, TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()
from Interface.Verify import verifyClass

from Products.CMFCore.CatalogTool import CatalogTool
from Products.CMFCore.CatalogTool import IndexableObjectWrapper
from Products.CMFCore.tests.base.dummy import DummyContent


class IndexableObjectWrapperTests(TestCase):

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_catalog \
                import IndexableObjectWrapper as IIndexableObjectWrapper

        verifyClass(IIndexableObjectWrapper, IndexableObjectWrapper)


class CatalogToolTests( TestCase ):

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



def test_suite():
    return TestSuite((
        makeSuite( IndexableObjectWrapperTests ),
        makeSuite( CatalogToolTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
