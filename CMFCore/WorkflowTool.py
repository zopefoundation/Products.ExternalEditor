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

"""Basic workflow tool.
$Id$
"""
__version__='$Revision$'[11:-2]

import sys
from utils import UniqueObject, _checkPermission, getToolByName, _dtmldir
from OFS.Folder import Folder
from Globals import InitializeClass, PersistentMapping, DTMLFile
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner, aq_parent
from WorkflowCore import WorkflowException, ObjectDeleted, ObjectMoved
import CMFCorePermissions
from string import join, split, replace, strip

AUTO_MIGRATE_WORKFLOW_TOOLS = 0  # Set to 1 to auto-migrate


_marker = []  # Create a new marker object.

class WorkflowInformation:
    """
        Shim implementation of ActionInformation, to enable
        querying actions without mediation of the 'portal_actions' tool.
    """
    def __init__(self, object):
        self.content = object
        self.content_url = object.absolute_url()
        self.portal_url = self.folder_url = ''

    def __getitem__(self, name):
        if name[:1] == '_':
            raise KeyError, name
        if hasattr(self, name):
            return getattr(self, name)
        raise KeyError, name


class WorkflowTool (UniqueObject, Folder):
    '''
    This tool accesses and changes the workflow state of content.
    '''
    id = 'portal_workflow'
    meta_type = 'CMF Workflow Tool'

    _chains_by_type = None  # PersistentMapping
    _default_chain = ('default_workflow',)

    security = ClassSecurityInfo()

    manage_options = ( { 'label' : 'Workflows'
                       , 'action' : 'manage_selectWorkflows'
                       }
                     , { 'label' : 'Overview', 'action' : 'manage_overview' }
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
        for key in _workflow_factories.keys():
            wft.append(key)
        wft.sort()
        return self._manage_addWorkflowForm(REQUEST, workflow_types=wft)

    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'manage_addWorkflow')
    def manage_addWorkflow(self, workflow_type, id, RESPONSE=None):
        '''
        Adds a workflow from the registered types.
        '''
        factory = _workflow_factories[workflow_type]
        ob = factory(id)
        self._setObject(id, ob)
        if RESPONSE is not None:
            RESPONSE.redirect(self.absolute_url() +
                              '/manage_main?management_view=Contents')

    def all_meta_types(self):
        return (
            {'name': 'Workflow',
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

    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'setDefaultChain')
    def setDefaultChain(self, default_chain):
        """ Set the default chain """
        default_chain = replace(default_chain, ',', ' ')
        ids = []
        for wf_id in split(default_chain, ' '):
            if wf_id:
                if not self.getWorkflowById(wf_id):
                    raise ValueError, ( '"%s" is not a workflow ID.' % wf_id)
                ids.append(wf_id)

        self._default_chain = tuple(ids)

    security.declareProtected(CMFCorePermissions.ManagePortal,
                              'setChainForPortalTypes')
    def setChainForPortalTypes(self, pt_names, chain):
        """ Set a chain for a specific portal type """
        cbt = self._chains_by_type
        if cbt is None:
            self._chains_by_type = cbt = PersistentMapping()

        if type(chain) is type(''):
            chain = map(strip, split(chain,','))

        ti = self._listTypeInfo()
        for t in ti:
            id = t.getId()
            if id in pt_names:
                cbt[id] = tuple(chain)


    security.declareProtected(CMFCorePermissions.ManagePortal,
                              'updateRoleMappings')
    def updateRoleMappings(self, REQUEST=None):
        '''
        '''
        wfs = {}
        for id in self.objectIds():
            wf = self.getWorkflowById(id)
            if hasattr(aq_base(wf), 'updateRoleMappingsFor'):
                wfs[id] = wf
        portal = aq_parent(aq_inner(self))
        count = self._recursiveUpdateRoleMappings(portal, wfs)
        if REQUEST is not None:
            return self.manage_selectWorkflows(REQUEST, manage_tabs_message=
                                               '%d object(s) updated.' % count)
        else:
            return count

    def _recursiveUpdateRoleMappings(self, ob, wfs):
        # Returns a count of updated objects.
        count = 0
        wf_ids = self.getChainFor(ob)
        if wf_ids:
            changed = 0
            for wf_id in wf_ids:
                wf = wfs.get(wf_id, None)
                if wf is not None:
                    did = wf.updateRoleMappingsFor(ob)
                    if did: changed = 1
            if changed:
                count = count + 1
        if hasattr(aq_base(ob), 'objectItems'):
            obs = ob.objectItems()
            if obs:
                for k, v in obs:
                    changed = getattr(v, '_p_changed', 0)
                    count = count + self._recursiveUpdateRoleMappings(v, wfs)
                    if changed is None:
                        # Re-ghostify.
                        v._p_deactivate()
        return count

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
        wf_ids = []

        for obj_name, obj in self.objectItems():
            if getattr(obj, '_isAWorkflow', 0):
                wf_ids.append(obj_name)

        return tuple(wf_ids)

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

    security.declarePublic('getActionsFor')
    def getActionsFor(self, ob):
        '''
        Return a list of action dictionaries for 'ob', just as though
        queried via 'ActionsTool.listFilteredActionsFor'.
        '''
        return self.listActions( WorkflowInformation( ob ) )

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

    def _invokeWithNotification(self, wfs, ob, action, func, args, kw):
        '''
        Private utility method.
        '''
        reindex = 1
        for w in wfs:
            w.notifyBefore(ob, action)
        try:
            res = apply(func, args, kw)
        except ObjectDeleted, ex:
            res = ex.getResult()
            reindex = 0
        except ObjectMoved, ex:
            res = ex.getResult()
            ob = ex.getNewObject()
        except:
            exc = sys.exc_info()
            try:
                for w in wfs:
                    w.notifyException(ob, action, exc)
                raise exc[0], exc[1], exc[2]
            finally:
                exc = None
        for w in wfs:
            w.notifySuccess(ob, action, res)
        if reindex:
            catalog = getToolByName(ob, 'portal_catalog', None)
            if catalog is not None:
                catalog.reindexObject(ob)
        return res

    security.declarePublic('doActionFor')
    def doActionFor(self, ob, action, wf_id=None, *args, **kw):
        '''
        Invoked by user interface code.
        Allows the user to request a workflow action.  The workflow object
        must perform its own security checks.
        '''
        wfs = self.getWorkflowsFor(ob)
        if wfs is None:
            wfs = ()
        if wf_id is None:
            if not wfs:
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
        return self._invokeWithNotification(
            wfs, ob, action, wf.doActionFor, (ob, action) + args, kw)

    security.declarePrivate('wrapWorkflowMethod')
    def wrapWorkflowMethod(self, ob, method_id, func, args, kw):
        '''
        To be invoked only by WorkflowCore.
        Allows a workflow definition to wrap a WorkflowMethod.
        '''
        wf = None
        wfs = self.getWorkflowsFor(ob)
        if wfs:
            for w in wfs:
                if (hasattr(w, 'isWorkflowMethodSupported')
                    and w.isWorkflowMethodSupported(ob, method_id)):
                    wf = w
                    break
        else:
            wfs = ()
        if wf is None:
            # No workflow wraps this method.
            return apply(func, args, kw)
        return self._invokeWithNotification(
            wfs, ob, method_id, wf.wrapWorkflowMethod,
            (ob, method_id, func, args, kw), {})

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


_workflow_factories = {}

def addWorkflowFactory(factory, id=None, title=None):
    # The factory should take one argument, id.
    if id is None:
        id = getattr(factory, 'id', '') or getattr(factory, 'meta_type', '')
    if title is None:
        title = getattr(factory, 'title', '')
    key = id
    if title:
        key = key + ' (%s)' % title
    _workflow_factories[key] = factory

addWorkflowClass = addWorkflowFactory  # bw compat.

