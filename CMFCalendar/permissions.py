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
""" CMFCalendar product permissions

$Id$
"""
from AccessControl import ModuleSecurityInfo

from Products.CMFCore.permissions import setDefaultRoles

security = ModuleSecurityInfo('Products.CMFCalendar.permissions')

security.declarePublic('AddEvents')
AddEvents = 'Add portal events'
setDefaultRoles(AddEvents, ('Manager', 'Owner', 'Member'))

security.declarePublic('ChangeEvents')
ChangeEvents = 'Change portal events'
setDefaultRoles(ChangeEvents, ('Manager', 'Owner',))

security.declarePublic('AddPortalContent')
from Products.CMFCore.permissions import AddPortalContent

security.declarePublic('ManagePortal')
from Products.CMFCore.permissions import ManagePortal

security.declarePublic('View')
from Products.CMFCore.permissions import View

security.declarePublic('ModifyPortalContent')
from Products.CMFCore.permissions import ModifyPortalContent
