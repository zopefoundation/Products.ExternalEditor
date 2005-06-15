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
""" Unit tests for SimpleStringCriterion module.

$Id$
"""

from unittest import TestSuite, makeSuite, main
import Testing
import Zope2
Zope2.startup()

from common import CriterionTestCase


class SimpleStringCriterionTests(CriterionTestCase):

    def _getTargetClass(self):
        from Products.CMFTopic.SimpleStringCriterion \
                import SimpleStringCriterion

        return SimpleStringCriterion

    def test_Empty( self ):
        ssc = self._makeOne('foo', 'foofield')

        self.assertEqual( ssc.getId(), 'foo' )
        self.assertEqual( ssc.field, 'foofield' )
        self.assertEqual( ssc.value, '' )
        self.assertEqual( len( ssc.getCriteriaItems() ), 0 )

    def test_Nonempty( self ):
        ssc = self._makeOne('foo', 'foofield')
        ssc.edit( 'bar' )

        self.assertEqual( ssc.getId(), 'foo' )
        self.assertEqual( ssc.field, 'foofield' )
        self.assertEqual( ssc.value, 'bar' )

        items = ssc.getCriteriaItems()

        self.assertEqual( len( items ), 1 )
        self.assertEqual( len( items[0] ), 2 )
        self.assertEqual( items[0][0], 'foofield' )
        self.assertEqual( items[0][1], 'bar' )


def test_suite():
    return TestSuite((
        makeSuite(SimpleStringCriterionTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
