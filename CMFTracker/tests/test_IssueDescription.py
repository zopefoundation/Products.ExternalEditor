import unittest
from Products.CMFTracker.tests.utils import *

class TestIssueDescription( BaseTrackerTestCase ):

    def test_null( self ): # validate 'test_all', base class, etc.
        pass

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite( TestIssueDescription ) )
    return suite

def run():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    run()
