import unittest
#from Products.CMFDecor.tests import test_Decor

def test_suite():
    suite = unittest.TestSuite()
    #suite.addTest( test_Decor.test_suite() )
    return suite

def run():
    unittest.JUnitTextTestRunner().run(test_suite())

if __name__ == '__main__':
    run()
