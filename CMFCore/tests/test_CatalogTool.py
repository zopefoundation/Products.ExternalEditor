import Zope
import unittest
import OFS.Folder, OFS.SimpleItem
import Acquisition
from Products.CMFCore.CatalogTool import *
from Products.CMFCore.PortalContent import PortalContent


class DummyContent( PortalContent, OFS.SimpleItem.Item ):
    """
    """
    meta_type = 'Dummy'

class CatalogToolTests( unittest.TestCase ):

    def setUp( self ):
        get_transaction().begin()
    
    def tearDown( self ):
        get_transaction().abort()

    def test_processActions( self ):
        """
            Tracker #405:  CatalogTool doesn't accept optional third
            argument, 'idxs', to 'catalog_object'.
        """
        tool = CatalogTool()
        dummy = DummyContent()

        tool.catalog_object( dummy, '/dummy' )
        tool.catalog_object( dummy, '/dummy', [ 'SearchableText' ] )

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite( CatalogToolTests ) )
    return suite

def run():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    run()
