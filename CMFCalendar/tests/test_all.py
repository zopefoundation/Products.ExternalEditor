import unittest
import Zope
from Products.CMFCore.tests.base.utils import build_test_suite

def test_suite():
    return build_test_suite('Products.CMFCalendar.tests',
                            ['test_Event',
                             'test_Calendar'])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
