import unittest
from Products.CMFTracker.tests.utils import *

class TestIssueDescription( BaseTrackerTestCase ):

    def setUp( self ):
        get_transaction().begin()

    def tearDown( self ):
        get_transaction().abort()

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
