"""Currently all stub, no substance."""
import Zope
from unittest import TestSuite,main
from Products.CMFCore.tests.base.utils import build_test_suite

def test_suite():
    return TestSuite()

if __name__ == '__main__':
    main(defaultTest='test_suite')
