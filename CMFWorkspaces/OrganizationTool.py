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

    security.declarePublic('listAddableTypes' )
    def listAddableTypes(self):
        """Returns the list of types that can be added without specifying
        a location beforehand."""
        return ('Document', 'File')


    security.declarePublic('getAddFormURLs' )
    def getAddFormURLs(self):
        """Returns an object that maps type name to add form URL.
        """
        base = aq_parent(aq_inner(self)).absolute_url()
        return {
            'Document': base + '/Documents/document_add_form',
            'File': base + '/Files/file_add_form',
            }


InitializeClass(OrganizationTool)

