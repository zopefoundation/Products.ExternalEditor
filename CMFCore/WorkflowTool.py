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
from utils import UniqueObject, _checkPermission, getToolByName, _dtmldir
from OFS.Folder import Folder
from Globals import InitializeClass, PersistentMapping, DTMLFile
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from WorkflowCore import WorkflowException
import CMFCorePermissions
from string import join, split, replace, strip

AUTO_MIGRATE_WORKFLOW_TOOLS = 1  # This will later be set to 0.


_marker = []  # Create a new marker object.


class WorkflowTool (UniqueObject, Folder):
    '''
    This tool accesses and changes the workflow state of content.
    '''
    id = 'portal_workflow'
    meta_type = 'CMF Workflow Tool'

    _chains_by_type = None  # PersistentMapping
    _default_chain = ('default_workflow',)

    security = ClassSecurityInfo()

    manage_options = ( { 'label' : 'Overview', 'action' : 'manage_overview' }
                     , { 'label' : 'Workflows'
                       , 'action' : 'manage_selectWorkflows'
                       }
                     ) + Folder.manage_options

    #
    #   ZMI methods
    #
    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'manage_overview' )
    manage_overview = DTMLFile( 'explainWorkflowTool', _dtmldir )

    if AUTO_MIGRATE_WORKFLOW_TOOLS:
        def __setstate__(self, state):
            # Adds default_workflow to persistent WorkflowTool instances.
            # This is temporary!
            WorkflowTool.inheritedAttribute('__setstate__')(self, state)
            if not self.__dict__.has_key('default_workflow'):
                try:
                    from Products.CMFDefault import DefaultWorkflow
                except ImportError:
                    pass
                else:
                    self.default_workflow = (
                        DefaultWorkflow.DefaultWorkflowDefinition(
                        'default_workflow'))
                    self._objects = self._objects + (
                        {'id': 'default_workflow',
                         'meta_type': self.default_workflow.meta_type},)

    _manage_addWorkflowForm = DTMLFile('addWorkflow', _dtmldir)

    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'manage_addWorkflowForm')
    def manage_addWorkflowForm(self, REQUEST):
        '''
        Form for adding workflows.
        '''
        wft = []
        for mt, klass in _workflow_classes.items():
            wft.append((mt, '%s (%s)' % (klass.id, klass.title)))
        wft.sort()
        return self._manage_addWorkflowForm(REQUEST, workflow_types=wft)

    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'manage_addWorkflow')
    def manage_addWorkflow(self, workflow_type, id='', RESPONSE=None):
        '''
        Adds a workflow from the registered types.
        '''
        klass = _workflow_classes[workflow_type]
        if not id:
            id = klass.id
        ob = klass(id)
        self._setObject(id, ob)
        if RESPONSE is not None:
            RESPONSE.redirect(self.absolute_url() +
                              '/manage_main?management_view=Contents')

    def all_meta_types(self):
        mt = WorkflowTool.inheritedAttribute('all_meta_types')(self)
        return mt + ({'name': 'Workflow',
                      'action': 'manage_addWorkflowForm',
                      'permission': CMFCorePermissions.ManagePortal },)

    def _listTypeInfo(self):
        pt = getToolByName(self, 'portal_types', None)
        if pt is None:
            return ()
        else:
            return pt.listTypeInfo()

    _manage_selectWorkflows = DTMLFile('selectWorkflows', _dtmldir)

    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'manage_selectWorkflows')
    def manage_selectWorkflows(self, REQUEST, manage_tabs_message=None):
        '''
        Shows a management screen for changing type to workflow connections.
        '''
        cbt = self._chains_by_type
        ti = self._listTypeInfo()
        types_info = []
        for t in ti:
            id = t.getId()
            title = t.Type()
            if title == id:
                title = None
            if cbt is not None and cbt.has_key(id):
                chain = join(cbt[id], ', ')
            else:
                chain = '(Default)'
            types_info.append({'id': id,
                               'title': title,
                               'chain': chain})
        return self._manage_selectWorkflows(
            REQUEST,
            default_chain=join(self._default_chain, ', '),
            types_info=types_info,
            management_view='Workflows',
            manage_tabs_message=manage_tabs_message)

    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'manage_changeWorkflows')
    def manage_changeWorkflows(self, default_chain, props=None, REQUEST=None):
        '''
        Changes which workflows apply to objects of which type.
        '''
        if props is None:
            props = REQUEST
        cbt = self._chains_by_type
        if cbt is None:
            self._chains_by_type = cbt = PersistentMapping()
        ti = self._listTypeInfo()
        # Set up the chains by type.
        for t in ti:
            id = t.getId()
            field_name = 'chain_%s' % id
            chain = strip(props.get(field_name, '(Default)'))
            if chain == '(Default)':
                # Remove from cbt.
                if cbt.has_key(id):
                    del cbt[id]
            else:
                chain = replace(chain, ',', ' ')
                ids = []
                for wf_id in split(chain, ' '):
                    if wf_id:
                        if not self.getWorkflowById(wf_id):
                            raise ValueError, (
                                '"%s" is not a workflow ID.' % wf_id)
                        ids.append(wf_id)
                cbt[id] = tuple(ids)
        # Set up the default chain.
        default_chain = replace(default_chain, ',', ' ')
        ids = []
        for wf_id in split(default_chain, ' '):
            if wf_id:
                if not self.getWorkflowById(wf_id):
                    raise ValueError, (
                        '"%s" is not a workflow ID.' % wf_id)
                ids.append(wf_id)
        self._default_chain = tuple(ids)
        if REQUEST is not None:
            return self.manage_selectWorkflows(REQUEST, manage_tabs_message=
                                               'Changed.')

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
            # Note that if chain is not in cbt or has a value of
            # None, we use a default chain.
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


_workflow_classes = {}

def addWorkflowClass(klass):
    # klass is expected to have id, title, and meta_type attributes.
    # Its constructor should take one argument, id.
    _workflow_classes[klass.meta_type] = klass
