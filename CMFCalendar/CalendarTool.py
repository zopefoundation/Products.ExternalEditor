########################################################################
#
# Calendar Tool by Andy Dawkins (New Information Paradigms Ltd)
#
# Converted to a CMF Tool by Alan Runyan
#
# Additional Modification for the CMFCalendar by Andy Dawkins 29/04/2002
#
########################################################################


import calendar
calendar.setfirstweekday(6) #start day  Mon(0)-Sun(6)
from DateTime import DateTime

from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import _checkPermission, _getAuthenticatedUser, limitGrantedRoles
from Products.CMFCore.utils import getToolByName, _dtmldir
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

class CalendarTool (UniqueObject, SimpleItem):
    """ a calendar tool for encapsualting how calendars work and are displayed """
    id = 'portal_calendar'
    meta_type= 'CMF Calendar Tool'
    security = ClassSecurityInfo()
    plone_tool = 1

    manage_options = ( ({ 'label' : 'Overview', 'action' : 'manage_overview' }
                     ,  { 'label' : 'Configure', 'action' : 'manage_configure' }
                     ,
                     ) + SimpleItem.manage_options
                     )

    #
    #   ZMI methods
    #
    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'manage_overview' )    
    manage_overview = PageTemplateFile('www/explainCalendarTool', globals(),
                                   __name__='manage_overview')

    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'manage_configure' )    
    manage_configure = PageTemplateFile('www/configureCalendarTool', globals(),
                                   __name__='manage_configure')
    
    def __init__(self):
        self.calendar_types = ['Event']
        self.use_session = "True"

    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'edit_configuration' )
    def edit_configuration(self, show_types, use_session):
        """ Change the configuration of the calendar tool """
        self.calendar_types = show_types
        self.use_session = use_session
        if hasattr(self.REQUEST, 'RESPONSE'):
            self.REQUEST.RESPONSE.redirect('manage_configure')
        
    security.declarePublic('getCalendarTypes')
    def getCalendarTypes(self):
        """ Returns a list of type that will show in the calendar """
        return self.calendar_types

    security.declarePublic('getUseSession')
    def getUseSession(self):
        """ Returns the Use_Session option """
        return self.use_session

    security.declarePublic('getDays')
    def getDays(self):
        """ Returns a list of days with the correct start day first """        
        import string
        return string.split(calendar.weekheader(2),' ')
        
    security.declarePublic('getWeeksList')
    def getWeeksList(self, month='1', year='2002'):
        """Creates a series of weeks, each of which contains an integer day number.
           A day number of 0 means that day is in the previous or next month.
        """
        # daysByWeek is a list of days inside a list of weeks, like so:
        # [[0, 1, 2, 3, 4, 5, 6],
        #  [7, 8, 9, 10, 11, 12, 13],
        #  [14, 15, 16, 17, 18, 19, 20],
        #  [21, 22, 23, 24, 25, 26, 27],
        #  [28, 29, 30, 31, 0, 0, 0]]
        daysByWeek=calendar.monthcalendar(year, month)
    
        return daysByWeek

    security.declarePublic('getEventsForCalendar')
    def getEventsForCalendar(self, month='1', year='2002'):
        """ recreates a sequence of weeks, by days each day is a mapping.
            {'day': #, 'url': None}
        """
        year=int(year)
        month=int(month)
        # daysByWeek is a list of days inside a list of weeks, like so:
        # [[0, 1, 2, 3, 4, 5, 6],
        #  [7, 8, 9, 10, 11, 12, 13],
        #  [14, 15, 16, 17, 18, 19, 20],
        #  [21, 22, 23, 24, 25, 26, 27],
        #  [28, 29, 30, 31, 0, 0, 0]]
        daysByWeek=calendar.monthcalendar(year, month)
        weeks=[]
        
        events=self.catalog_getevents(year, month)
    
        for week in daysByWeek:
            days=[]
            for day in week:
                if events.has_key(day):
                    days.append(events[day])
                else:
                    days.append({'day': day, 'event': 0, 'eventslist':[]})
                
            weeks.append(days)
            
        return weeks
    
    security.declarePublic('catalog_getevents')
    def catalog_getevents(self, year, month):
        """ given a year and month return a list of days that have events """
        first_date=DateTime(str(month)+'/1/'+str(year))
        last_day=calendar.monthrange(year, month)[1]
        last_date=DateTime(str(month)+'/'+str(last_day)+'/'+str(year))
    
        query=self.portal_catalog(Type=self.calendar_types,
                                  review_state='published',	                          
                                  start=(first_date, last_date),
                                  start_usage='range:min:max',
                                  sort_on='start')
        # I don't like doing two searches
        # What i want to do is
        # start date => 1/1/2002 and start date <= 31/1/2002
        # or
        # end date => 1/1/2002 and end date <= 31/1/2002
        # but I don't know how to do that in one search query :(  - AD

        # if you look at calendar_slot you can see how to do this in 1 query - runyaga
        query+=self.portal_catalog(Type=self.calendar_types,
                                   review_state='published',
                                   end=(first_date, last_date),
                                   end_usage='range:min:max',
                                   sort_on='end')
        
        # compile a list of the days that have events
        eventDays={}
        for daynumber in range(1, 32): # 1 to 31
            eventDays[daynumber] = {'eventslist':[], 'event':0, 'day':daynumber}
        includedevents = []
        for result in query:
            if result.getRID() in includedevents:
                break
            else:
                includedevents.append(result.getRID())
            event={}
            # we need to deal with events that end next month
            if  result.end.month() != month:  # doesn't work for events that last ~12 months - fix it if it's a problem, otherwise ignore
                eventEndDay = last_day
                event['end'] = None
            else:
                eventEndDay = result.end.day()
                event['end'] = result.end.Time()
            # and events that started last month
            if result.start.month() != month:  # same as above re: 12 month thing
                eventStartDay = 1
                event['start'] = None
            else:
                eventStartDay = result.start.day()
                event['start'] = result.start.Time()
            event['title'] = result.Title or result.id
            if eventStartDay != eventEndDay:
                allEventDays = range(eventStartDay, eventEndDay+1)
                eventDays[eventStartDay]['eventslist'].append({'end':None, 'start':result.start.Time(), 'title':result.Title})
                eventDays[eventStartDay]['event'] = 1
                for eventday in allEventDays[1:-1]:
                    eventDays[eventday]['eventslist'].append({'end':None, 'start':None, 'title':result.Title})
                    eventDays[eventday]['event'] = 1
                eventDays[eventEndDay]['eventslist'].append({'end':result.end.Time(), 'start':None, 'title':result.Title})
                eventDays[eventEndDay]['event'] = 1
            else:
                eventDays[eventStartDay]['eventslist'].append(event)
                eventDays[eventStartDay]['event'] = 1
            # This list is not uniqued and isn't sorted
            # uniquing and sorting only wastes time
            # and in this example we don't need to because
            # later we are going to do an 'if 2 in eventDays'
            # so the order is not important.
            # example:  [23, 28, 29, 30, 31, 23]
        return eventDays

    security.declarePublic('getEventsForThisDay')
    def getEventsForThisDay(self, thisDay):
        """ given an exact day return ALL events that:
            A) Start on this day  OR
            B) End on this day  OR
            C) Start before this day  AND  end after this day"""
        
        catalog = self.portal_catalog
        
        first_date, last_date = self.getBeginAndEndTimes(thisDay.day(), thisDay.month(), thisDay.year())
        #first_date=DateTime(thisDay.Date()+" 00:00:00")
        #last_date=DateTime(thisDay.Date()+" 23:59:59")

        # Get all events that Start on this day
        query=self.portal_catalog(Type=self.calendar_types,
                                  review_state='published',	                          
                                  start=(first_date,last_date),
                                  start_usage='range:min:max')
        
        # Get all events that End on this day
        query+=self.portal_catalog(Type=self.calendar_types,
                                  review_state='published',	                          
                                  end=(first_date,last_date),
                                  end_usage='range:min:max')

        # Get all events that Start before this day AND End after this day
        query+=self.portal_catalog(Type=self.calendar_types,
                                  review_state='published',
                                  start=first_date,
                                  start_usage='range:max',
                                  end=last_date,
                                  end_usage='range:min')

        # Unique the results
        results = []
        rids = []
        for item in query:
            rid = item.getRID()
            if not rid in rids:
                results.append(item)
                rids.append(rid)
                
        def sort_function(x,y):
            z = cmp(x.start,y.start)
            if not z: 
                return cmp(x.end,y.end)
            return z
        
        # Sort by start date
        results.sort(sort_function)
                
        return results
                
        
    security.declarePublic('getPreviousMonth')
    def getPreviousMonth(self, month, year):
        # given any particular year and month, this method will return a datetime object
        # for one month prior
        
        try: month=int(month)
        except: raise "Calendar Type Error", month
        try: year=int(year)
        except: raise "Calendar Type Error", year
        
        if month==0 or month==1:
            month, year = 12, year - 1
        else:
            month-=1
        
        return DateTime(str(month) + '/1/' + str(year))    
    
    security.declarePublic('getNextMonth')
    def getNextMonth(self, month, year):
        # given any particular year and month, this method will return a datetime object
        # for one month after
    
        try: month=int(month)
        except: raise "Calendar Type Error", month
        try: year=int(year)
        except: raise "Calendar Type Error", year
        
        if month==12:
            month, year = 1, year + 1
        else:
            month+=1
        
        return DateTime(str(month) + '/1/' + str(year))

    security.declarePublic('getBeginAndEndTimes')
    def getBeginAndEndTimes(self, day, month, year):
        # Given any day, month and year this method returns 2 DateTime objects
        # That represent the exact start and the exact end of that particular day.
        
        day=str(day)
        month=str(month)
        year=str(year)
        
        begin=DateTime(month+'/'+day+'/'+year+' 12:00:00AM')
        end=DateTime(month+'/'+day+'/'+year+' 11:59:59PM')
        
        return (begin, end)    
        
    
InitializeClass(CalendarTool)
