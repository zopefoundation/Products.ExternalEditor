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
"""Unit tests for ListCriterion module.

$Id$
"""
__version__ = '$Revision$'[11:-2]

import unittest

class ListCriterionTests( unittest.TestCase ):

    def test_Interface( self ):
        from Products.CMFTopic.interfaces import Criterion
        from Products.CMFTopic.ListCriterion import ListCriterion
        self.failUnless(
            Criterion.isImplementedByInstancesOf( ListCriterion ) )

    def test_Empty( self ):

        from Products.CMFTopic.ListCriterion import ListCriterion
        listc = ListCriterion('foo', 'foofield')

        self.assertEqual( listc.getId(), 'foo' )
        self.assertEqual( listc.field, 'foofield' )
        self.assertEqual( listc.value, ('',) )
        self.assertEqual( len(listc.getCriteriaItems()), 0 )
    
    def test_Edit_withString( self ):

        from Products.CMFTopic.ListCriterion import ListCriterion
        listc = ListCriterion( 'foo', 'foofield' )

        listc.edit('bar\nbaz')
        self.assertEqual( listc.getId(), 'foo' )
        self.assertEqual( listc.field, 'foofield' )
        self.assertEqual( listc.value, ( 'bar', 'baz' ) )

        items = listc.getCriteriaItems()
        self.assertEqual( len( items ), 1 )
        self.assertEqual( len( items[0] ), 2 )
        self.assertEqual( items[0][0], 'foofield' )
        self.assertEqual( items[0][1], ( 'bar', 'baz' ) )
    
    def test_Edit_withList( self ):

        from Products.CMFTopic.ListCriterion import ListCriterion
        listc = ListCriterion( 'foo', 'foofield' )

        abc = [ 'a', 'b', 'c' ]
        listc.edit( abc )

        items = listc.getCriteriaItems()
        self.assertEqual( items[0][1], tuple( abc ) )

def test_suite():
    return unittest.makeSuite( ListCriterionTests )

def main():
    unittest.TextTestRunner().run( test_suite() )

if __name__ == '__main__':
    main()
