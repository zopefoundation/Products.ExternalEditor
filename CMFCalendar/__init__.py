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
from Products.CMFDefault import Portal
import Event
import Products.CMFCore

from Products.CMFCore import utils, CMFCorePermissions
from Products.CMFCore.DirectoryView import registerDirectory
import EventPermissions
import CalendarTool

import sys
this_module = sys.modules[ __name__ ]

contentConstructors = (Event.addEvent,)
contentClasses = (Event.Event,)

tools = ( CalendarTool.CalendarTool, )

z_bases = utils.initializeBasesPhase1( contentClasses, this_module )

# This is used by a script (external method) that can be run
# to set up Events in an existing CMF Site instance.
event_globals=globals()

# Make the skins available as DirectoryViews
registerDirectory('skins', globals())
registerDirectory('skins/calendar', globals())

def initialize( context ):
    utils.ToolInit('CMFCalendar Tool', tools=tools,
                   product_name='CMFCalendar', icon='tool.gif',
                   ).initialize( context )
    
    utils.initializeBasesPhase2( z_bases, context )
    context.registerHelpTitle('CMF Calendar Help')
    context.registerHelp(directory='help')
    utils.ContentInit( 'CMF Event'
                     , content_types = contentClasses
                     , permission = CMFCorePermissions.AddPortalContent 
                     , extra_constructors = contentConstructors
                     , fti = Event.factory_type_information
                     ).initialize( context ) 
