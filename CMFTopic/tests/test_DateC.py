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
""" Unit tests for DateCriteria module.

$Id$
"""

from unittest import TestSuite, makeSuite, main
import Testing
import Zope2
Zope2.startup()

from DateTime.DateTime import DateTime

from common import CriterionTestCase


class FriendlyDateCriterionTests(CriterionTestCase):

    lessThanFiveDaysOld = { 'value': 4
                          , 'operation': 'min'
                          , 'daterange': 'old'
                          }

    lessThanOneMonthAhead = { 'value': 30
                            , 'operation': 'max'
                            , 'daterange': 'ahead'
                            }
    today = { 'value': 0
            , 'operation': 'within_day'
            , 'daterange': 'ahead'
            }

    def _getTargetClass(self):
        from Products.CMFTopic.DateCriteria import FriendlyDateCriterion

        return FriendlyDateCriterion

    def test_Empty( self ):
        friendly = self._makeOne('foo', 'foofield')

        self.assertEqual( friendly.getId(), 'foo' )
        self.assertEqual( friendly.field, 'foofield' )
        self.assertEqual( friendly.value, None )
        self.assertEqual( friendly.operation, 'min' )
        self.assertEqual( friendly.daterange, 'old' )
        self.assertEqual( len( friendly.getCriteriaItems() ), 0 )

    def test_ListOfDefaultDates( self ):
        friendly = self._makeOne('foo', 'foofield')

        d = friendly.defaultDateOptions()
        self.assertEqual( d[0][0], 0 )
        self.assertEqual( d[1][0], 1 )
        self.assertEqual( d[2][0], 2 )

    def test_Clear( self ):
        friendly = self._makeOne('foo', 'foofield')

        friendly.edit( value=None )
        self.assertEqual( friendly.value, None )
        self.assertEqual( friendly.operation, 'min' )
        self.assertEqual( friendly.daterange, 'old' )

    def test_Basic( self ):
        friendly = self._makeOne('foo', 'foofield')

        friendly.apply( self.lessThanFiveDaysOld )
        self.assertEqual( friendly.value, 4 )
        self.assertEqual( friendly.operation, 'min' )
        self.assertEqual( friendly.daterange, 'old' )

    def test_BadInput( self ):
        friendly = self._makeOne('foo', 'foofield')

        # Bogus value
        self.assertRaises( ValueError, friendly.edit, 'blah' )

        # Bogus operation
        self.assertRaises( ValueError, friendly.edit, 4, 'min:max', 'old' )

        # Bogus daterange
        self.assertRaises( ValueError, friendly.edit, 4, 'max', 'new' )

    def test_StringAsValue( self ):
        friendly = self._makeOne('foo', 'foofield')

        friendly.edit( '4' )
        self.assertEqual( friendly.value, 4 )

        friendly.edit( '-4' )
        self.assertEqual( friendly.value, -4 )

        friendly.edit( '' )
        self.assertEqual( friendly.value, None )

    def test_Today( self ):
        friendly = self._makeOne('foo', 'foofield')

        friendly.apply( self.today )
        self.assertEqual( friendly.daterange, 'ahead' )

        now = DateTime()

        result = friendly.getCriteriaItems()
        self.assertEqual( len(result), 1 )
        self.assertEqual( result[0][0], 'foofield' )
        self.assertEqual( result[0][1]['query'],
                          ( now.earliestTime(), now.latestTime() ) )
        self.assertEqual( result[0][1]['range'], 'min:max' )

    def test_FiveDaysOld( self ):
        friendly = self._makeOne('foo', 'foofield')

        friendly.apply( self.lessThanFiveDaysOld )
        self.assertEqual( friendly.daterange, 'old' )

        result = friendly.getCriteriaItems()
        self.assertEqual( len(result), 1 )
        self.assertEqual( result[0][0], 'foofield' )
        self.assertEqual( result[0][1]['query'].Date(),
                          ( DateTime() - 4 ).Date() )
        self.assertEqual( result[0][1]['range'], 'min' )

    def test_OneMonthAhead( self ):
        friendly = self._makeOne('foo', 'foofield')

        friendly.apply( self.lessThanOneMonthAhead )
        self.assertEqual( friendly.daterange, 'ahead' )

        result = friendly.getCriteriaItems()
        self.assertEqual( result[0][1]['query'].Date(),
                          ( DateTime() + 30 ).Date() )
        self.assertEqual( result[0][1]['range'], 'max' )


def test_suite():
    return TestSuite((
        makeSuite(FriendlyDateCriterionTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
