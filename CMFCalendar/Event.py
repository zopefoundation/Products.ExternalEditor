##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
##############################################################################
import os, urllib
from DateTime import DateTime
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.WorkflowCore import WorkflowAction

# Import permission names
from Products.CMFCore import CMFCorePermissions
import EventPermissions

# Factory type information -- makes Events objects play nicely
# with the Types Tool (portal_types)
factory_type_information = (
    {'id': 'Event',
     'content_icon': 'event_icon.gif',
     'meta_type': 'CMF Event',
     'description': ('Events are objects for use in Calendar topical '
                     'queries on the catalog.'),
     'product': 'CMFCalendar',
     'factory': 'addEvent',
     'immediate_view': 'event_edit_form',
     'actions': ({'id': 'view',
                  'name': 'View',
                  'action': 'event_view',
                  'permissions': (CMFCorePermissions.View,)},
                 {'id': 'edit',
                  'name': 'Edit',
                  'action': 'event_edit_form',
                  'permissions': (EventPermissions.ChangeEvents,)},
                 ),                     # End Actions
     },
    )

def addEvent(self
             , id
             , title=''
             , description=''
             , effective_date = None 
             , expiration_date = None 
             , start_date = DateTime() 
             , end_date = DateTime()
             , location=''
             , contact_name=''
             , contact_email=''
             , contact_phone=''
             , event_url=''
             , REQUEST=None):
    """
    Create an empty event.
    """
    event = Event(id
                  , title
                  , description
                  , effective_date
                  , expiration_date
                  , start_date
                  , end_date
                  , location
                  , contact_name
                  , contact_email
                  , contact_phone
                  , event_url
                 )
    self._setObject(id, event)

def _dateStrings( when ):

    strings = {}

    if when is not None:
        strings[ 'year' ]   = str( when.year() )
        strings[ 'month' ]  = str( when.month() )
        strings[ 'day' ]    = str( when.day() )
    else:
        strings[ 'year' ]   = ''
        strings[ 'month' ]  = ''
        strings[ 'day' ]    = ''

    return strings

class Event(PortalContent, DefaultDublinCoreImpl):
    """
    Events are objects for the Calendar topical query.
    """
    meta_type='CMF Event'

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(CMFCorePermissions.View)
    
    def __init__(self
                 , id
                 , title=''
                 , description=''
                 , effective_date = None 
                 , expiration_date = None 
                 , start_date = DateTime()
                 , end_date = DateTime()
                 , location=''
                 , contact_name=''
                 , contact_email=''
                 , contact_phone=''
                 , event_url=''
                ):
        DefaultDublinCoreImpl.__init__(self)
        self.id=id
        self.setTitle(title)
        self.setDescription(description)
        self.effective_date = effective_date
        self.expiration_date = expiration_date
        self.setStartDate(start_date)
        self.setEndDate(end_date)
        self.location=location
        self.contact_name=contact_name
        self.contact_email=contact_email
        self.contact_phone=contact_phone
        self.event_url=event_url

    security.declarePrivate( '_datify' )
    def _datify( self, attrib ):
        if attrib == 'None':
            attrib = None
        elif not isinstance( attrib, DateTime ):
            if attrib is not None:
                attrib = DateTime( attrib )
        return attrib
    
    security.declarePublic('getEndStrings')
    def getEndStrings(self):
        """
        """
        return _dateStrings(self.end())

    security.declarePublic('getStartStrings')
    def getStartStrings(self):
        """
        """
        return _dateStrings(self.start())

    security.declareProtected(EventPermissions.ChangeEvents, 'edit')
    def edit(self
             , title=None
             , description=None
             , eventType=None
             , effectiveDay=None
             , effectiveMo=None
             , effectiveYear=None
             , expirationDay=None
             , expirationMo=None
             , expirationYear=None
             , start_time=None
             , startAMPM=None
             , stop_time=None
             , stopAMPM=None
             , location=None
             , contact_name=None
             , contact_email=None
             , contact_phone=None
             , event_url=None
            ):
        """\
        """
        if title is not None: 
            self.setTitle(title)
        if description is not None:
            self.setDescription(description)
        if eventType is not None:
            self.setSubject(eventType)
        efdate = '%s/%s/%s %s %s' % (effectiveDay
                                 , effectiveMo
                                 , effectiveYear
                                 , start_time
                                 , startAMPM
                                 )

        exdate = '%s/%s/%s %s %s' % (expirationDay
                                 , expirationMo
                                 , expirationYear
                                 , stop_time
                                 , stopAMPM
                                 )
 
        self.setStartDate(DateTime(efdate))
        self.setEndDate(DateTime(exdate))
        if location is not None:
            self.location = location
        if contact_name is not None:
            self.contact_name = contact_name
        if contact_email is not None:
            self.contact_email = contact_email
        if contact_phone is not None:
            self.contact_phone = contact_phone
        if event_url is not None:
            self.event_url = event_url
        self.reindexObject()
    edit = WorkflowAction(edit) 
    
    security.declarePublic('buildTimes')
    def buildTimes(self):
        result = []
        for hour in range (1, 13):
            for min in (00, 30):
                result.append('%02d:%02d' % (hour, min))
        return result
    
    security.declarePublic('buildDays')
    def buildDays(self):
        result = []
        for day in range (1, 32):
            result.append(str('%d' % (day)))
        return result

    security.declarePublic('buildMonths')
    def buildMonths(self):
        result = []
        for month in range (1, 13):
            result.append(str('%d' % (month)))
        return result
    
    security.declarePublic('buildYears')
    def buildYears(self):
        result = []
        start = (DateTime().year() - 2)
        end = (DateTime().year() + 5)
        for year in range (start, end):
            result.append(str(year))
        return result

    security.declareProtected(EventPermissions.ChangeEvents, 'setStartDate')
    def setStartDate(self, start):
        """
        Setting the event start date, when the event is scheduled to begin.
        """
        self.start_date = self._datify(start)
    
    security.declareProtected(EventPermissions.ChangeEvents, 'setEndDate')
    def setEndDate(self, end):
        """
        Setting the event end date, when the event ends.
        """
        self.end_date = self._datify(end)

    security.declarePublic('start')
    def start(self):
        """
            Return our start time as a string.
        """
        date = getattr( self, 'start_date', None )
        return date is None and self.created() or date

    security.declarePublic('end')
    def end(self):
        """
            Return our stop time as a string.
        """
        date = getattr( self, 'end_date', None )
        return date is None and self.start() or date    

    security.declarePublic('getStartTimeString')
    def getStartTimeString( self ):
        """
            Return our start time as a string.
        """
        return self.start().AMPMMinutes() 

    security.declarePublic('getStopTimeString')
    def getStopTimeString( self ):
        """
            Return our stop time as a string.
        """
        return self.end().AMPMMinutes() 

# Intialize the Event class, setting up security.
InitializeClass(Event)
