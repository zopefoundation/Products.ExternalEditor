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
""" Unit tests for SimpleIntCriterion module.

$Id$
"""

from unittest import TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()

from common import CriterionTestCase


class SimpleIntCriterionTests(CriterionTestCase):

    def _getTargetClass(self):
        from Products.CMFTopic.SimpleIntCriterion import SimpleIntCriterion

        return SimpleIntCriterion

    def test_Empty( self ):
        sic = self._makeOne('foo', 'foofield')
        self.assertEqual( sic.getId(), 'foo' )
        self.assertEqual( sic.field, 'foofield' )
        self.assertEqual( sic.value, None )
        self.assertEqual( sic.getValueString(), '' )
        self.assertEqual( len(sic.getCriteriaItems() ), 0 )

    def test_EditWithString( self ):
        sic = self._makeOne('foo', 'foofield')
        sic.edit('0')
        self.assertEqual( sic.value, 0 )
        self.assertEqual( sic.getValueString(), '0' )

        items = sic.getCriteriaItems()
        self.assertEqual( len( items ), 1 )
        self.assertEqual( len( items[0] ), 2 )
        self.assertEqual( items[0][0], 'foofield' )
        self.assertEqual( items[0][1], 0 )

    def test_EditWithInt( self ):
        sic = self._makeOne('foo', 'foofield')
        sic.edit( 32 )
        self.assertEqual( sic.value, 32 )
        self.assertEqual( sic.getValueString(), '32' )

        items = sic.getCriteriaItems()
        self.assertEqual( len(items), 1 )
        self.assertEqual( len(items[0]), 2 )
        self.assertEqual( items[0][1], 32 )

    def test_RangeMin( self ):
        sic = self._makeOne('foo', 'foofield')
        sic.edit( '32', self._getTargetClass().MINIMUM )

        self.assertEqual( sic.value, 32 )
        self.assertEqual( sic.getValueString(), '32' )

        items = sic.getCriteriaItems()
        self.assertEqual( len(items), 1 )
        self.assertEqual( len( items[0] ), 2 )
        self.assertEqual( items[0][0], 'foofield' )
        self.assertEqual( items[0][1]['query'], 32 )
        self.assertEqual( items[0][1]['range'], 'min' )

    def test_RangeMin_withInt( self ):
        sic = self._makeOne('foo', 'foofield')
        sic.edit( 32, self._getTargetClass().MINIMUM )

        self.assertEqual( sic.value, 32 )
        self.assertEqual( sic.getValueString(), '32' )

        items = sic.getCriteriaItems()
        self.assertEqual( len(items), 1 )
        self.assertEqual( len( items[0] ), 2 )
        self.assertEqual( items[0][0], 'foofield' )
        self.assertEqual( items[0][1]['query'], 32 )
        self.assertEqual( items[0][1]['range'], 'min' )

    def test_RangeMax( self ):
        sic = self._makeOne('foo', 'foofield')
        sic.edit( '32', self._getTargetClass().MAXIMUM )

        self.assertEqual( sic.value, 32 )
        self.assertEqual( sic.getValueString(), '32' )

        items = sic.getCriteriaItems()
        self.assertEqual( len(items), 1 )
        self.assertEqual( len( items[0] ), 2 )
        self.assertEqual( items[0][0], 'foofield' )
        self.assertEqual( items[0][1]['query'], 32 )
        self.assertEqual( items[0][1]['range'], 'max' )

    def test_RangeMax_withInt( self ):
        sic = self._makeOne('foo', 'foofield')
        sic.edit( 32, self._getTargetClass().MAXIMUM )

        self.assertEqual( sic.value, 32 )
        self.assertEqual( sic.getValueString(), '32' )

        items = sic.getCriteriaItems()
        self.assertEqual( len(items), 1 )
        self.assertEqual( len( items[0] ), 2 )
        self.assertEqual( items[0][0], 'foofield' )
        self.assertEqual( items[0][1]['query'], 32 )
        self.assertEqual( items[0][1]['range'], 'max' )

    def test_RangeMinMax( self ):
        sic = self._makeOne('foo', 'foofield')
        sic.edit( '32 34', self._getTargetClass().MINMAX )

        self.assertEqual( sic.value, ( 32, 34 ) )
        self.assertEqual( sic.getValueString(), '32 34' )

        items = sic.getCriteriaItems()
        self.assertEqual( len(items), 1 )
        self.assertEqual( len( items[0] ), 2 )
        self.assertEqual( items[0][0], 'foofield' )
        self.assertEqual( items[0][1]['query'], ( 32, 34 ) )
        self.assertEqual( items[0][1]['range'], 'min:max' )

    def test_RangeMinMax_withTuple( self ):
        sic = self._makeOne('foo', 'foofield')
        sic.edit( ( 32, 34 ), self._getTargetClass().MINMAX )

        self.assertEqual( sic.value, ( 32, 34 ) )
        self.assertEqual( sic.getValueString(), '32 34' )

        items = sic.getCriteriaItems()
        self.assertEqual( len(items), 1 )
        self.assertEqual( len( items[0] ), 2 )
        self.assertEqual( items[0][0], 'foofield' )
        self.assertEqual( items[0][1]['query'], ( 32, 34 ) )
        self.assertEqual( items[0][1]['range'], 'min:max' )


def test_suite():
    return TestSuite((
        makeSuite(SimpleIntCriterionTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
