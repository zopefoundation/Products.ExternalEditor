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
Transitions in a web-configurable workflow.
$Id$
'''
__version__='$Revision$'[11:-2]

from string import join, split, strip

from OFS.SimpleItem import SimpleItem
from Globals import DTMLFile, PersistentMapping
from Acquisition import aq_inner, aq_parent
import Globals
from AccessControl import ClassSecurityInfo

from Products.CMFCore.CMFCorePermissions import ManagePortal

from ContainerTab import ContainerTab
from Guard import Guard
from utils import _dtmldir
from Expression import Expression

TRIGGER_AUTOMATIC = 0
TRIGGER_USER_ACTION = 1
TRIGGER_WORKFLOW_METHOD = 2


class TransitionDefinition (SimpleItem):
    meta_type = 'Workflow Transition'

    security = ClassSecurityInfo()
    security.declareObjectProtected(ManagePortal)

    title = ''
    new_state_id = ''
    trigger_type = TRIGGER_USER_ACTION
    guard = None
    actbox_name = ''
    actbox_url = ''
    actbox_category = 'workflow'
    var_exprs = None  # A mapping.
    script_name = None  # Executed before transition
    after_script_name = None  # Executed after transition

    manage_options = (
        {'label': 'Properties', 'action': 'manage_properties'},
        {'label': 'Variables', 'action': 'manage_variables'},
        )

    def __init__(self, id):
        self.id = id

    def getId(self):
        return self.id

    def getGuardSummary(self):
        res = None
        if self.guard is not None:
            res = self.guard.getSummary()
        return res

    def getGuard(self):
        if self.guard is not None:
            return self.guard
        else:
            return Guard()  # Create a temporary guard.

    def getVarExprText(self, id):
        if not self.var_exprs:
            return ''
        else:
            expr = self.var_exprs.get(id, None)
            if expr is not None:
                return expr.text
            else:
                return ''

    def getWorkflow(self):
        return aq_parent(aq_inner(aq_parent(aq_inner(self))))

    def getAvailableStateIds(self):
        return self.getWorkflow().states.keys()

    def getAvailableScriptIds(self):
        return self.getWorkflow().scripts.keys()

    def getAvailableVarIds(self):
        return self.getWorkflow().variables.keys()

    _properties_form = DTMLFile('transition_properties', _dtmldir)

    def manage_properties(self, REQUEST, manage_tabs_message=None):
        '''
        '''
        return self._properties_form(REQUEST,
                                     management_view='Properties',
                                     manage_tabs_message=manage_tabs_message,
                                     )

    def setProperties(self, title, new_state_id,
                      trigger_type=TRIGGER_USER_ACTION, script_name='',
                      after_script_name='',
                      actbox_name='', actbox_url='',
                      actbox_category='workflow',
                      props=None, REQUEST=None):
        '''
        '''
        self.title = str(title)
        self.new_state_id = str(new_state_id)
        self.trigger_type = int(trigger_type)
        self.script_name = str(script_name)
        self.after_script_name = str(after_script_name)
        g = Guard()
        if g.changeFromProperties(props or REQUEST):
            self.guard = g
        else:
            self.guard = None
        self.actbox_name = str(actbox_name)
        self.actbox_url = str(actbox_url)
        self.actbox_category = str(actbox_category)
        if REQUEST is not None:
            return self.manage_properties(REQUEST, 'Properties changed.')

    _variables_form = DTMLFile('transition_variables', _dtmldir)

    def manage_variables(self, REQUEST, manage_tabs_message=None):
        '''
        '''
        return self._variables_form(REQUEST,
                                     management_view='Variables',
                                     manage_tabs_message=manage_tabs_message,
                                     )

    def getVariableExprs(self):
        ''' get variable exprs for management UI
        '''
        ve = self.var_exprs
        if ve is None:
            return []
        else:
            ret = []
            for key in ve.keys():
                ret.append((key,self.getVarExprText(key)))
            return ret
    
    def getWorkflowVariables(self):
        ''' get all variables that are available form
            workflow and not handled yet.
        '''
        wf_vars = self.getAvailableVarIds()
        if self.var_exprs is None:
                return wf_vars
        ret = []
        for vid in wf_vars:
            if not self.var_exprs.has_key(vid):
                ret.append(vid)
        return ret

    def addVariable(self, id, text, REQUEST=None):
        '''
        Add a variable expression.
        '''
        if self.var_exprs is None:
            self.var_exprs = PersistentMapping()
        
        expr = None
        if text:
          expr = Expression(str(text))
        self.var_exprs[id] = expr
        
        if REQUEST is not None:
            return self.manage_variables(REQUEST, 'Variable added.')
    
    def deleteVariables(self,ids=[],REQUEST=None):
        ''' delete a WorkflowVariable from State
        '''
        ve = self.var_exprs
        for id in ids:
            if ve.has_key(id):
                del ve[id]
                
        if REQUEST is not None:
            return self.manage_variables(REQUEST, 'Variables deleted.')

    def setVariables(self, ids=[], REQUEST=None):
        ''' set values for Variables set by this state
        '''
        if self.var_exprs is None:
            self.var_exprs = PersistentMapping()
 
        ve = self.var_exprs
 
        if REQUEST is not None:
            for id in ve.keys():
                fname = 'varexpr_%s' % id

                val = REQUEST[fname]
                expr = None
                if val:
                    expr = Expression(str(REQUEST[fname]))
                ve[id] = expr

            return self.manage_variables(REQUEST, 'Variables changed.')

Globals.InitializeClass(TransitionDefinition)


class Transitions (ContainerTab):

    meta_type = 'Workflow Transitions'

    security = ClassSecurityInfo()
    security.declareObjectProtected(ManagePortal)

    all_meta_types = ({'name':TransitionDefinition.meta_type,
                       'action':'addTransition',
                       },)

    _manage_transitions = DTMLFile('transitions', _dtmldir)

    def manage_main(self, REQUEST, manage_tabs_message=None):
        '''
        '''
        return self._manage_transitions(
            REQUEST,
            management_view='Transitions',
            manage_tabs_message=manage_tabs_message,
            )

    def addTransition(self, id, REQUEST=None):
        '''
        '''
        tdef = TransitionDefinition(id)
        self._setObject(id, tdef)
        if REQUEST is not None:
            return self.manage_main(REQUEST, 'Transition added.')

    def deleteTransitions(self, ids, REQUEST=None):
        '''
        '''
        for id in ids:
            self._delObject(id)
        if REQUEST is not None:
            return self.manage_main(REQUEST, 'Transition(s) removed.')

Globals.InitializeClass(Transitions)
