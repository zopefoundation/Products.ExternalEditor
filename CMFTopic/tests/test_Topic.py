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
""" Unit tests for Topic module.

$Id$
"""

from unittest import TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()

from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.testcase import SecurityTest
from Products.CMFCore.TypesTool import FactoryTypeInformation as FTI
from Products.CMFCore.TypesTool import TypesTool
from Products.CMFTopic.Topic import factory_type_information as FTIDATA_TOPIC
from Products.CMFTopic.Topic import Topic


class TestTopic(SecurityTest):
    """
        Test all the general Topic cases
    """

    def setUp(self):
        SecurityTest.setUp(self)
        self.site = DummySite('site').__of__(self.root)

    def _makeOne(self, id, *args, **kw):
        return self.site._setObject( id, Topic(id, *args, **kw) )

    def test_Empty( self ):
        topic = self._makeOne('top')

        query = topic.buildQuery()
        self.assertEqual( len( query ), 0 )

    def test_Simple( self ):
        topic = self._makeOne('top')
        topic.addCriterion( 'foo', 'String Criterion' )
        topic.getCriterion( 'foo' ).edit( 'bar' )

        query = topic.buildQuery()
        self.assertEqual( len(query), 1 )
        self.assertEqual( query['foo'], 'bar' )

        topic.addCriterion( 'baz', 'Integer Criterion' )
        topic.getCriterion( 'baz' ).edit( 43 )

        query = topic.buildQuery()
        self.assertEqual( len( query ), 2 )
        self.assertEqual( query[ 'foo' ], 'bar' )
        self.assertEqual( query[ 'baz' ], 43 )

    def test_Nested( self ):
        self.site._setObject( 'portal_types', TypesTool() )
        fti = FTIDATA_TOPIC[0].copy()
        self.site.portal_types._setObject( 'Topic', FTI(**fti) )
        topic = self._makeOne('top')
        topic._setPortalTypeName('Topic')

        topic.addCriterion( 'foo', 'String Criterion' )
        topic.getCriterion( 'foo' ).edit( 'bar' )

        topic.addSubtopic( 'qux' )
        subtopic = topic.qux

        subtopic.addCriterion( 'baz', 'String Criterion' )
        subtopic.getCriterion( 'baz' ).edit( 'bam' )

        query = subtopic.buildQuery()
        self.assertEqual( len( query ), 2 )
        self.assertEqual( query['foo'], 'bar' )
        self.assertEqual( query['baz'], 'bam' )

        subtopic.acquireCriteria = 0
        query = subtopic.buildQuery()
        self.assertEqual( len( query ), 1 )
        self.assertEqual( query['baz'], 'bam' )


def test_suite():
    return TestSuite((
        makeSuite(TestTopic),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
