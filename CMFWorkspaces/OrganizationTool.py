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
from urllib import quote

from Acquisition import aq_inner
from Acquisition import aq_parent
from Globals import InitializeClass
from Globals import DTMLFile
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.utils import UniqueObject, getToolByName

from permissions import ManagePortal

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
        res = self._types.keys()
        res.sort()
        return res


    security.declarePublic('getAddFormURL')
    def getAddFormURL(self, type_name, workspace=None):
        """Returns the URL to visit to add an object of the given type.
        """
        location, skin_name = self._types[str(type_name)]
        if not location.startswith('/'):
            location = '/' + location
        base = aq_parent(aq_inner(self)).absolute_url()
        base_url = base + location
        if not base_url.endswith('/'):
            base_url = base_url + '/'
        ws = ''
        if workspace is not None:
            ws = '&workspace=%s' % quote(
                '/'.join(workspace.getPhysicalPath()))
        return '%s%s?type=%s%s' % (base_url, skin_name, quote(type_name), ws)


    security.declarePublic('getTypeContainer')
    def getTypeContainer(self, type_name):
        """Returns the container for a given type."""
        portal = aq_parent(aq_inner(self))
        location, skin_name = self._types[str(type_name)]
        if location.startswith('/'):
            location = location[1:]
        return portal.restrictedTraverse(location)


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


    security.declareProtected(ManagePortal, 'setTypeLocation')
    def setTypeLocation(self, type, location, skin_name=''):
        """Sets a single location and skin name for a type.
        """
        t = self._types
        t[type] = (location, skin_name)
        self._types = t

    security.declareProtected(ManagePortal, 'setLocationInfo')
    def setLocationInfo(self, info, RESPONSE=None):
        """Sets the list of types, locations, and skin names.
        """
        types = {}
        for r in info:
            t = str(r['type'])
            if t:
                types[t] = (str(r['location']), str(r['skin_name']))
        self._types = types
        if RESPONSE is not None:
            RESPONSE.redirect(self.absolute_url() + '/manage_placement?' +
                              'manage_tabs_message=Saved+changes.')


InitializeClass(OrganizationTool)

