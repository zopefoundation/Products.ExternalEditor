##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################
"""Unit tests for DateCriterion module.

$Id$
"""
__version__ = '$Revision$'[11:-2]

import unittest
from DateTime.DateTime import DateTime

class FriendlyDateCriterionTests( unittest.TestCase ):

    lessThanFiveDaysOld = { 'value': 4
                          , 'operation': 'min'
                          , 'daterange': 'old'
                          }

    lessThanOneMonthAhead = { 'value': 30
                            , 'operation': 'max'
                            , 'daterange': 'ahead'
                            }

    def test_Interface( self ):
        from Products.CMFTopic.interfaces import Criterion
        from Products.CMFTopic.DateCriteria import FriendlyDateCriterion
        self.failUnless(
            Criterion.isImplementedByInstancesOf( FriendlyDateCriterion ) )

    def test_Empty( self ):

        from Products.CMFTopic.DateCriteria import FriendlyDateCriterion
        friendly = FriendlyDateCriterion( 'foo', 'foofield' )

        self.assertEqual( friendly.getId(), 'foo' )
        self.assertEqual( friendly.field, 'foofield' )
        self.assertEqual( friendly.value, None )
        self.assertEqual( friendly.operation, 'min' )
        self.assertEqual( friendly.daterange, 'old' )
        self.assertEqual( len( friendly.getCriteriaItems() ), 0 )

    def test_ListOfDefaultDates( self ):

        from Products.CMFTopic.DateCriteria import FriendlyDateCriterion
        friendly = FriendlyDateCriterion( 'foo', 'foofield' )

        d = friendly.defaultDateOptions()
        self.assertEqual( d[1][0], 2 )

    def test_Clear( self ):

        from Products.CMFTopic.DateCriteria import FriendlyDateCriterion
        friendly = FriendlyDateCriterion( 'foo', 'foofield' )

        friendly.edit( value=None )
        self.assertEqual( friendly.value, None )
        self.assertEqual( friendly.operation, 'min' )
        self.assertEqual( friendly.daterange, 'old' )

    def test_Basic( self ):

        from Products.CMFTopic.DateCriteria import FriendlyDateCriterion
        friendly = FriendlyDateCriterion( 'foo', 'foofield' )
        
        friendly.apply( self.lessThanFiveDaysOld )
        self.assertEqual( friendly.value, 4 )
        self.assertEqual( friendly.operation, 'min' )
        self.assertEqual( friendly.daterange, 'old' )

    def test_BadInput( self ):

        from Products.CMFTopic.DateCriteria import FriendlyDateCriterion
        friendly = FriendlyDateCriterion( 'foo', 'foofield' )

        # Bogus value
        self.assertRaises( ValueError, friendly.edit, 'blah' )

        # Bogus operation
        self.assertRaises( ValueError, friendly.edit, 4, 'min:max', 'old' )

        # Bogus daterange
        self.assertRaises( ValueError, friendly.edit, 4, 'max', 'new' )

    def test_StringAsValue( self ):

        from Products.CMFTopic.DateCriteria import FriendlyDateCriterion
        friendly = FriendlyDateCriterion( 'foo', 'foofield' )

        friendly.edit( '4' )
        self.assertEqual( friendly.value, 4 )

        friendly.edit( '-4' )
        self.assertEqual( friendly.value, -4 )

        friendly.edit( '' )
        self.assertEqual( friendly.value, None )

    def test_FiveDaysOld( self ):

        from Products.CMFTopic.DateCriteria import FriendlyDateCriterion
        friendly = FriendlyDateCriterion( 'foo', 'foofield' )

        friendly.apply( self.lessThanFiveDaysOld )
        self.assertEqual( friendly.daterange, 'old' )
        
        result = friendly.getCriteriaItems()
        self.assertEqual( len( result ), 2 )
        self.assertEqual( result[0][0], 'foofield' )
        self.assertEqual( result[0][1].Date(), ( DateTime() - 4 ).Date() )
        self.assertEqual( result[1][0], 'foofield_usage' )
        self.assertEqual( result[1][1], 'range:min' )

    def test_OneMonthAhead( self ):

        from Products.CMFTopic.DateCriteria import FriendlyDateCriterion
        friendly = FriendlyDateCriterion( 'foo', 'foofield' )

        friendly.apply( self.lessThanOneMonthAhead )
        self.assertEqual( friendly.daterange, 'ahead' )

        result = friendly.getCriteriaItems()
        self.assertEqual( result[0][1].Date(), ( DateTime() + 30 ).Date() )
        self.assertEqual( result[1][1], 'range:max' )

def test_suite():
    return unittest.makeSuite( FriendlyDateCriterionTests )

def main():
    unittest.TextTestRunner().run( test_suite() )
    
if __name__ == '__main__':
    main()
