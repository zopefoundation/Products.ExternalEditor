from unittest import main

import Testing
import Zope
try:
    Zope.startup()
except AttributeError:
    # for Zope versions before 2.6.1
    pass

from Products.CMFCore.tests.base.utils import build_test_suite

def test_suite():
    return build_test_suite('Products.CMFCalendar.tests',
                            ['test_Event',
                             'test_Calendar'])

if __name__ == '__main__':
    main(defaultTest='test_suite')
