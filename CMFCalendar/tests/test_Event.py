##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Unit tests for Event module.

$Id$
"""

from unittest import TestCase, TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()

from DateTime import DateTime

from Products.CMFCalendar.Event import Event
from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.dummy import DummyTool
from Products.CMFCore.tests.base.testcase import RequestTest


class TestEvent(TestCase):

    def setUp(self):
        self.site = DummySite('site')
        self.site._setObject( 'portal_membership', DummyTool() )

    def test_new(self):
        event = Event('test')
        assert event.getId() == 'test'
        assert not event.Title()

    def test_edit(self):
        event = self.site._setObject( 'testimage', Event('editing') )
        event.edit( title='title'
                  , description='description'
                  , eventType=( 'eventType', )
                  , effectiveDay=1
                  , effectiveMo=1
                  , effectiveYear=1999
                  , expirationDay=12
                  , expirationMo=31
                  , expirationYear=1999
                  , start_time="00:00"
                  , startAMPM="AM"
                  , stop_time="11:59"
                  , stopAMPM="PM"
                  )
        assert event.Title() == 'title'
        assert event.Description() == 'description'
        assert event.Subject() == ( 'eventType', ), event.Subject()
        assert event.effective_date == None
        assert event.expiration_date == None
        assert event.end() == DateTime('1999/12/31 23:59')
        assert event.start() == DateTime('1999/01/01 00:00')
        assert not event.contact_name

    def test_puke(self):
        event = Event( 'shouldPuke' )
        self.assertRaises( DateTime.DateError
                         , event.edit
                         , effectiveDay=31
                         , effectiveMo=2
                         , effectiveYear=1999
                         , start_time="00:00"
                         , startAMPM="AM"
                         )


class EventPUTTests(RequestTest):

    def setUp(self):
        RequestTest.setUp(self)
        self.site = DummySite('site')
        self.site._setObject( 'portal_membership', DummyTool() )

    def _makeOne(self, id, *args, **kw):
        return self.site._setObject( id, Event(id, *args, **kw) )

    def test_PutWithoutMetadata(self):
        self.REQUEST['BODY'] = ''
        d = self._makeOne('foo') 
        d.PUT(self.REQUEST, self.RESPONSE)
        self.assertEqual( d.Title(), '' )
        self.assertEqual( d.Format(), 'text/plain' )
        self.assertEqual( d.Description(), '' )
        self.assertEqual( d.Subject(), () )
        self.assertEqual( d.Contributors(), () )
        self.assertEqual( d.EffectiveDate(), 'None' )
        self.assertEqual( d.ExpirationDate(), 'None' )
        self.assertEqual( d.Language(), '' )
        self.assertEqual( d.Rights(), '' )


def test_suite():
    return TestSuite((
        makeSuite(TestEvent),
        makeSuite(EventPUTTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
