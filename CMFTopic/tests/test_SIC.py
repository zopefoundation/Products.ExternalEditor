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
"""Unit tests for SimpleIntCriterion module.

$Id$
"""
__version__ = '$Revision$'[11:-2]

import unittest

class SimpleIntCriterionTests( unittest.TestCase ):

    def test_Interface( self ):
        from Products.CMFTopic.interfaces import Criterion
        from Products.CMFTopic.SimpleIntCriterion import SimpleIntCriterion
        self.failUnless(
            Criterion.isImplementedByInstancesOf( SimpleIntCriterion ) )

    def test_Empty( self ):

        from Products.CMFTopic.SimpleIntCriterion import SimpleIntCriterion

        sic = SimpleIntCriterion( 'foo', 'foofield' )
        self.assertEqual( sic.getId(), 'foo' )
        self.assertEqual( sic.field, 'foofield' )
        self.assertEqual( sic.value, None )
        self.assertEqual( sic.getValueString(), '' )
        self.assertEqual( len(sic.getCriteriaItems() ), 0 )
    
    def test_EditWithString( self ):

        from Products.CMFTopic.SimpleIntCriterion import SimpleIntCriterion

        sic = SimpleIntCriterion('foo', 'foofield')
        sic.edit('0')
        self.assertEqual( sic.value, 0 )
        self.assertEqual( sic.getValueString(), '0' )

        items = sic.getCriteriaItems()
        self.assertEqual( len( items ), 1 )
        self.assertEqual( len( items[0] ), 2 )
        self.assertEqual( items[0][0], 'foofield' )
        self.assertEqual( items[0][1], 0 )
    
    def test_EditWithInt( self ):

        from Products.CMFTopic.SimpleIntCriterion import SimpleIntCriterion

        sic = SimpleIntCriterion( 'foo', 'foofield' )
        sic.edit( 32 )
        self.assertEqual( sic.value, 32 )
        self.assertEqual( sic.getValueString(), '32' )

        items = sic.getCriteriaItems()
        self.assertEqual( len(items), 1 )
        self.assertEqual( len(items[0]), 2 )
        self.assertEqual( items[0][1], 32 )

    def test_RangeMin( self ):

        from Products.CMFTopic.SimpleIntCriterion import SimpleIntCriterion

        sic = SimpleIntCriterion( 'foo', 'foofield' )
        sic.edit( '32', SimpleIntCriterion.MINIMUM )

        self.assertEqual( sic.value, 32 )
        self.assertEqual( sic.getValueString(), '32' )

        items = sic.getCriteriaItems()
        self.assertEqual( len( items ), 2 )
        self.assertEqual( len( items[0] ), 2 )
        self.assertEqual( len( items[1] ), 2 )
        self.assertEqual( items[0][0], 'foofield' )
        self.assertEqual( items[0][1], 32 )
        self.assertEqual( items[1][0], 'foofield_usage' )
        self.assertEqual( items[1][1], 'range:min' )

    def test_RangeMin_withInt( self ):

        from Products.CMFTopic.SimpleIntCriterion import SimpleIntCriterion

        sic = SimpleIntCriterion( 'foo', 'foofield' )
        sic.edit( 32, SimpleIntCriterion.MINIMUM )

        self.assertEqual( sic.value, 32 )
        self.assertEqual( sic.getValueString(), '32' )

        items = sic.getCriteriaItems()
        self.assertEqual( len( items ), 2 )
        self.assertEqual( len( items[0] ), 2 )
        self.assertEqual( len( items[1] ), 2 )
        self.assertEqual( items[0][0], 'foofield' )
        self.assertEqual( items[0][1], 32 )
        self.assertEqual( items[1][0], 'foofield_usage' )
        self.assertEqual( items[1][1], 'range:min' )

    def test_RangeMax( self ):

        from Products.CMFTopic.SimpleIntCriterion import SimpleIntCriterion

        sic = SimpleIntCriterion( 'foo', 'foofield' )
        sic.edit( '32', SimpleIntCriterion.MAXIMUM )

        self.assertEqual( sic.value, 32 )
        self.assertEqual( sic.getValueString(), '32' )

        items = sic.getCriteriaItems()
        self.assertEqual( len( items ), 2 )
        self.assertEqual( len( items[0] ), 2 )
        self.assertEqual( len( items[1] ), 2 )
        self.assertEqual( items[0][0], 'foofield' )
        self.assertEqual( items[0][1], 32 )
        self.assertEqual( items[1][0], 'foofield_usage' )
        self.assertEqual( items[1][1], 'range:max' )

    def test_RangeMax_withInt( self ):

        from Products.CMFTopic.SimpleIntCriterion import SimpleIntCriterion

        sic = SimpleIntCriterion( 'foo', 'foofield' )
        sic.edit( 32, SimpleIntCriterion.MAXIMUM )

        self.assertEqual( sic.value, 32 )
        self.assertEqual( sic.getValueString(), '32' )

        items = sic.getCriteriaItems()
        self.assertEqual( len( items ), 2 )
        self.assertEqual( len( items[0] ), 2 )
        self.assertEqual( len( items[1] ), 2 )
        self.assertEqual( items[0][0], 'foofield' )
        self.assertEqual( items[0][1], 32 )
        self.assertEqual( items[1][0], 'foofield_usage' )
        self.assertEqual( items[1][1], 'range:max' )

    def test_RangeMinMax( self ):

        from Products.CMFTopic.SimpleIntCriterion import SimpleIntCriterion

        sic = SimpleIntCriterion( 'foo', 'foofield' )
        sic.edit( '32 34', SimpleIntCriterion.MINMAX )

        self.assertEqual( sic.value, ( 32, 34 ) )
        self.assertEqual( sic.getValueString(), '32 34' )

        items = sic.getCriteriaItems()
        self.assertEqual( len( items ), 2 )
        self.assertEqual( len( items[0] ), 2 )
        self.assertEqual( len( items[1] ), 2 )
        self.assertEqual( items[0][0], 'foofield' )
        self.assertEqual( items[0][1], ( 32, 34 ) )
        self.assertEqual( items[1][0], 'foofield_usage' )
        self.assertEqual( items[1][1], 'range:min:max' )

    def test_RangeMinMax_withTuple( self ):

        from Products.CMFTopic.SimpleIntCriterion import SimpleIntCriterion

        sic = SimpleIntCriterion( 'foo', 'foofield' )
        sic.edit( ( 32, 34 ), SimpleIntCriterion.MINMAX )

        self.assertEqual( sic.value, ( 32, 34 ) )
        self.assertEqual( sic.getValueString(), '32 34' )

        items = sic.getCriteriaItems()
        self.assertEqual( len( items ), 2 )
        self.assertEqual( len( items[0] ), 2 )
        self.assertEqual( len( items[1] ), 2 )
        self.assertEqual( items[0][0], 'foofield' )
        self.assertEqual( items[0][1], ( 32, 34 ) )
        self.assertEqual( items[1][0], 'foofield_usage' )
        self.assertEqual( items[1][1], 'range:min:max' )

def test_suite():
    return unittest.makeSuite( SimpleIntCriterionTests )

def main():
    unittest.TextTestRunner().run( test_suite() )

if __name__ == '__main__':
    main()
