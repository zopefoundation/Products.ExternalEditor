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
States in a web-configurable workflow.
$Id$
'''
__version__='$Revision$'[11:-2]

from string import join

from Acquisition import aq_inner, aq_parent
import Globals
from Globals import DTMLFile, PersistentMapping
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo

from Products.CMFCore.CMFCorePermissions import ManagePortal

from ContainerTab import ContainerTab
from utils import _dtmldir


TupleType = type(())


class StateDefinition (SimpleItem):
    meta_type = 'Workflow State'

    manage_options = (
        {'label': 'Properties', 'action': 'manage_properties'},
        {'label': 'Permissions', 'action': 'manage_permissions'},
        {'label': 'Variables', 'action': 'manage_variables'},
        )

    title = ''
    transitions = ()  # The ids of possible transitions.
    permission_roles = None
    var_values = None  # PersistentMapping if set.  Overrides transition exprs.

    security = ClassSecurityInfo()
    security.declareObjectProtected(ManagePortal)

    def __init__(self, id):
        self.id = id

    def getId(self):
        return self.id

    def getWorkflow(self):
        return aq_parent(aq_inner(aq_parent(aq_inner(self))))

    def getTransitions(self):
        return list(self.transitions)

    def getTransitionTitle(self, tid):
        t = self.getWorkflow().transitions.get(tid, None)
        if t is not None:
            return t.title
        return ''

    def getAvailableTransitionIds(self):
        return self.getWorkflow().transitions.keys()

    def getAvailableVarIds(self):
        return self.getWorkflow().variables.keys()

    def getManagedPermissions(self):
        return list(self.getWorkflow().permissions)

    def getAvailableRoles(self):
        return list(self.valid_roles())

    def getPermissionInfo(self, p):
        roles = None
        if self.permission_roles:
            roles = self.permission_roles.get(p, None)
        if roles is None:
            return {'acquired':1, 'roles':[]}
        else:
            if type(roles) is TupleType:
                acq = 0
            else:
                acq = 1
            return {'acquired':acq, 'roles':list(roles)}

    _properties_form = DTMLFile('state_properties', _dtmldir)

    def manage_properties(self, REQUEST, manage_tabs_message=None):
        '''
        '''
        return self._properties_form(REQUEST,
                                     management_view='Properties',
                                     manage_tabs_message=manage_tabs_message,
                                     )

    def setProperties(self, title='', transitions=(), REQUEST=None):
        '''
        '''
        self.title = str(title)
        self.transitions = tuple(map(str, transitions))
        if REQUEST is not None:
            return self.manage_properties(REQUEST, 'Properties changed.')


    _variables_form = DTMLFile('state_variables', _dtmldir)

    def manage_variables(self, REQUEST, manage_tabs_message=None):
        '''
        '''
        return self._variables_form(REQUEST,
                                     management_view='Variables',
                                     manage_tabs_message=manage_tabs_message,
                                     )

    def getVariableValues(self):
        ''' get VariableValues for management UI
        '''
        vv = self.var_values
        if vv is None:
            return []
        else:
            return vv.items()
    
    def getWorkflowVariables(self):
        ''' get all variables that are available form
            workflow and not handled yet.
        '''
        wf_vars = self.getAvailableVarIds()
        if self.var_values is None:
                return wf_vars
        ret = []
        for vid in wf_vars:
            if not self.var_values.has_key(vid):
                ret.append(vid)
        return ret

    def addVariable(self,id,value,REQUEST=None):
        ''' add a WorkflowVariable to State
        '''
        if self.var_values is None:
            self.var_values = PersistentMapping()
        
        self.var_values[id] = value
        
        if REQUEST is not None:
            return self.manage_variables(REQUEST, 'Variable added.')
    
    def deleteVariables(self,ids=[],REQUEST=None):
        ''' delete a WorkflowVariable from State
        '''
        vv = self.var_values
        for id in ids:
            if vv.has_key(id):
                del vv[id]
                
        if REQUEST is not None:
            return self.manage_variables(REQUEST, 'Variables deleted.')

    def setVariables(self, ids=[], REQUEST=None):
        ''' set values for Variables set by this state
        '''
        if self.var_values is None:
            self.var_values = PersistentMapping()
 
        vv = self.var_values
 
        if REQUEST is not None:
            for id in vv.keys():
                fname = 'varval_%s' % id
                vv[id] = str(REQUEST[fname])
            return self.manage_variables(REQUEST, 'Variables changed.')



    _permissions_form = DTMLFile('state_permissions', _dtmldir)

    def manage_permissions(self, REQUEST, manage_tabs_message=None):
        '''
        '''
        
        return self._permissions_form(REQUEST,
                                     management_view='Permissions',
                                     manage_tabs_message=manage_tabs_message,
                                     )

    def setPermissions(self, REQUEST):
        '''
        '''
        pr = self.permission_roles
        if pr is None:
            self.permission_roles = pr = PersistentMapping()
        for p in self.getManagedPermissions():
            roles = []
            acquired = REQUEST.get('acquire_' + p, 0)
            for r in self.getAvailableRoles():
                if REQUEST.get('%s|%s' % (p, r), 0):
                    roles.append(r)
            roles.sort()
            if not acquired:
                roles = tuple(roles)
            pr[p] = roles
        return self.manage_permissions(REQUEST, 'Permissions changed.')

    def setPermission(self, permission, acquired, roles):
        '''
        '''
        pr = self.permission_roles
        if pr is None:
            self.permission_roles = pr = PersistentMapping()
        if acquired:
            roles = list(roles)
        else:
            roles = tuple(roles)
        pr[permission] = roles

Globals.InitializeClass(StateDefinition)


class States (ContainerTab):

    meta_type = 'Workflow States'

    security = ClassSecurityInfo()
    security.declareObjectProtected(ManagePortal)

    all_meta_types = ({'name':StateDefinition.meta_type,
                       'action':'addState',
                       },)

    _manage_states = DTMLFile('states', _dtmldir)

    def manage_main(self, REQUEST, manage_tabs_message=None):
        '''
        '''
        return self._manage_states(REQUEST,
                                   management_view='States',
                                   manage_tabs_message=manage_tabs_message,
                                   )

    def addState(self, id, REQUEST=None):
        '''
        '''
        sdef = StateDefinition(id)
        self._setObject(id, sdef)
        if REQUEST is not None:
            return self.manage_main(REQUEST, 'State added.')

    def deleteStates(self, ids, REQUEST=None):
        '''
        '''
        for id in ids:
            self._delObject(id)
        if REQUEST is not None:
            return self.manage_main(REQUEST, 'State(s) removed.')

    def setInitialState(self, id=None, ids=None, REQUEST=None):
        '''
        '''
        if not id:
            if len(ids) != 1:
                raise ValueError, 'One and only one state must be selected'
            id = ids[0]
        id = str(id)
        aq_parent(aq_inner(self)).initial_state = id
        if REQUEST is not None:
            return self.manage_main(REQUEST, 'Initial state selected.')

Globals.InitializeClass(States)
