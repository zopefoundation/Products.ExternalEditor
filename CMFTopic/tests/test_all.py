import unittest
from Products.CMFTopic.tests import test_Topic
from Products.CMFTopic.tests import test_DateC
from Products.CMFTopic.tests import test_ListC
from Products.CMFTopic.tests import test_SIC
from Products.CMFTopic.tests import test_SSC

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest( test_Topic.test_suite() )
    suite.addTest( test_DateC.test_suite() )
    suite.addTest( test_ListC.test_suite() )
    suite.addTest( test_SIC.test_suite() )
    suite.addTest( test_SSC.test_suite() )
    return suite

def run():
    unittest.JUnitTextTestRunner().run(test_suite())

if __name__ == '__main__':
    run()
