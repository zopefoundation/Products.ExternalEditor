import unittest
from Products.CMFCalendar.tests import test_Event

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest( test_Event.test_suite() )
    return suite

def run():
    unittest.JUnitTextTestRunner().run(test_suite())

if __name__ == '__main__':
    run()
