##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
##############################################################################

"""Basic workflow tool.
$Id$
"""
__version__='$Revision$'[11:-2]


import sys
from utils import UniqueObject, _checkPermission, getToolByName
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass, PersistentMapping
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from DefaultWorkflow import DefaultWorkflowDefinition
from WorkflowCore import WorkflowException


_marker = []  # Create a new marker object.


class WorkflowTool (UniqueObject, SimpleItem):
    '''
    This tool accesses and changes the workflow state of content.
    '''
    id = 'portal_workflow'
    meta_type = 'CMF Workflow Tool'

    _chains_by_type = None  # PersistentMapping
    _default_chain = ('default_workflow',)
    default_workflow = DefaultWorkflowDefinition()

    security = ClassSecurityInfo()

    security.declarePrivate('getWorkflowById')
    def getWorkflowById(self, wf_id):
        wf = getattr(self, wf_id, None)
        if getattr(wf, '_isAWorkflow', 0):
            return wf
        else:
            return None

    security.declarePrivate('getDefaultChainFor')
    def getDefaultChainFor(self, ob):
        if getattr(ob, '_isPortalContent', 0):
            # Apply a default workflow to portal content.
            return self._default_chain

    security.declarePrivate('getChainFor')
    def getChainFor(self, ob):
        '''
        Returns the chain that applies to the given object.
        '''
        cbt = self._chains_by_type
        if hasattr(aq_base(ob), '_getPortalTypeName'):
            pt = ob._getPortalTypeName()
        else:
            pt = ob.meta_type  # Use a common Zope idiom.
        chain = None
        if cbt is not None:
            chain = cbt.get(pt, None)
        if chain is None:
            chain = self.getDefaultChainFor(ob)
            if chain is None:
                return ()
        return chain

    security.declarePrivate('getWorkflowIds')
    def getWorkflowIds(self):
        '''
        Returns the list of workflow ids.
        '''
        # To do...
        return self._default_chain

    security.declarePrivate('getWorkflowsFor')
    def getWorkflowsFor(self, ob):
        '''
        Finds the Workflow objects for the type of the given object.
        '''
        res = []
        for wf_id in self.getChainFor(ob):
            wf = self.getWorkflowById(wf_id)
            if wf is not None:
                res.append(wf)
        return res

    security.declarePrivate('getCatalogVariablesFor')
    def getCatalogVariablesFor(self, ob):
        '''
        Invoked by portal_catalog.  Allows workflows
        to add variables to the catalog based on workflow status,
        making it possible to implement queues.
        Returns a mapping containing the catalog variables
        that apply to ob.
        '''
        wfs = self.getWorkflowsFor(ob)
        if wfs is None:
            return None
        # Iterate through the workflows backwards so that
        # earlier workflows can override later workflows.
        wfs.reverse()
        vars = {}
        for wf in wfs:
            v = wf.getCatalogVariablesFor(ob)
            if v is not None:
                vars.update(v)
        return vars

    security.declarePrivate('listActions')
    def listActions(self, info):
        '''
        Invoked by the portal_actions tool.  Allows workflows to
        include actions to be displayed in the actions box.
        Object actions are supplied by workflows that apply
        to the object.  Global actions are supplied by all
        workflows.
        Returns the actions to be displayed to the user.
        '''
        chain = self.getChainFor(info.content)
        did = {}
        actions = []
        for wf_id in chain:
            did[wf_id] = 1
            wf = self.getWorkflowById(wf_id)
            if wf is not None:
                a = wf.listObjectActions(info)
                if a is not None:
                    actions.extend(a)
                a = wf.listGlobalActions(info)
                if a is not None:
                    actions.extend(a)

        wf_ids = self.getWorkflowIds()
        for wf_id in wf_ids:
            if not did.has_key(wf_id):
                wf = self.getWorkflowById(wf_id)
                if wf is not None:
                    a = wf.listGlobalActions(info)
                    if a is not None:
                        actions.extend(a)
        return actions

    security.declarePublic('doActionFor')
    def doActionFor(self, ob, action, wf_id=None, *args, **kw):
        '''
        Invoked by user interface code.
        Allows the user to request a workflow action.  The workflow object
        must perform its own security checks.
        '''
        if wf_id is None:
            wfs = self.getWorkflowsFor(ob)
            if wfs is None:
                raise WorkflowException('No workflows found.')
            found = 0
            for wf in wfs:
                if wf.isActionSupported(ob, action):
                    found = 1
                    break
            if not found:
                raise WorkflowException(
                    'No workflow provides the "%s" action.' % action)
        else:
            wf = self.getWorkflowById(wf_id)
            if wf is None:
                raise WorkflowException(
                    'Requested workflow definition not found.')
        return apply(wf.doActionFor, (ob, action) + args, kw)

    security.declarePublic('getInfoFor')
    def getInfoFor(self, ob, name, default=_marker, wf_id=None, *args, **kw):
        '''
        Invoked by user interface code.  Allows the user to request
        information provided by the workflow.  The workflow object
        must perform its own security checks.
        '''
        if wf_id is None:
            wfs = self.getWorkflowsFor(ob)
            if wfs is None:
                if default is _marker:
                    raise WorkflowException('No workflows found.')
                else:
                    return default
            found = 0
            for wf in wfs:
                if wf.isInfoSupported(ob, name):
                    found = 1
                    break
            if not found:
                if default is _marker:
                    raise WorkflowException(
                        'No workflow provides "%s" information.' % name)
                else:
                    return default
        else:
            wf = self.getWorkflowById(wf_id)
            if wf is None:
                if default is _marker:
                    raise WorkflowException(
                        'Requested workflow definition not found.')
                else:
                    return default
        res = apply(wf.getInfoFor, (ob, name, default) + args, kw)
        if res is _marker:
            raise WorkflowException('Could not get info: %s' % name)
        return res

    security.declarePrivate('notifyCreated')
    def notifyCreated(self, ob):
        '''
        Notifies all applicable workflows after an object has been created
        and put in its new place.
        '''
        wfs = self.getWorkflowsFor(ob)
        for wf in wfs:
            wf.notifyCreated(ob)

    security.declarePrivate('notifyBefore')
    def notifyBefore(self, ob, action):
        '''
        Notifies all applicable workflows of an action before it happens,
        allowing veto by exception.  Unless an exception is thrown, either
        a notifySuccess() or notifyException() can be expected later on.
        The action usually corresponds to a method name.
        '''
        wfs = self.getWorkflowsFor(ob)
        for wf in wfs:
            wf.notifyBefore(ob, action)

    security.declarePrivate('notifySuccess')
    def notifySuccess(self, ob, action, result=None):
        '''
        Notifies all applicable workflows that an action has taken place.
        '''
        wfs = self.getWorkflowsFor(ob)
        for wf in wfs:
            wf.notifySuccess(ob, action, result)

    security.declarePrivate('notifyException')
    def notifyException(self, ob, action, exc):
        '''
        Notifies all applicable workflows that an action failed.
        '''
        wfs = self.getWorkflowsFor(ob)
        for wf in wfs:
            wf.notifyException(ob, action, exc)

    security.declarePrivate('getHistoryOf')
    def getHistoryOf(self, wf_id, ob):
        '''
        Invoked by workflow definitions.  Returns the history
        of an object.
        '''
        if hasattr(aq_base(ob), 'workflow_history'):
            wfh = ob.workflow_history
            return wfh.get(wf_id, None)
        return ()

    security.declarePrivate('getStatusOf')
    def getStatusOf(self, wf_id, ob):
        '''
        Invoked by workflow definitions.  Returns the last element of a
        history.
        '''
        wfh = self.getHistoryOf(wf_id, ob)
        if wfh:
            return wfh[-1]
        return None

    security.declarePrivate('setStatusOf')
    def setStatusOf(self, wf_id, ob, status):
        '''
        Invoked by workflow definitions.  Appends to the workflow history.
        '''
        wfh = None
        has_history = 0
        if hasattr(aq_base(ob), 'workflow_history'):
            history = ob.workflow_history
            if history is not None:
                has_history = 1
                wfh = history.get(wf_id, None)
                if wfh is not None:
                    wfh = list(wfh)
        if not wfh:
            wfh = []
        wfh.append(status)
        if not has_history:
            ob.workflow_history = PersistentMapping()
        ob.workflow_history[wf_id] = tuple(wfh)

InitializeClass(WorkflowTool)
