import Zope
from unittest import TestSuite,main
from Products.CMFCore.tests.base.utils import build_test_suite

def test_suite():    

    return TestSuite((
        build_test_suite('Products.CMFCore.tests',['test_all']),
        build_test_suite('Products.CMFDefault.tests',['test_all']),
        build_test_suite('Products.CMFTopic.tests',['test_all']),
        build_test_suite('Products.CMFCalendar.tests',['test_all'],required=0),
        build_test_suite('Products.CMFDecor.tests',['test_all'],required=0),
        build_test_suite('Products.DCWorkflow.tests',['test_all'],required=0),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')

