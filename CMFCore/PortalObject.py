##############################################################################
#
# Copyright (c) 2001-2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
""" PortalObject: The portal root object class

$Id$
"""

from Globals import InitializeClass

from PortalFolder import PortalFolder
from Skinnable import SkinnableObjectManager
from CMFCorePermissions import AddPortalMember
from CMFCorePermissions import SetOwnPassword
from CMFCorePermissions import SetOwnProperties
from CMFCorePermissions import MailForgottenPassword
from CMFCorePermissions import RequestReview
from CMFCorePermissions import ReviewPortalContent
from CMFCorePermissions import AccessFuturePortalContent

PORTAL_SKINS_TOOL_ID = 'portal_skins'


class PortalObjectBase(PortalFolder, SkinnableObjectManager):

    meta_type = 'Portal Site'
    _isPortalRoot = 1

    # Ensure certain attributes come from the correct base class.
    __getattr__ = SkinnableObjectManager.__getattr__
    __of__ = SkinnableObjectManager.__of__
    _checkId = SkinnableObjectManager._checkId

    # Ensure all necessary permissions exist.
    __ac_permissions__ = (
        (AddPortalMember, ()),
        (SetOwnPassword, ()),
        (SetOwnProperties, ()),
        (MailForgottenPassword, ()),
        (RequestReview, ()),
        (ReviewPortalContent, ()),
        (AccessFuturePortalContent, ()),
        )

    def getSkinsFolderName(self):
        return PORTAL_SKINS_TOOL_ID

InitializeClass(PortalObjectBase)
