#!/usr/bin/env python

##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" CMF tests.

$Id$
"""

import unittest
import Testing
import Zope
Zope.startup()

import getopt
import sys

from Products.CMFCore.tests.base.utils import build_test_suite


#                  PackageName     Required?
CMF_PACKAGES = [ ( 'CMFCore',        1 )
               , ( 'CMFDefault',     1 )
               , ( 'CMFTopic',       1 )
               , ( 'DCWorkflow',     1 )
               , ( 'CMFActionIcons', 1 )
               , ( 'CMFSetup',       1 )
               , ( 'CMFUid',         1 )
               , ( 'CMFCalendar',    0 )
               ]

PACKAGES_UNDER_TEST = []

def test_suite():

    suite = unittest.TestSuite()

    packages = PACKAGES_UNDER_TEST or CMF_PACKAGES

    for package_name, required in packages:
        dotted = 'Products.%s.tests' % package_name
        suite.addTest( build_test_suite( dotted
                                       , [ 'test_all' ]
                                       , required=required
                                       , suite_name='suite'
                                       ) )

    return suite

def usage():

    USAGE = """\
all_cmf_tests.py [-?] <package_name>*

where

  package_name is the list of packages to be tested
  default: %s
"""

    print USAGE % CMF_PACKAGES
    sys.exit( 2 )

def main():

    try:
        opts, args = getopt.getopt( sys.argv[1:], 'vq?' )
    except getopt.GetoptError:
        usage()

    sys.argv[ 1: ] = []
    PASSTHROUGH = ( '-v', '-q' )

    for k, v in opts:

        if k in PASSTHROUGH:
            sys.argv.append( k )

        if k == '-?' or k == '--help':
            usage()

    for arg in args:
        PACKAGES_UNDER_TEST.append( ( arg, 1 ) )

    unittest.main(defaultTest='test_suite')


if __name__ == '__main__':
    main()
