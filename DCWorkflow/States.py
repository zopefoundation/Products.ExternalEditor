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
        {'label': 'Variables', 'action': 'manage_vars'},
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

    def getVarValues(self):
        vv = self.var_values
        if vv is None:
            return []
        else:
            return vv.items()

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
        return self.getWorkflow().vars.keys()

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
