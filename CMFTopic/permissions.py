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
""" Permissions used throughout CMFTopic.

$Id$
"""
from AccessControl import ModuleSecurityInfo

security = ModuleSecurityInfo('Products.CMFTopic.permissions')

from Products.CMFCore.permissions import setDefaultRoles

security.declarePublic('AddTopics')
AddTopics = 'Add portal topics'
setDefaultRoles(AddTopics, ('Manager',))

security.declarePublic('ChangeTopics')
ChangeTopics = 'Change portal topics'
setDefaultRoles(ChangeTopics, ('Manager', 'Owner',))

security.declarePublic('AccessContentsInformation')
from Products.CMFCore.permissions import AccessContentsInformation

security.declarePublic('ListFolderContents')
from Products.CMFCore.permissions import ListFolderContents

security.declarePublic('View')
from Products.CMFCore.permissions import View
