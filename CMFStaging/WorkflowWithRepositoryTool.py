##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""WorkflowWithRepositoryTool class.

$Id$
"""

import Globals
from Acquisition import aq_inner, aq_parent
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowTool import WorkflowTool
from Persistence import PersistentMapping


class WorkflowWithRepositoryTool (WorkflowTool):
    """Workflow tool that uses a workflow status repository.

    Depends on portal_versions."""

    meta_type = 'Workflow Tool (repository aware)'

    security = ClassSecurityInfo()

    def _getId(self, ob, allow_create_version=0):
        vt = getToolByName(self, 'portal_versions')
        if not vt.isUnderVersionControl(ob):
            if allow_create_version:
                vt.checkin(ob, 'Auto checkin by workflow')
            else:
                return None
        return vt.getHistoryId(ob)

    def _getRepository(self):
        parent = aq_parent(aq_inner(self))
        try:
            repo = parent.workflow_repository
        except AttributeError:
            raise RuntimeError, 'A workflow_repository object is required.'
        return repo

    security.declarePrivate('getHistoryOf')
    def getHistoryOf(self, wf_id, ob):
        """Invoked by workflow definitions.  Returns the history of an object.
        """
        ob_id = self._getId(ob)
        if ob_id is None:
            return ()
        repo = self._getRepository()
        h = repo.getHistory(ob_id)
        if h is None:
            return None
        else:
            return h.get(wf_id, None)

    security.declarePrivate('setStatusOf')
    def setStatusOf(self, wf_id, ob, status):
        """Invoked by workflow definitions.  Appends to the workflow history.
        """
        ob_id = self._getId(ob, 1)
        assert ob_id, 'No version history ID available'
        repo = self._getRepository()
        h = repo.getHistory(ob_id)
        if h is None:
            h = PersistentMapping()
            repo.setHistory(ob_id, h)
        wfh = h.get(wf_id)
        if wfh is not None:
            wfh = list(wfh)
        else:
            wfh = []
        wfh.append(status)
        h[wf_id] = tuple(wfh)

Globals.InitializeClass(WorkflowWithRepositoryTool)

