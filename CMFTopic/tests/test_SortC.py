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
"""Unit tests for SortCriterion module.

$Id$
"""
__version__ = '$Revision$'[11:-2]

import unittest

class SortCriterionTests( unittest.TestCase ):

    def test_Interface( self ):
        from Products.CMFTopic.interfaces import Criterion
        from Products.CMFTopic.SortCriterion import SortCriterion
        self.failUnless(
            Criterion.isImplementedByInstancesOf( SortCriterion ) )
    
    def test_Empty( self ):

        from Products.CMFTopic.SortCriterion import SortCriterion
        ssc = SortCriterion( 'foo', 'foofield' )

        self.assertEqual( ssc.getId(), 'foo' )
        self.assertEqual( ssc.field, None )
        self.assertEqual( ssc.index, 'foofield' )
        self.assertEqual( ssc.Field(), 'foofield' )
        self.assertEqual( ssc.reversed, 0 )

        items = ssc.getCriteriaItems()
        self.assertEqual( len( items ), 1 )
        self.assertEqual( items[0][0], 'sort_on' )
        self.assertEqual( items[0][1], 'foofield' )
    
    def test_Nonempty( self ):

        from Products.CMFTopic.SortCriterion import SortCriterion
        ssc = SortCriterion( 'foo', 'foofield' )

        ssc.edit( 1 )

        self.assertEqual( ssc.getId(), 'foo' )
        self.assertEqual( ssc.field, None )
        self.assertEqual( ssc.index, 'foofield' )
        self.assertEqual( ssc.Field(), 'foofield' )
        self.assertEqual( ssc.reversed, 1 )

        items = ssc.getCriteriaItems()
        self.assertEqual( len( items ), 2 )
        self.assertEqual( items[0][0], 'sort_on' )
        self.assertEqual( items[0][1], 'foofield' )
        self.assertEqual( items[1][0], 'sort_order' )
        self.assertEqual( items[1][1], 'reverse' )

def test_suite():
    return unittest.makeSuite( SortCriterionTests )

def main():
    unittest.TextTestRunner().run( test_suite() )

if __name__ == '__main__':
    main()
    
