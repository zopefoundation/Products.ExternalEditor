##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
"""WorkflowRepository class.

$Id$
"""

import os

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from BTrees.OOBTree import OOBTree
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import SimpleItemWithProperties

from permissions import ManagePortal

_www = os.path.join(os.path.dirname(__file__), 'www')


class WorkflowRepository (SimpleItemWithProperties):
    """An object where a workflow tool stores object status.
    """
    meta_type = 'Workflow Repository'

    security = ClassSecurityInfo()

    manage_options = (
        {'label': 'Info', 'action': 'manage_main'},
        ) + SimpleItemWithProperties.manage_options

    manage_main = PageTemplateFile('workflowRepositoryInfo', _www)

    _properties = ()

    def __init__(self, id):
        self.id = id
        self._histories = OOBTree()

    security.declarePrivate('getHistory')
    def getHistory(self, id):
        return self._histories.get(id)

    security.declarePrivate('setHistory')
    def setHistory(self, id, h):
        self._histories[id] = h

    security.declareProtected(ManagePortal, 'countHistories')
    def countHistories(self):
        return len(self._histories)

InitializeClass(WorkflowRepository)


manage_addWorkflowRepositoryForm = PageTemplateFile(
    'addWorkflowRepository', _www)

def manage_addWorkflowRepository(dispatcher, id, REQUEST=None):
    """ """
    ob = WorkflowRepository(id)
    dispatcher._setObject(id, ob)
    if REQUEST is not None:
        return dispatcher.manage_main(dispatcher, REQUEST)

