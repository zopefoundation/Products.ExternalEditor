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
Expressions in a web-configurable workflow.
$Id$
'''
__version__='$Revision$'[11:-2]

import Globals
from Globals import Persistent
from Acquisition import aq_inner, aq_parent
from AccessControl import getSecurityManager, ClassSecurityInfo
from DateTime import DateTime

from Products.CMFCore.WorkflowCore import ObjectDeleted, ObjectMoved
from Products.CMFCore.Expression import Expression
from Products.PageTemplates.Expressions import getEngine
from Products.PageTemplates.TALES import SafeMapping
from Products.PageTemplates.Expressions import SecureModuleImporter

class StateChangeInfo:
    '''
    Provides information for expressions and scripts.
    '''
    _date = None

    ObjectDeleted = ObjectDeleted
    ObjectMoved = ObjectMoved

    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

    def __init__(self, object, workflow, status=None, transition=None,
                 old_state=None, new_state=None, kwargs=None):
        if kwargs is None:
            kwargs = {}
        else:
            # Don't allow mutation
            kwargs = SafeMapping(kwargs)
        if status is None:
            tool = aq_parent(aq_inner(workflow))
            status = tool.getStatusOf(workflow.id, object)
            if status is None:
                status = {}
        if status:
            # Don't allow mutation
            status = SafeMapping(status)
        self.object = object
        self.workflow = workflow
        self.old_state = old_state
        self.new_state = new_state
        self.transition = transition
        self.status = status
        self.kwargs = kwargs

    def __getitem__(self, name):
        if name[:1] != '_' and hasattr(self, name):
            return getattr(self, name)
        raise KeyError, name

    def getHistory(self):
        wf = self.workflow
        tool = aq_parent(aq_inner(wf))
        wf_id = wf.id
        h = tool.getHistoryOf(wf_id, self.object)
        if h:
            return map(lambda dict: dict.copy(), h)  # Don't allow mutation
        else:
            return ()

    def getPortal(self):
        ob = self.object
        while ob is not None and not getattr(ob, '_isPortalRoot', 0):
            ob = aq_parent(aq_inner(ob))
        return ob

    def getDateTime(self):
        date = self._date
        if not date:
            date = self._date = DateTime()
        return date

Globals.InitializeClass(StateChangeInfo)


def createExprContext(sci):
    '''
    An expression context provides names for TALES expressions.
    '''
    ob = sci.object
    wf = sci.workflow
    data = {
        'here':         ob,
        'container':    aq_parent(aq_inner(ob)),
        'nothing':      None,
        'root':         wf.getPhysicalRoot(),
        'request':      getattr( ob, 'REQUEST', None ),
        'modules':      SecrueModuleImporter,
        'user':         getSecurityManager().getUser(),
        'state_change': sci,
        'transition':   sci.transition,
        'status':       sci.status,
        'kwargs':       sci.kwargs,
        'workflow':     wf,
        'scripts':      wf.scripts,
        }
    return getEngine().getContext(data)

