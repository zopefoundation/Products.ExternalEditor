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
Variables in a web-configurable workflow.
$Id$
'''
__version__='$Revision$'[11:-2]

from string import join, split, strip

from OFS.SimpleItem import SimpleItem
from Globals import DTMLFile
from Acquisition import aq_inner, aq_parent
import Globals
from AccessControl import ClassSecurityInfo

from Products.CMFCore.CMFCorePermissions import ManagePortal

from ContainerTab import ContainerTab
from Guard import Guard
from Expression import Expression
from utils import _dtmldir


class VariableDefinition (SimpleItem):
    meta_type = 'Workflow Variable'

    security = ClassSecurityInfo()
    security.declareObjectProtected(ManagePortal)

    description = ''
    for_catalog = 1
    for_status = 1
    default_value = ''
    default_expr = None  # Overrides default_value if set
    info_guard = None
    update_always = 1

    manage_options = (
        {'label': 'Properties', 'action': 'manage_properties'},
        )

    def __init__(self, id):
        self.id = id

    def getDefaultExprText(self):
        if not self.default_expr:
            return ''
        else:
            return self.default_expr.text

    def getInfoGuard(self):
        if self.info_guard is not None:
            return self.info_guard
        else:
            return Guard()  # Create a temporary guard.

    def getInfoGuardSummary(self):
        res = None
        if self.info_guard is not None:
            res = self.info_guard.getSummary()
        return res

    _properties_form = DTMLFile('variable_properties', _dtmldir)

    def manage_properties(self, REQUEST, manage_tabs_message=None):
        '''
        '''
        return self._properties_form(REQUEST,
                                     management_view='Properties',
                                     manage_tabs_message=manage_tabs_message,
                                     )

    def setProperties(self, description,
                      default_value='', default_expr='',
                      for_catalog=0, for_status=0,
                      update_always=0,
                      props=None, REQUEST=None):
        '''
        '''
        self.description = str(description)
        self.default_value = str(default_value)
        if default_expr:
            self.default_expr = Expression(default_expr)
        else:
            self.default_expr = None
            
        g = Guard()
        if g.changeFromProperties(props or REQUEST):
            self.info_guard = g
        else:
            self.info_guard = None
        self.for_catalog = not not for_catalog  # Pure boolean value
        self.for_status = not not for_status
        self.update_always = not not update_always
        if REQUEST is not None:
            return self.manage_properties(REQUEST, 'Properties changed.')

Globals.InitializeClass(VariableDefinition)


class Variables (ContainerTab):

    meta_type = 'Workflow Variables'

    all_meta_types = ({'name':VariableDefinition.meta_type,
                       'action':'addVariable',
                       },)

    _manage_variables = DTMLFile('variables', _dtmldir)

    def manage_main(self, REQUEST, manage_tabs_message=None):
        '''
        '''
        return self._manage_variables(
            REQUEST,
            management_view='Variables',
            manage_tabs_message=manage_tabs_message,
            )

    def addVariable(self, id, REQUEST=None):
        '''
        '''
        vdef = VariableDefinition(id)
        self._setObject(id, vdef)
        if REQUEST is not None:
            return self.manage_main(REQUEST, 'Variable added.')

    def deleteVariables(self, ids, REQUEST=None):
        '''
        '''
        for id in ids:
            self._delObject(id)
        if REQUEST is not None:
            return self.manage_main(REQUEST, 'Variable(s) removed.')

    def _checkId(self, id, allow_dup=0):
        wf_def = aq_parent(aq_inner(self))
        if id == wf_def.state_var:
            raise 'Bad Request', '"%s" is used for keeping state.' % id
        return ContainerTab._checkId(self, id, allow_dup)

    def getStateVar(self):
        wf_def = aq_parent(aq_inner(self))
        return wf_def.state_var

    def setStateVar(self, id, REQUEST=None):
        '''
        '''
        wf_def = aq_parent(aq_inner(self))
        if id != wf_def.state_var:
            self._checkId(id)
            wf_def.state_var = str(id)
        if REQUEST is not None:
            return self.manage_main(REQUEST, 'Set state variable.')

Globals.InitializeClass(Variables)
