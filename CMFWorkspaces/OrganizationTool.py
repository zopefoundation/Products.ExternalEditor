##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Organization Tool

  Responsible for specifying places for new objects.

  - specifies types that can be added placelessly

  - specifies the skin name of the form for adding each type

  - specifies the default location where instances of those types
    get added

$Id$
"""

import os

from Acquisition import aq_inner, aq_parent
from Globals import InitializeClass, DTMLFile
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.CMFCorePermissions import ManagePortal

_wwwdir = os.path.join(os.path.dirname(__file__), 'www') 


class OrganizationTool(UniqueObject, SimpleItem):
    id = 'portal_organization'
    meta_type = 'Portal Organization Tool'

    security = ClassSecurityInfo()

    manage_options = ( { 'label': 'Overview', 'action': 'manage_overview' }
                     , { 'label': 'Placement', 'action': 'manage_placement' },
                     ) + SimpleItem.manage_options

    _types = {}  # type name -> (location, skin name)

    #
    #   ZMI methods
    #
    security.declareProtected(ManagePortal, 'manage_overview' )
    manage_overview = DTMLFile('explainOrganizationTool', _wwwdir)

    security.declareProtected(ManagePortal, 'manage_placement' )
    manage_placement = PageTemplateFile('placement', _wwwdir)

    #
    #   'OrganizationTool' interface methods
    #

    security.declarePublic('listAddableTypes')
    def listAddableTypes(self):
        """Returns a list of types."""
        return self._types.keys()


    security.declarePublic('getAddFormURL')
    def getAddFormURL(self, type_name):
        """Returns the URL to visit to add an object of the given type.
        """
        base = aq_parent(aq_inner(self)).absolute_url()
        location, skin_name = self._types[str(type_name)]
        if not location.startswith('/'):
            location = '/' + location
        if not location.endswith('/'):
            location = location + '/'
        return base + location + skin_name


    security.declareProtected(ManagePortal, 'getLocationInfo')
    def getLocationInfo(self):
        """Returns the list of types, locations, and skin names.
        """
        base = aq_parent(aq_inner(self)).absolute_url()
        res = []
        items = self._types.items()
        items.sort()
        for key, (location, skin_name) in items:
            res.append({'type': key,
                        'location': location,
                        'skin_name': skin_name,})
        return res


    security.declareProtected(ManagePortal, 'setLocationInfo')
    def setLocationInfo(self, info, RESPONSE=None):
        """Sets the list of types, locations, and skin names.
        """
        types = {}
        for r in info:
            t = str(r.type)
            if t:
                types[t] = (str(r.location), str(r.skin_name))
        self._types = types
        if RESPONSE is not None:
            RESPONSE.redirect(self.absolute_url() + '/manage_placement?' +
                              'manage_tabs_message=Saved+changes.')


InitializeClass(OrganizationTool)

