import Zope
from unittest import TestCase, TestSuite, makeSuite, main

from Products.CMFCore.tests.base.dummy import \
     DummyContent

from Products.CMFCore.CatalogTool import CatalogTool

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

def test_suite():
    return TestSuite((
        makeSuite( CatalogToolTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
