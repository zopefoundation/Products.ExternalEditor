import Zope
from unittest import TestCase, TestSuite, main, makeSuite
from Testing.makerequest import makerequest
from Products.CMFCalendar import CalendarTool
from DateTime import DateTime
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.User import UnrestrictedUser
from Products.ExternalMethod.ExternalMethod import manage_addExternalMethod

class TestCalendar(TestCase):

    def setUp(self):
        get_transaction().begin()
        
        self.app = makerequest(Zope.app())
        # Log in as a god :-)
        newSecurityManager(None, UnrestrictedUser('god',
                                                  'god',
                                                  [],
                                                  ''))
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

        session = app.unrestrictedTraverse('/session_data_manager').getSessionData
        app.REQUEST.set_lazy('SESSION', session)
        
        # bodge us a URL1
        
    def _testURL(self,url,params=None):
        Site = self.Site
        obj = Site.restrictedTraverse(url)
        if params is None:
            params=(obj, Site.REQUEST)
        apply(obj,params)
        
    def tearDown(self):
        get_transaction().abort()
        self.app._p_jar.close()
        
        
    def test_new(self):
        tool = CalendarTool.CalendarTool()
        self.assertEqual(tool.getId(),'portal_calendar')
    
    def test_types(self):
        self.assertEqual(self.Tool.getCalendarTypes(),['Event'])

        self.Tool.edit_configuration(show_types=['Event','Party'], use_session="True")
        self.assertEqual(self.Tool.getCalendarTypes(),['Event', 'Party'])
        
    def test_Days(self):
        assert self.Tool.getDays() == ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']

    def test_sessions(self):
        self.Tool.edit_configuration(show_types=['Event'], use_session="True")
        
        self._testURL('/CalendarTest/calendarBox', ())
        
        self.assertNotEqual(self.app.REQUEST.SESSION.get('calendar_year',None),None)

    def test_noSessions(self):
        self.Tool.edit_configuration(show_types=['Event'], use_session="")
        
        self._testURL('/CalendarTest/calendarBox', ())
        
        self.assertEqual(self.app.REQUEST.SESSION.get('calendar_year',None),None)

    def test_simpleCalendarRendering(self):
        data = [
                [
                 {'day': 0, 'event': 0, 'eventslist':[]},
                 {'day': 0, 'event': 0, 'eventslist':[]},
                 {'day': 1, 'event': 0, 'eventslist':[]},
                 {'day': 2, 'event': 0, 'eventslist':[]},
                 {'day': 3, 'event': 0, 'eventslist':[]},
                 {'day': 4, 'event': 0, 'eventslist':[]},
                 {'day': 5, 'event': 0, 'eventslist':[]}
                 ],
                [
                 {'day': 6, 'event': 0, 'eventslist':[]},
                 {'day': 7, 'event': 0, 'eventslist':[]},
                 {'day': 8, 'event': 0, 'eventslist':[]},
                 {'day': 9, 'event': 0, 'eventslist':[]},
                 {'day':10, 'event': 0, 'eventslist':[]},
                 {'day':11, 'event': 0, 'eventslist':[]},
                 {'day':12, 'event': 0, 'eventslist':[]}
                 ],
                [
                 {'day':13, 'event': 0, 'eventslist':[]},
                 {'day':14, 'event': 0, 'eventslist':[]},
                 {'day':15, 'event': 0, 'eventslist':[]},
                 {'day':16, 'event': 0, 'eventslist':[]},
                 {'day':17, 'event': 0, 'eventslist':[]},
                 {'day':18, 'event': 0, 'eventslist':[]},
                 {'day':19, 'event': 0, 'eventslist':[]}
                 ],
                [
                 {'day':20, 'event': 0, 'eventslist':[]},
                 {'day':21, 'event': 0, 'eventslist':[]},
                 {'day':22, 'event': 0, 'eventslist':[]},
                 {'day':23, 'event': 0, 'eventslist':[]},
                 {'day':24, 'event': 0, 'eventslist':[]},
                 {'day':25, 'event': 0, 'eventslist':[]},
                 {'day':26, 'event': 0, 'eventslist':[]}
                 ],
                [
                 {'day':27, 'event': 0, 'eventslist':[]},
                 {'day':28, 'event': 0, 'eventslist':[]},
                 {'day':29, 'event': 0, 'eventslist':[]},
                 {'day':30, 'event': 0, 'eventslist':[]},
                 {'day':31, 'event': 0, 'eventslist':[]},
                 {'day': 0, 'event': 0, 'eventslist':[]},
                 {'day': 0, 'event': 0, 'eventslist':[]}
                 ]                
                ]
        assert self.Tool.getEventsForCalendar(month='1', year='2002') == data, self.Tool.getEventsForCalendar(month='1', year='2002')
        
    def test_singleEventCalendarRendering(self):
        
        self.Site.Members.folder_factories.invokeFactory(type_name="Event",id='Event1')
        event = self.app.restrictedTraverse('/CalendarTest/Members/Event1')
        event.edit( title='title'
                    , description='description'
                    , eventType=( 'eventType', )
                    , effectiveDay=1
                    , effectiveMo=1
                    , effectiveYear=2002
                    , expirationDay=1
                    , expirationMo=1
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
                 {'day': 1, 'event': 1, 'eventslist':[{'title': 'title', 'end': '23:59:00', 'start': '00:00:00'}]},
                 {'day': 2, 'event': 0, 'eventslist':[]},
                 {'day': 3, 'event': 0, 'eventslist':[]},
                 {'day': 4, 'event': 0, 'eventslist':[]},
                 {'day': 5, 'event': 0, 'eventslist':[]}
                 ],
                [
                 {'day': 6, 'event': 0, 'eventslist':[]},
                 {'day': 7, 'event': 0, 'eventslist':[]},
                 {'day': 8, 'event': 0, 'eventslist':[]},
                 {'day': 9, 'event': 0, 'eventslist':[]},
                 {'day':10, 'event': 0, 'eventslist':[]},
                 {'day':11, 'event': 0, 'eventslist':[]},
                 {'day':12, 'event': 0, 'eventslist':[]}
                 ],
                [
                 {'day':13, 'event': 0, 'eventslist':[]},
                 {'day':14, 'event': 0, 'eventslist':[]},
                 {'day':15, 'event': 0, 'eventslist':[]},
                 {'day':16, 'event': 0, 'eventslist':[]},
                 {'day':17, 'event': 0, 'eventslist':[]},
                 {'day':18, 'event': 0, 'eventslist':[]},
                 {'day':19, 'event': 0, 'eventslist':[]}
                 ],
                [
                 {'day':20, 'event': 0, 'eventslist':[]},
                 {'day':21, 'event': 0, 'eventslist':[]},
                 {'day':22, 'event': 0, 'eventslist':[]},
                 {'day':23, 'event': 0, 'eventslist':[]},
                 {'day':24, 'event': 0, 'eventslist':[]},
                 {'day':25, 'event': 0, 'eventslist':[]},
                 {'day':26, 'event': 0, 'eventslist':[]}
                 ],
                [
                 {'day':27, 'event': 0, 'eventslist':[]},
                 {'day':28, 'event': 0, 'eventslist':[]},
                 {'day':29, 'event': 0, 'eventslist':[]},
                 {'day':30, 'event': 0, 'eventslist':[]},
                 {'day':31, 'event': 0, 'eventslist':[]},
                 {'day': 0, 'event': 0, 'eventslist':[]},
                 {'day': 0, 'event': 0, 'eventslist':[]}
                 ]                
                ]
        assert self.Tool.getEventsForCalendar(month='1', year='2002') == data, self.Tool.getEventsForCalendar(month='1', year='2002')

    def test_spanningEventCalendarRendering(self):
        
        self.Site.Members.folder_factories.invokeFactory(type_name="Event",id='Event1')
        event = self.app.restrictedTraverse('/CalendarTest/Members/Event1')
        event.edit( title='title'
                    , description='description'
                    , eventType=( 'eventType', )
                    , effectiveDay=1
                    , effectiveMo=1
                    , effectiveYear=2002
                    , expirationDay=31
                    , expirationMo=1
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
                 {'day': 1, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': '00:00:00'}]},
                 {'day': 2, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day': 3, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day': 4, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day': 5, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]}
                 ],
                [
                 {'day': 6, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day': 7, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day': 8, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day': 9, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':10, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':11, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':12, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]}
                 ],
                [
                 {'day':13, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':14, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':15, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':16, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':17, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':18, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':19, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]}
                 ],
                [
                 {'day':20, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':21, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':22, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':23, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':24, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':25, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':26, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]}
                 ],
                [
                 {'day':27, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':28, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':29, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':30, 'event': 1, 'eventslist':[{'title': 'title', 'end': None, 'start': None}]},
                 {'day':31, 'event': 1, 'eventslist':[{'title': 'title', 'end': '23:59:00', 'start': None}]},
                 {'day': 0, 'event': 0, 'eventslist':[]},
                 {'day': 0, 'event': 0, 'eventslist':[]}
                 ]                
                ]
        assert self.Tool.getEventsForCalendar(month='1', year='2002') == data, self.Tool.getEventsForCalendar(month='1', year='2002')

    def test_getPreviousMonth(self):
        assert self.Tool.getPreviousMonth(2,2002) == DateTime('1/1/2002')
        assert self.Tool.getPreviousMonth(1,2002) == DateTime('12/1/2001')
       
    def test_getNextMonth(self):
        assert self.Tool.getNextMonth(12,2001) == DateTime('1/1/2002')
        assert self.Tool.getNextMonth(1,2002) == DateTime('2/1/2002')

    def test_getBeginAndEndTimes(self):
        assert self.Tool.getBeginAndEndTimes(1,12,2001) == (DateTime('12/1/2001 12:00:00AM'),DateTime('12/1/2001 11:59:59PM'))

    def test_singleDayRendering(self):
        
        self.Site.Members.folder_factories.invokeFactory(type_name="Event",id='Event1')
        event = self.app.restrictedTraverse('/CalendarTest/Members/Event1')
        event.edit( title='title'
                    , description='description'
                    , eventType=( 'eventType', )
                    , effectiveDay=1
                    , effectiveMo=1
                    , effectiveYear=2002
                    , expirationDay=31
                    , expirationMo=1
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
        
        assert len(self.Site.portal_calendar.getEventsForThisDay(thisDay=DateTime('1/1/2002'))) == 1

        self.Site.Members.folder_factories.invokeFactory(type_name="Event",id='Event2')
        event = self.app.restrictedTraverse('/CalendarTest/Members/Event2')
        event.edit( title='title'
                    , description='description'
                    , eventType=( 'eventType', )
                    , effectiveDay=1
                    , effectiveMo=1
                    , effectiveYear=2002
                    , expirationDay=1
                    , expirationMo=1
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

        assert len(self.Site.portal_calendar.getEventsForThisDay(thisDay=DateTime('1/1/2002'))) == 2
        
        self.Site.Members.folder_factories.invokeFactory(type_name="Event",id='Event3')
        event = self.app.restrictedTraverse('/CalendarTest/Members/Event3')
        event.edit( title='title'
                    , description='description'
                    , eventType=( 'eventType', )
                    , effectiveDay=12
                    , effectiveMo=12
                    , effectiveYear=2001
                    , expirationDay=1
                    , expirationMo=1
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

        assert len(self.Site.portal_calendar.getEventsForThisDay(thisDay=DateTime('1/1/2002'))) == 3

        self.Site.Members.folder_factories.invokeFactory(type_name="Event",id='Event4')
        event = self.app.restrictedTraverse('/CalendarTest/Members/Event4')
        event.edit( title='title'
                    , description='description'
                    , eventType=( 'eventType', )
                    , effectiveDay=12
                    , effectiveMo=12
                    , effectiveYear=2001
                    , expirationDay=31
                    , expirationMo=1
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

        assert len(self.Site.portal_calendar.getEventsForThisDay(thisDay=DateTime('1/1/2002'))) == 4

        self.Site.Members.folder_factories.invokeFactory(type_name="Event",id='Event5')
        event = self.app.restrictedTraverse('/CalendarTest/Members/Event5')
        event.edit( title='title'
                    , description='description'
                    , eventType=( 'eventType', )
                    , effectiveDay=31
                    , effectiveMo=1
                    , effectiveYear=2002
                    , expirationDay=31
                    , expirationMo=1
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

        assert len(self.Site.portal_calendar.getEventsForThisDay(thisDay=DateTime('1/1/2002'))) == 4

def test_suite():
    return TestSuite((
        makeSuite( TestCalendar ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
