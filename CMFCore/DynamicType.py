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
""" DynamicType: Mixin for dynamic properties.

$Id$
"""

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from utils import getToolByName
from urllib import quote

from interfaces.Dynamic import DynamicType as IDynamicType


class DynamicType:
    """
    Mixin for portal content that allows the object to take on
    a dynamic type property.
    """

    __implements__ = IDynamicType

    portal_type = None

    security = ClassSecurityInfo()

    def _setPortalTypeName(self, pt):
        '''
        Called by portal_types during construction, records an
        ID that will be used later to locate the correct
        ContentTypeInformation.
        '''
        self.portal_type = pt

    security.declarePublic('getPortalTypeName')
    def getPortalTypeName(self):
        """
        Returns the portal type name that can be passed to portal_types.
        If the object is uninitialized, returns None.
        """
        pt = self.portal_type
        if callable( pt ):
            pt = pt()
        return pt

    _getPortalTypeName = getPortalTypeName

    security.declarePublic('getTypeInfo')
    def getTypeInfo(self):
        '''
        Returns an object that supports the ContentTypeInformation interface.
        '''
        tool = getToolByName(self, 'portal_types', None)
        if tool is None:
            return None
        return tool.getTypeInfo(self)  # Can return None.

    # Support for dynamic icons

    security.declarePublic('getIcon')
    def getIcon(self, relative_to_portal=0):
        """
        Using this method allows the content class
        creator to grab icons on the fly instead of using a fixed
        attribute on the class.
        """
        ti = self.getTypeInfo()
        if ti is not None:
            icon = quote(ti.getIcon())
            if icon:
                if relative_to_portal:
                    return icon
                else:
                    # Relative to REQUEST['BASEPATH1']
                    portal_url = getToolByName( self, 'portal_url' )
                    res = portal_url(relative=1) + '/' + icon
                    while res[:1] == '/':
                        res = res[1:]
                    return res
        return 'misc_/OFSP/dtmldoc.gif'

    security.declarePublic('icon')
    icon = getIcon  # For the ZMI

InitializeClass(DynamicType)
