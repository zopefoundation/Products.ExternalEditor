""" CMFSetup tests.

$Id$
"""

from unittest import main
import Testing
import Zope
Zope.startup()

from Products.CMFCore.tests.base.utils import build_test_suite


def suite():
    return build_test_suite( 'Products.CMFSetup.tests'
                           , [ 'test_registry'
                             ,
                             ]
                           )

def test_suite():
    # Just to silence the top-level test.py
    return None

if __name__ == '__main__':
    main(defaultTest='suite')

