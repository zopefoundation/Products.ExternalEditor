"""Currently all stub, no substance."""
import unittest
from Products.CMFCore.tests.base.utils import build_test_suite

def test_suite():
    return unittest.TestSuite()

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
