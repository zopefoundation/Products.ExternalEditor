##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Unit tests for CalendarTool module.

$Id$
"""

import unittest
import Testing
try:
    import Zope2
except ImportError:
    # BBB: for Zope 2.7
    import Zope as Zope2
Zope2.startup()

import locale

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.User import UnrestrictedUser
from DateTime import DateTime
from Products.TemporaryFolder.TemporaryFolder import MountedTemporaryFolder
from Products.Transience.Transience import TransientObjectContainer
from Testing.makerequest import makerequest
try:
    import transaction
except ImportError:
    # BBB: for Zope 2.7
    from Products.CMFCore.utils import transaction


class CalendarTests(unittest.TestCase):

    def _makeOne(self, *args, **kw):
        from Products.CMFCalendar.CalendarTool import CalendarTool

        return CalendarTool(*args, **kw)

    def test_new(self):
        ctool = self._makeOne()
        self.assertEqual( ctool.getId(), 'portal_calendar' )

    def test_types(self):
        ctool = self._makeOne()
        self.assertEqual(ctool.getCalendarTypes(), ('Event',))

        ctool.edit_configuration(show_types=['Event','Party'],
                                 show_states=[],
                                 use_session="")
        self.assertEqual( ctool.getCalendarTypes(), ('Event', 'Party') )

    def test_states(self):
        ctool = self._makeOne()
        self.assertEqual(ctool.getCalendarStates(), ('published',))

        ctool.edit_configuration(show_types=[],
                                 show_states=['pending', 'published'],
                                 use_session="")
        self.assertEqual( ctool.getCalendarStates(), ('pending', 'published') )

    def test_days(self):
        ctool = self._makeOne()
        old_locale = locale.getlocale(locale.LC_ALL)[0]
        locale.setlocale(locale.LC_ALL, 'C')
        try:
            self.assertEqual( ctool.getDays(),
                              ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'] )
        finally:
            locale.setlocale(locale.LC_ALL, old_locale)


class CalendarRequestTests(unittest.TestCase):

    def setUp(self):
        transaction.begin()

        app = self.app = makerequest(Zope2.app())
        # Log in as a god :-)
        newSecurityManager( None, UnrestrictedUser('god', 'god', ['Manager'], '') )

        factory = app.manage_addProduct['CMFSetup'].addConfiguredSite
        factory('CalendarTest', 'CMFDefault:default', snapshot=False,
                extension_ids=('CMFCalendar:default',))
        self.Site = app.CalendarTest
        self.Tool = app.CalendarTest.portal_calendar

        # sessioning setup
        if getattr(app, 'temp_folder', None) is None:
            temp_folder = MountedTemporaryFolder('temp_folder')
            app._setObject('temp_folder', temp_folder)
        if getattr(app.temp_folder, 'session_data', None) is None:
            session_data = TransientObjectContainer('session_data')
            app.temp_folder._setObject('session_data', session_data)
        app.REQUEST.set_lazy( 'SESSION',
                              app.session_data_manager.getSessionData )

    def tearDown(self):
        noSecurityManager()
        transaction.abort()
        self.app._p_jar.close()

    def _testURL(self,url,params=None):
        Site = self.Site
        obj = Site.restrictedTraverse(url)
        if params is None:
            params=(obj, Site.REQUEST)
        obj(*params)

    def test_sessions(self):
        self.Tool.edit_configuration(show_types=['Event'], use_session="True")

        self._testURL('/CalendarTest/calendarBox', ())

        self.failUnless(self.app.REQUEST.SESSION.get('calendar_year',None))

    def test_noSessions(self):
        self.Tool.edit_configuration(show_types=['Event'], use_session="")

        self._testURL('/CalendarTest/calendarBox', ())

        self.failIf(self.app.REQUEST.SESSION.get('calendar_year',None))

    def test_simpleCalendarRendering(self):
        data = [
                [
                 {'day': 0, 'event': 0, 'eventslist':[]},
                 {'day': 0, 'event': 0, 'eventslist':[]},
                 {'day': 0, 'event': 0, 'eventslist':[]},
                 {'day': 1, 'event': 0, 'eventslist':[]},
                 {'day': 2, 'event': 0, 'eventslist':[]},
                 {'day': 3, 'event': 0, 'eventslist':[]},
                 {'day': 4, 'event': 0, 'eventslist':[]},
                 ],
                [
                 {'day': 5, 'event': 0, 'eventslist':[]},
                 {'day': 6, 'event': 0, 'eventslist':[]},
                 {'day': 7, 'event': 0, 'eventslist':[]},
                 {'day': 8, 'event': 0, 'eventslist':[]},
                 {'day': 9, 'event': 0, 'eventslist':[]},
                 {'day':10, 'event': 0, 'eventslist':[]},
                 {'day':11, 'event': 0, 'eventslist':[]},
                 ],
                [
                 {'day':12, 'event': 0, 'eventslist':[]},
                 {'day':13, 'event': 0, 'eventslist':[]},
                 {'day':14, 'event': 0, 'eventslist':[]},
                 {'day':15, 'event': 0, 'eventslist':[]},
                 {'day':16, 'event': 0, 'eventslist':[]},
                 {'day':17, 'event': 0, 'eventslist':[]},
                 {'day':18, 'event': 0, 'eventslist':[]},
                 ],
                [
                 {'day':19, 'event': 0, 'eventslist':[]},
                 {'day':20, 'event': 0, 'eventslist':[]},
                 {'day':21, 'event': 0, 'eventslist':[]},
                 {'day':22, 'event': 0, 'eventslist':[]},
                 {'day':23, 'event': 0, 'eventslist':[]},
                 {'day':24, 'event': 0, 'eventslist':[]},
                 {'day':25, 'event': 0, 'eventslist':[]},
                 ],
                [
                 {'day':26, 'event': 0, 'eventslist':[]},
                 {'day':27, 'event': 0, 'eventslist':[]},
                 {'day':28, 'event': 0, 'eventslist':[]},
                 {'day':29, 'event': 0, 'eventslist':[]},
                 {'day':30, 'event': 0, 'eventslist':[]},
                 {'day':31, 'event': 0, 'eventslist':[]},
                 {'day': 0, 'event': 0, 'eventslist':[]},
                 ]
                ]
        result = self.Tool.getEventsForCalendar(month='5', year='2002')
        self.assertEqual(result, data)

    def test_singleEventCalendarRendering(self):

        self.Site.Members.invokeFactory(type_name="Event",id='Event1')
        event = self.app.restrictedTraverse('/CalendarTest/Members/Event1')
        event.edit( title='title'
                    , description='description'
                    , eventType=( 'eventType', )
                    , effectiveDay=1
                    , effectiveMo=5
                    , effectiveYear=2002
                    , expirationDay=1
                    , expirationMo=5
                    , expirationYear=2002
                    , start_time="00:00"
                    , startAMPM="AM"
                    , stop_time="11:59"
                    , stopAMPM="PM"
                    )
        self.Site.portal_workflow.doActionFor(
                                              event,
                                              'publish',
                                              comment='testing')

        data = [
                [
                 {'day': 0, 'event': 0, 'eventslist':[]},
                 {'day': 0, 'event': 0, 'eventslist':[]},
                 {'day': 0, 'event': 0, 'eventslist':[]},
                 {'day': 1, 'event': 1, 'eventslist':[{'title': 'title', 'end': '23:59:00', 'start': '00:00:00'}]},
                 {'day': 2, 'event': 0, 'eventslist':[]},
                 {'day': 3, 'event': 0, 'eventslist':[]},
                 {'day': 4, 'event': 0, 'eventslist':[]},
                 ],
                [
                 {'day': 5, 'event': 0, 'eventslist':[]},
                 {'day': 6, 'event': 0, 'eventslist':[]},
                 {'day': 7, 'event': 0, 'eventslist':[]},
                 {'day': 8, 'event': 0, 'eventslist':[]},
                 {'day': 9, 'event': 0, 'eventslist':[]},
                 {'day':10, 'event': 0, 'eventslist':[]},
                 {'day':11, 'event': 0, 'eventslist':[]},
                 ],
                [
                 {'day':12, 'event': 0, 'eventslist':[]},
                 {'day':13, 'event': 0, 'eventslist':[]},
                 {'day':14, 'event': 0, 'eventslist':[]},
                 {'day':15, 'event': 0, 'eventslist':[]},
                 {'day':16, 'event': 0, 'eventslist':[]},
                 {'day':17, 'event': 0, 'eventslist':[]},
                 {'day':18, 'event': 0, 'eventslist':[]},
                 ],
                [
                 {'day':19, 'event': 0, 'eventslist':[]},
                 {'day':20, 'event': 0, 'eventslist':[]},
                 {'day':21, 'event': 0, 'eventslist':[]},
                 {'day':22, 'event': 0, 'eventslist':[]},
                 {'day':23, 'event': 0, 'eventslist':[]},
                 {'day':24, 'event': 0, 'eventslist':[]},
                 {'day':25, 'event': 0, 'eventslist':[]},
                 ],
                [
                 {'day':26, 'event': 0, 'eventslist':[]},
                 {'day':27, 'event': 0, 'eventslist':[]},
                 {'day':28, 'event': 0, 'eventslist':[]},
                 {'day':29, 'event': 0, 'eventslist':[]},
                 {'day':30, 'event': 0, 'eventslist':[]},
                 {'day':31, 'event': 0, 'eventslist':[]},
                 {'day': 0, 'event': 0, 'eventslist':[]},
                 ]
                ]
        result = self.Tool.getEventsForCalendar(month='5', year='2002')
        self.assertEqual(result, data)

    def test_spanningEventCalendarRendering(self):

        self.Site.Members.invokeFactory(type_name="Event",id='Event1')
        event = self.app.restrictedTraverse('/CalendarTest/Members/Event1')
        event.edit( title='title'
                    , description='description'
                    , eventType=( 'eventType', )
                    , effectiveDay=1
                    , effectiveMo=5
                    , effectiveYear=2002
                    , expirationDay=31
                    , expirationMo=5
                    , expirationYear=2002
                    , start_time="00:00"
                    , startAMPM="AM"
                    , stop_time="11:59"
                    , stopAMPM="PM"
                    )
        self.Site.portal_workflow.doActionFor(
                                              event,
                                              'publish',
                                              comment='testing')

        data = [
                [
                 {'day': 0, 'event': 0, 'eventslist':[]},
                 {'day': 0, 'event': 0, 'eventslist':[]},
                 {'day': 0, 'event': 0, 'eventslist':[]},
                 {'day': 1, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': '00:00:00'}]},
                 {'day': 2, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day': 3, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day': 4, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 ],
                [
                 {'day': 5, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day': 6, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day': 7, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day': 8, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day': 9, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':10, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':11, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 ],
                [
                 {'day':12, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':13, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':14, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':15, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':16, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':17, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':18, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 ],
                [
                 {'day':19, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':20, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':21, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':22, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':23, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':24, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':25, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 ],
                [
                 {'day':26, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':27, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':28, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':29, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':30, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':31, 'event': 1, 'eventslist':[{'title': 'title', 'end': '23:59:00', 'start': None}]},
                 {'day': 0, 'event': 0, 'eventslist':[]},
                 ]
                ]
        result = self.Tool.getEventsForCalendar(month='5', year='2002')
        self.assertEqual(result, data)

    def test_getPreviousMonth(self):
        self.assertEqual( self.Tool.getPreviousMonth(2,2002),
                          DateTime('2002/1/1') )
        self.assertEqual( self.Tool.getPreviousMonth(1,2002),
                          DateTime('2001/12/1') )

    def test_getNextMonth(self):
        self.assertEqual( self.Tool.getNextMonth(12,2001),
                          DateTime('2002/1/1') )
        self.assertEqual( self.Tool.getNextMonth(1,2002),
                          DateTime('2002/2/1') )

    def test_getBeginAndEndTimes(self):
        self.assertEqual( self.Tool.getBeginAndEndTimes(1,12,2001),
                          ( DateTime('2001/12/1 12:00:00AM'),
                            DateTime('2001/12/1 11:59:59PM') ) )

    def test_singleDayRendering(self):
        wftool = self.Site.portal_workflow

        self.Site.Members.invokeFactory(type_name="Event",id='Event1')
        event = self.Site.Members.Event1
        event.edit( title='title'
                    , description='description'
                    , eventType=( 'eventType', )
                    , effectiveDay=1
                    , effectiveMo=5
                    , effectiveYear=2002
                    , expirationDay=31
                    , expirationMo=5
                    , expirationYear=2002
                    , start_time="00:00"
                    , startAMPM="AM"
                    , stop_time="11:59"
                    , stopAMPM="PM"
                    )
        wftool.doActionFor(event, 'publish', comment='testing')
        events = self.Tool.getEventsForThisDay(thisDay=DateTime('2002/5/1'))
        self.assertEqual( len(events), 1 )

        self.Site.Members.invokeFactory(type_name="Event",id='Event2')
        event = self.Site.Members.Event2
        event.edit( title='title'
                    , description='description'
                    , eventType=( 'eventType', )
                    , effectiveDay=1
                    , effectiveMo=5
                    , effectiveYear=2002
                    , expirationDay=1
                    , expirationMo=5
                    , expirationYear=2002
                    , start_time="00:00"
                    , startAMPM="AM"
                    , stop_time="11:59"
                    , stopAMPM="PM"
                    )
        wftool.doActionFor(event, 'publish', comment='testing')
        events = self.Tool.getEventsForThisDay(thisDay=DateTime('2002/5/1'))
        self.assertEqual( len(events), 2 )

        self.Site.Members.invokeFactory(type_name="Event",id='Event3')
        event = self.Site.Members.Event3
        event.edit( title='title'
                    , description='description'
                    , eventType=( 'eventType', )
                    , effectiveDay=12
                    , effectiveMo=12
                    , effectiveYear=2001
                    , expirationDay=1
                    , expirationMo=5
                    , expirationYear=2002
                    , start_time="00:00"
                    , startAMPM="AM"
                    , stop_time="11:59"
                    , stopAMPM="PM"
                    )
        wftool.doActionFor(event, 'publish', comment='testing')
        events = self.Tool.getEventsForThisDay(thisDay=DateTime('2002/5/1'))
        self.assertEqual( len(events), 3 )

        self.Site.Members.invokeFactory(type_name="Event",id='Event4')
        event = self.Site.Members.Event4
        event.edit( title='title'
                    , description='description'
                    , eventType=( 'eventType', )
                    , effectiveDay=12
                    , effectiveMo=12
                    , effectiveYear=2001
                    , expirationDay=31
                    , expirationMo=5
                    , expirationYear=2002
                    , start_time="00:00"
                    , startAMPM="AM"
                    , stop_time="11:59"
                    , stopAMPM="PM"
                    )
        wftool.doActionFor(event, 'publish', comment='testing')
        events = self.Tool.getEventsForThisDay(thisDay=DateTime('2002/5/1'))
        self.assertEqual( len(events), 4 )

        self.Site.Members.invokeFactory(type_name="Event",id='Event5')
        event = self.Site.Members.Event5
        event.edit( title='title'
                    , description='description'
                    , eventType=( 'eventType', )
                    , effectiveDay=31
                    , effectiveMo=5
                    , effectiveYear=2002
                    , expirationDay=31
                    , expirationMo=5
                    , expirationYear=2002
                    , start_time="00:00"
                    , startAMPM="AM"
                    , stop_time="11:59"
                    , stopAMPM="PM"
                    )
        wftool.doActionFor(event, 'publish', comment='testing')
        events = self.Tool.getEventsForThisDay(thisDay=DateTime('2002/5/1'))
        self.assertEqual( len(events), 4 )
        events = self.Tool.getEventsForThisDay(thisDay=DateTime('2002/5/31'))
        self.assertEqual( len(events), 3 )

    def test_lastDayRendering(self):
        # Bug in catalog_getevents included events starting at 00:00:00 on the next day

        self.Site.invokeFactory('Event', id='today', title='today',
                                 start_date='2002/05/31 23:50:00', 
                                 end_date='2002/05/31 23:59:59')

        self.Site.invokeFactory('Event', id='tomorrow', title='tomorrow',
                                 start_date='2002/06/01 00:00:00', 
                                 end_date='2002/06/01 00:10:00')

        self.Site.portal_workflow.doActionFor(self.Site.today, 'publish')
        self.Site.portal_workflow.doActionFor(self.Site.tomorrow, 'publish')

        # Last week of May 2002
        data = [
               {'day': 25, 'event': 0, 'eventslist':[]},
               {'day': 26, 'event': 0, 'eventslist':[]},
               {'day': 27, 'event': 0, 'eventslist':[]},
               {'day': 28, 'event': 0, 'eventslist':[]},
               {'day': 29, 'event': 0, 'eventslist':[]},
               {'day': 30, 'event': 0, 'eventslist':[]},
               {'day': 31, 'event': 1, 'eventslist':[{'start': '23:50:00', 'end': '23:59:59', 'title': 'today'}]},
               ]

        events = self.Site.portal_calendar.catalog_getevents(2002, 5)
        self.assertEqual([events[e] for e in range(25, 32)], data)

    def test_firstDayRendering(self):
        # Double check it works on the other boundary as well

        self.Site.invokeFactory('Event', id='yesterday', title='yesterday',
                                 start_date='2002/05/31 23:50:00', 
                                 end_date='2002/05/31 23:59:59')

        self.Site.invokeFactory('Event', id='today', title='today',
                                 start_date='2002/06/01 00:00:00', 
                                 end_date='2002/06/01 00:10:00')

        self.Site.portal_workflow.doActionFor(self.Site.yesterday, 'publish')
        self.Site.portal_workflow.doActionFor(self.Site.today, 'publish')

        # First week of June 2002
        data = [
               {'day': 1, 'event': 1, 'eventslist':[{'start': '00:00:00', 'end': '00:10:00', 'title': 'today'}]},
               {'day': 2, 'event': 0, 'eventslist':[]},
               {'day': 3, 'event': 0, 'eventslist':[]},
               {'day': 4, 'event': 0, 'eventslist':[]},
               {'day': 5, 'event': 0, 'eventslist':[]},
               {'day': 6, 'event': 0, 'eventslist':[]},
               {'day': 7, 'event': 0, 'eventslist':[]},
               ]

        events = self.Site.portal_calendar.catalog_getevents(2002, 6)
        self.assertEqual([events[e] for e in range(1, 8)], data)

    def test_workflowStateRendering(self):
        # Calendar should return events in all of the selected workflow states

        self.Site.invokeFactory('Event', id='meeting',
                                 start_date='2002/05/01 11:00:00', 
                                 end_date='2002/05/01 13:30:00')

        self.Site.invokeFactory('Event', id='dinner',
                                 start_date='2002/05/01 20:00:00', 
                                 end_date='2002/05/01 22:00:00')

        self.assertEqual(len(self.Site.portal_catalog(portal_type='Event')), 2)

        # No published events
        self.assertEqual(len(self.Site.portal_calendar.getEventsForThisDay(DateTime('2002/05/01'))), 0) 
        
        # One published event
        self.Site.portal_workflow.doActionFor(self.Site.meeting, 'publish')
        self.assertEqual(len(self.Site.portal_catalog(review_state='published')), 1)

        self.assertEqual(len(self.Site.portal_calendar.getEventsForThisDay(DateTime('2002/05/01'))), 1) 

        # One pending event
        self.Site.portal_workflow.doActionFor(self.Site.dinner, 'submit')
        self.assertEqual(len(self.Site.portal_catalog(review_state='pending')), 1)

        self.assertEqual(len(self.Site.portal_calendar.getEventsForThisDay(DateTime('2002/05/01'))), 1) 

        # Make calendar return pending events
        self.Site.portal_calendar.edit_configuration(show_types=('Event',), 
                                                     show_states=('pending', 'published'), 
                                                     use_session='')

        self.assertEqual(len(self.Site.portal_calendar.getEventsForThisDay(DateTime('2002/05/01'))), 2)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(CalendarTests),
        unittest.makeSuite(CalendarRequestTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
