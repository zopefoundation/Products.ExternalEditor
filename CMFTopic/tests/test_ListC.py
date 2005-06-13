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
""" Unit tests for ListCriterion module.

$Id$
"""

from unittest import TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()

from common import CriterionTestCase


class ListCriterionTests(CriterionTestCase):

    def _getTargetClass(self):
        from Products.CMFTopic.ListCriterion import ListCriterion

        return ListCriterion

    def test_Empty( self ):
        listc = self._makeOne('foo', 'foofield')

        self.assertEqual( listc.getId(), 'foo' )
        self.assertEqual( listc.field, 'foofield' )
        self.assertEqual( listc.value, ('',) )
        self.assertEqual( len(listc.getCriteriaItems()), 0 )

    def test_Edit_withString( self ):
        listc = self._makeOne('foo', 'foofield')

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
        listc = self._makeOne('foo', 'foofield')

        abc = [ 'a', 'b', 'c' ]
        listc.edit( abc )

        items = listc.getCriteriaItems()
        self.failUnless( 'foofield' in map( lambda x: x[0], items ) )
        self.failUnless( tuple( abc ) in map( lambda x: x[1], items ) )

    def test_operator( self ):
        listc = self._makeOne('foo', 'foofield')

        abc = [ 'a', 'b', 'c' ]

        listc.edit( abc )
        items = listc.getCriteriaItems()
        self.assertEqual( len( items ), 1 )

        listc.edit( abc, 'or' )
        items = listc.getCriteriaItems()
        self.assertEqual( len( items ), 2 )
        self.failUnless( ( 'foofield_operator', 'or' ) in items )

        listc.edit( abc, 'and' )
        items = listc.getCriteriaItems()
        self.assertEqual( len( items ), 2 )
        self.failUnless( ( 'foofield_operator', 'and' ) in items )


def test_suite():
    return TestSuite((
        makeSuite(ListCriterionTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
