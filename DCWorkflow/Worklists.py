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
Worklists in a web-configurable workflow.
$Id$
'''
__version__='$Revision$'[11:-2]

from OFS.SimpleItem import SimpleItem
from Globals import DTMLFile, PersistentMapping
from Acquisition import aq_inner, aq_parent
import Globals
from AccessControl import ClassSecurityInfo

from Products.CMFCore.CMFCorePermissions import ManagePortal

from ContainerTab import ContainerTab
from Guard import Guard
from utils import _dtmldir


class WorklistDefinition (SimpleItem):
    meta_type = 'Worklist'

    security = ClassSecurityInfo()
    security.declareObjectProtected(ManagePortal)

    description = ''
    var_matches = None  # Compared with catalog when set.
    actbox_name = ''
    actbox_url = ''
    actbox_category = 'global'
    guard = None

    manage_options = (
        {'label': 'Properties', 'action': 'manage_properties'},
        )

    def __init__(self, id):
        self.id = id

    def getGuard(self):
        if self.guard is not None:
            return self.guard
        else:
            return Guard()  # Create a temporary guard.

    def getGuardSummary(self):
        res = None
        if self.guard is not None:
            res = self.guard.getSummary()
        return res

    def getWorkflow(self):
        return aq_parent(aq_inner(aq_parent(aq_inner(self))))

    def getAvailableCatalogVars(self):
        res = []
        res.append(self.getWorkflow().state_var)
        for id, vdef in self.getWorkflow().variables.items():
            if vdef.for_catalog:
                res.append(id)
        res.sort()
        return res

    def getVarMatch(self, id):
        if self.var_matches:
            return self.var_matches.get(id, '')
        else:
            return ''

    _properties_form = DTMLFile('worklist_properties', _dtmldir)

    def manage_properties(self, REQUEST, manage_tabs_message=None):
        '''
        '''
        return self._properties_form(REQUEST,
                                     management_view='Properties',
                                     manage_tabs_message=manage_tabs_message,
                                     )

    def setProperties(self, description,
                      actbox_name='', actbox_url='', actbox_category='global',
                      props=None, REQUEST=None):
        '''
        '''
        if props is None:
            props = REQUEST
        self.description = str(description)
        for key in self.getAvailableCatalogVars():
            # Populate var_matches.
            fieldname = 'var_match_%s' % key
            v = props.get(fieldname, '')
            if v:
                if not self.var_matches:
                    self.var_matches = PersistentMapping()
                self.var_matches[key] = str(v)
            else:
                if self.var_matches and self.var_matches.has_key(key):
                    del self.var_matches[key]
        self.actbox_name = str(actbox_name)
        self.actbox_url = str(actbox_url)
        self.actbox_category = str(actbox_category)
        g = Guard()
        if g.changeFromProperties(props or REQUEST):
            self.guard = g
        else:
            self.guard = None
        if REQUEST is not None:
            return self.manage_properties(REQUEST, 'Properties changed.')

Globals.InitializeClass(WorklistDefinition)


class Worklists (ContainerTab):

    meta_type = 'Worklists'

    security = ClassSecurityInfo()
    security.declareObjectProtected(ManagePortal)

    all_meta_types = ({'name':WorklistDefinition.meta_type,
                       'action':'addWorklist',
                       },)

    _manage_worklists = DTMLFile('worklists', _dtmldir)

    def manage_main(self, REQUEST, manage_tabs_message=None):
        '''
        '''
        return self._manage_worklists(
            REQUEST,
            management_view='Worklists',
            manage_tabs_message=manage_tabs_message,
            )

    def addWorklist(self, id, REQUEST=None):
        '''
        '''
        qdef = WorklistDefinition(id)
        self._setObject(id, qdef)
        if REQUEST is not None:
            return self.manage_main(REQUEST, 'Worklist added.')

    def deleteWorklists(self, ids, REQUEST=None):
        '''
        '''
        for id in ids:
            self._delObject(id)
        if REQUEST is not None:
            return self.manage_main(REQUEST, 'Worklist(s) removed.')

Globals.InitializeClass(Worklists)
