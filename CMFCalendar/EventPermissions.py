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
"""EventPermissions: Permissions used in the CMF Events class
$Id$
"""
__version__='$Revision$'[11:-2]

from Products.CMFCore.CMFCorePermissions import setDefaultRoles

# Gathering Event Related Permissions into one place
AddEvents = 'Add portal events'
ChangeEvents = 'Change portal events'

# Set up default roles for permissions
setDefaultRoles(AddEvents, ('Manager', 'Owner', 'Member'))
setDefaultRoles(ChangeEvents, ('Manager', 'Owner',))
