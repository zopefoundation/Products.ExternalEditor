import Zope
from unittest import TestSuite,main
from Products.CMFCore.tests.base.utils import build_test_suite

def test_suite():

    # WHERE DID test_Decor GO? DID IT EVER EXIST?!
    # return build_test_suite('Products.CMFDecor.tests',['test_Decor'])
    return TestSuite()

if __name__ == '__main__':
    main(defaultTest='test_suite')
