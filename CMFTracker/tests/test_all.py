import unittest
#from Products.CMFCore.tests import test_ContentTypeRegistry

def test_suite():
    suite = unittest.TestSuite()
    #suite.addTest( test_ContentTypeRegistry.test_suite() )
    return suite

def run():
    unittest.JUnitTextTestRunner().run(test_suite())

if __name__ == '__main__':
    run()
