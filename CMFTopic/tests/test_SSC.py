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
"""Unit tests for SimpleStringCriterion module.

$Id$
"""
__version__ = '$Revision$'[11:-2]

import unittest

class SimpleStringCriterionTests( unittest.TestCase ):

    def test_Interface( self ):
        from Products.CMFTopic.interfaces import Criterion
        from Products.CMFTopic.SimpleStringCriterion \
            import SimpleStringCriterion
        self.failUnless(
            Criterion.isImplementedByInstancesOf( SimpleStringCriterion ) )
    
    def test_Empty( self ):

        from Products.CMFTopic.SimpleStringCriterion \
            import SimpleStringCriterion

        ssc = SimpleStringCriterion( 'foo', 'foofield' )

        self.assertEqual( ssc.getId(), 'foo' )
        self.assertEqual( ssc.field, 'foofield' )
        self.assertEqual( ssc.value, '' )
        self.assertEqual( len( ssc.getCriteriaItems() ), 0 )
    
    def test_Nonempty( self ):

        from Products.CMFTopic.SimpleStringCriterion \
            import SimpleStringCriterion

        ssc = SimpleStringCriterion( 'foo', 'foofield' )
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
    return unittest.makeSuite( SimpleStringCriterionTests )

def main():
    unittest.TextTestRunner().run( test_suite() )

if __name__ == '__main__':
    main()
    
