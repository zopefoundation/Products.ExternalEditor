import unittest
from Products.CMFTopic.tests import test_Topic, test_DateC, test_ListC, \
     test_SIC, test_SSC

def main():
    suite = unittest.TestSuite((
        test_Topic.test_suite(),
        test_DateC.test_suite(),
        test_ListC.test_suite(),
        test_SIC.test_suite(),
        test_SSC.test_suite(),
        ))
    unittest.TextTestRunner().run(suite)

if __name__ == '__main__':
    main()
    
