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
"""TopicPermissions: Permissions used throughout CMFTopic.

$Id$
"""
__version__='$Revision$'[11:-2]

from Products.CMFCore.CMFCorePermissions import setDefaultRoles

# Gathering Topic Related Permissions into one place
AddTopics = 'Add portal topics'
ChangeTopics = 'Change portal topics'

# Set up default roles for permissions
setDefaultRoles(AddTopics, ('Manager',))
setDefaultRoles(ChangeTopics, ('Manager', 'Owner',))

