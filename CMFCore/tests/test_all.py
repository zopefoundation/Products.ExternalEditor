import unittest
from Products.CMFCore.tests import test_ContentTypeRegistry
from Products.CMFCore.tests import test_PortalFolder

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest( test_ContentTypeRegistry.test_suite() )
    suite.addTest( test_PortalFolder.test_suite() )
    return suite

def run():
    unittest.JUnitTextTestRunner().run(test_suite())

if __name__ == '__main__':
    run()
