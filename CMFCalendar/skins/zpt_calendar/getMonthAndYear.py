
# Get the year and month that the calendar should display.

import DateTime

current = DateTime.DateTime()

year = None
month = None
use_session = container.portal_calendar.getUseSession()

# First priority goes to the data in the request
year  = context.REQUEST.get('year',  None)
month = context.REQUEST.get('month', None)
session = None

# Next get the data from the SESSION
if use_session == "True":
    session = context.REQUEST.get('SESSION', None)
    if session:
        if not year:   year  = session.get('calendar_year',  None)
        if not month:  month = session.get('calendar_month', None)
  
# Last resort to Today
if not year:   year  = current.year()
if not month:  month = current.month()

# Then store the results in the session for next time
if session:
  session.set('calendar_year',  year)
  session.set('calendar_month', month)
  
# Finally return the results
return (year, month)
