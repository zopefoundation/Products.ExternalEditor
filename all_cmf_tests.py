import Zope
import unittest

from Products.CMFCore.tests import test_all
core_tests = test_all

from Products.CMFDefault.tests import test_all
default_tests = test_all

from Products.CMFTopic.tests import test_all
topic_tests = test_all

try:
    from Products.CMFCalendar.tests import test_all
    calendar_tests = test_all
except ImportError:
    calendar_tests = None

try:
    from Products.CMFDecor.tests import test_all
    decor_tests = test_all
except ImportError:
    decor_tests = None

try:
    from Products.DCWorfklow.tests import test_all
    workflow_tests = test_all
except ImportError:
    workflow_tests = None



def test_suite():

    suite = unittest.TestSuite()

    suite.addTest( core_tests.test_suite() )
    suite.addTest( default_tests.test_suite() )
    suite.addTest( topic_tests.test_suite() )

    if calendar_tests:
        suite.addTest( calendar_tests.test_suite() )

    if decor_tests:
        suite.addTest( decor_tests.test_suite() )

    if workflow_tests:
        suite.addTest( workflow_tests.test_suite() )

    return suite

def run():
    if hasattr( unittest, 'JUnitTextTestRunner' ):
        unittest.JUnitTextTestRunner().run( test_suite() )
    else:
        unittest.TextTestRunner( verbosity=1 ).run( test_suite() )

if __name__ == '__main__':
    run()

