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
'''
Worklists in a web-configurable workflow.
$Id$
'''
__version__='$Revision$'[11:-2]

from OFS.SimpleItem import SimpleItem
from Globals import DTMLFile, PersistentMapping
from Acquisition import aq_inner, aq_parent
import Globals
from AccessControl import ClassSecurityInfo

from Products.CMFCore.CMFCorePermissions import ManagePortal

from ContainerTab import ContainerTab
from Guard import Guard
from utils import _dtmldir


class WorklistDefinition (SimpleItem):
    meta_type = 'Worklist'

    security = ClassSecurityInfo()
    security.declareObjectProtected(ManagePortal)

    description = ''
    var_matches = None  # Compared with catalog when set.
    actbox_name = ''
    actbox_url = ''
    actbox_category = 'global'
    guard = None

    manage_options = (
        {'label': 'Properties', 'action': 'manage_properties'},
        )

    def __init__(self, id):
        self.id = id

    def getGuard(self):
        if self.guard is not None:
            return self.guard
        else:
            return Guard()  # Create a temporary guard.

    def getGuardSummary(self):
        res = None
        if self.guard is not None:
            res = self.guard.getSummary()
        return res

    def getWorkflow(self):
        return aq_parent(aq_inner(aq_parent(aq_inner(self))))

    def getAvailableCatalogVars(self):
        res = []
        res.append(self.getWorkflow().state_var)
        for id, vdef in self.getWorkflow().variables.items():
            if vdef.for_catalog:
                res.append(id)
        res.sort()
        return res

    def getVarMatch(self, id):
        if self.var_matches:
            return self.var_matches.get(id, '')
        else:
            return ''

    _properties_form = DTMLFile('worklist_properties', _dtmldir)

    def manage_properties(self, REQUEST, manage_tabs_message=None):
        '''
        '''
        return self._properties_form(REQUEST,
                                     management_view='Properties',
                                     manage_tabs_message=manage_tabs_message,
                                     )

    def setProperties(self, description,
                      actbox_name='', actbox_url='', actbox_category='global',
                      props=None, REQUEST=None):
        '''
        '''
        if props is None:
            props = REQUEST
        self.description = str(description)
        for key in self.getAvailableCatalogVars():
            # Populate var_matches.
            fieldname = 'var_match_%s' % key
            v = props.get(fieldname, '')
            if v:
                if not self.var_matches:
                    self.var_matches = PersistentMapping()
                self.var_matches[key] = str(v)
            else:
                if self.var_matches and self.var_matches.has_key(key):
                    del self.var_matches[key]
        self.actbox_name = str(actbox_name)
        self.actbox_url = str(actbox_url)
        self.actbox_category = str(actbox_category)
        g = Guard()
        if g.changeFromProperties(props or REQUEST):
            self.guard = g
        else:
            self.guard = None
        if REQUEST is not None:
            return self.manage_properties(REQUEST, 'Properties changed.')

Globals.InitializeClass(WorklistDefinition)


class Worklists (ContainerTab):

    meta_type = 'Worklists'

    security = ClassSecurityInfo()
    security.declareObjectProtected(ManagePortal)

    all_meta_types = ({'name':WorklistDefinition.meta_type,
                       'action':'addWorklist',
                       },)

    _manage_worklists = DTMLFile('worklists', _dtmldir)

    def manage_main(self, REQUEST, manage_tabs_message=None):
        '''
        '''
        return self._manage_worklists(
            REQUEST,
            management_view='Worklists',
            manage_tabs_message=manage_tabs_message,
            )

    def addWorklist(self, id, REQUEST=None):
        '''
        '''
        qdef = WorklistDefinition(id)
        self._setObject(id, qdef)
        if REQUEST is not None:
            return self.manage_main(REQUEST, 'Worklist added.')

    def deleteWorklists(self, ids, REQUEST=None):
        '''
        '''
        for id in ids:
            self._delObject(id)
        if REQUEST is not None:
            return self.manage_main(REQUEST, 'Worklist(s) removed.')

Globals.InitializeClass(Worklists)
