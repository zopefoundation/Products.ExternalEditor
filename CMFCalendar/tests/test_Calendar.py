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
import Zope
Zope.startup()

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.User import UnrestrictedUser
from DateTime import DateTime
from Products.ExternalMethod.ExternalMethod import manage_addExternalMethod
from Testing.makerequest import makerequest

from Products.CMFCalendar import CalendarTool


class TestCalendar(unittest.TestCase):

    def setUp(self):
        get_transaction().begin()

        self.app = makerequest(Zope.app())
        # Log in as a god :-)
        newSecurityManager( None, UnrestrictedUser('god', 'god', ['Manager'], '') )
        app = self.app

        app.REQUEST.set('URL1','http://foo/sorcerertest/test')

        try: app._delObject('CalendarTest')
        except AttributeError: pass
        app.manage_addProduct['CMFDefault'].manage_addCMFSite('CalendarTest')

        self.Site = app.CalendarTest

        manage_addExternalMethod(app.CalendarTest,
                                 id='install_events',
                                 title="Install Events",
                                 module="CMFCalendar.Install",
                                 function="install")

        ExMethod = app.restrictedTraverse('/CalendarTest/install_events')
        ExMethod()

        self.Tool = app.restrictedTraverse('/CalendarTest/portal_calendar')

        # sessioning bodge until we find out how to do this properly

        self.have_session = hasattr( app, 'session_data_manager' )
        if self.have_session:
            app.REQUEST.set_lazy( 'SESSION'
                                , app.session_data_manager.getSessionData )

        # bodge us a URL1

    def _testURL(self,url,params=None):
        Site = self.Site
        obj = Site.restrictedTraverse(url)
        if params is None:
            params=(obj, Site.REQUEST)
        obj(*params)

    def tearDown(self):
        noSecurityManager()
        get_transaction().abort()
        self.app._p_jar.close()

    def test_new(self):
        tool = CalendarTool.CalendarTool()
        self.assertEqual(tool.getId(),'portal_calendar')

    def test_types(self):
        self.assertEqual(self.Tool.getCalendarTypes(), ('Event',))

        self.Tool.edit_configuration(show_types=['Event','Party']
                                    , show_states=[] 
                                    , use_session="")
        self.assertEqual(self.Tool.getCalendarTypes(), ('Event', 'Party'))

    def test_states(self):
        self.assertEqual(self.Tool.getCalendarStates(), ('published',))

        self.Tool.edit_configuration(show_types=[]
                                    , show_states=['pending', 'published'] 
                                    , use_session="")
        self.assertEqual(self.Tool.getCalendarStates(), ('pending', 'published'))

    def test_Days(self):
        import locale
        old_locale = locale.getlocale(locale.LC_ALL)[0]
        locale.setlocale(locale.LC_ALL, 'C')
        try:
            self.assertEqual(self.Tool.getDays(), ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'])
        finally:
            locale.setlocale(locale.LC_ALL, old_locale)

    def XXX_test_sessions(self):

        if not self.have_session:
            return

        self.Tool.edit_configuration(show_types=['Event'], use_session="True")

        self._testURL('/CalendarTest/calendarBox', ())

        self.failUnless(self.app.REQUEST.SESSION.get('calendar_year',None))

    def XXX_test_noSessions(self):
        self.Tool.edit_configuration(show_types=['Event'], use_session="")

        self._testURL('/CalendarTest/calendarBox', ())

        if self.have_session:
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

        self.Site.Members.folder_factories.invokeFactory(type_name="Event",id='Event1')
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

        self.Site.Members.folder_factories.invokeFactory(type_name="Event",id='Event1')
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
        assert self.Tool.getPreviousMonth(2,2002) == DateTime('2002/1/1')
        assert self.Tool.getPreviousMonth(1,2002) == DateTime('2001/12/1')

    def test_getNextMonth(self):
        assert self.Tool.getNextMonth(12,2001) == DateTime('2002/1/1')
        assert self.Tool.getNextMonth(1,2002) == DateTime('2002/2/1')

    def test_getBeginAndEndTimes(self):
        self.assertEqual( self.Tool.getBeginAndEndTimes(1,12,2001),
                          ( DateTime('2001/12/1 12:00:00AM'),
                            DateTime('2001/12/1 11:59:59PM') ) )

    def test_singleDayRendering(self):

        self.Site.Members.folder_factories.invokeFactory(type_name="Event",id='Event1')
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

        assert len(self.Site.portal_calendar.getEventsForThisDay(thisDay=DateTime('2002/5/1'))) == 1

        self.Site.Members.folder_factories.invokeFactory(type_name="Event",id='Event2')
        event = self.app.restrictedTraverse('/CalendarTest/Members/Event2')
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

        assert len(self.Site.portal_calendar.getEventsForThisDay(thisDay=DateTime('2002/5/1'))) == 2

        self.Site.Members.folder_factories.invokeFactory(type_name="Event",id='Event3')
        event = self.app.restrictedTraverse('/CalendarTest/Members/Event3')
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
        self.Site.portal_workflow.doActionFor(
                                              event,
                                              'publish',
                                              comment='testing')

        assert len(self.Site.portal_calendar.getEventsForThisDay(thisDay=DateTime('2002/5/1'))) == 3

        self.Site.Members.folder_factories.invokeFactory(type_name="Event",id='Event4')
        event = self.app.restrictedTraverse('/CalendarTest/Members/Event4')
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
        self.Site.portal_workflow.doActionFor(
                                              event,
                                              'publish',
                                              comment='testing')

        assert len(self.Site.portal_calendar.getEventsForThisDay(thisDay=DateTime('2002/5/1'))) == 4

        self.Site.Members.folder_factories.invokeFactory(type_name="Event",id='Event5')
        event = self.app.restrictedTraverse('/CalendarTest/Members/Event5')
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
        self.Site.portal_workflow.doActionFor(
                                              event,
                                              'publish',
                                              comment='testing')

        assert len(self.Site.portal_calendar.getEventsForThisDay(thisDay=DateTime('2002/5/1'))) == 4
        assert len(self.Site.portal_calendar.getEventsForThisDay(thisDay=DateTime('2002/5/31'))) == 3

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
        unittest.makeSuite( TestCalendar ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
