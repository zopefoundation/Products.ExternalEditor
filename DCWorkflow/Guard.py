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
Guard conditions in a web-configurable workflow.
$Id$
'''
__version__='$Revision$'[11:-2]

from string import split, strip, join
from cgi import escape

import Globals
from Globals import DTMLFile, Persistent
from AccessControl import ClassSecurityInfo

from Products.CMFCore.CMFCorePermissions import ManagePortal

from Expression import Expression, StateChangeInfo, createExprContext
from utils import _dtmldir


class Guard (Persistent):
    permissions = ()
    roles = ()
    expr = None

    security = ClassSecurityInfo()
    security.declareObjectProtected(ManagePortal)

    guardForm = DTMLFile('guard', _dtmldir)

    def check(self, sm, wf_def, ob):
        '''
        Checks conditions in this guard.
        '''
        pp = self.permissions
        if pp:
            found = 0
            for p in pp:
                if sm.checkPermission(p, ob):
                    found = 1
                    break
            if not found:
                return 0
        roles = self.roles
        if roles:
            # Require at least one of the given roles.
            found = 0
            u_roles = sm.getUser().getRolesInContext(ob)
            for role in roles:
                if role in u_roles:
                    found = 1
                    break
            if not found:
                return 0
        expr = self.expr
        if expr is not None:
            econtext = createExprContext(StateChangeInfo(ob, wf_def))
            res = expr(econtext)
            if not res:
                return 0
        return 1

    def getSummary(self):
        # Perhaps ought to be in DTML.
        res = []
        if self.permissions:
            res.append('Requires permission:')
            for idx in range(len(self.permissions)):
                p = self.permissions[idx]
                if idx > 0:
                    if idx < len(self.permissions) - 1:
                        res.append(';')
                    else:
                        res.append('or')
                res.append('<code>' + escape(p) + '</code>')
        if self.roles:
            if res:
                res.append(', role:')
            else:
                res.append('Requires role:')
            for idx in range(len(self.roles)):
                r = self.roles[idx]
                if idx > 0:
                    if idx < len(self.roles) - 1:
                        res.append(';')
                    else:
                        res.append('or')
                res.append('<code>' + escape(r) + '</code>')
        if self.expr is not None:
            if res:
                res.append(', expr:')
            else:
                res.append('Requires expr:')
            res.append('<code>' + escape(self.expr.text) + '</code>')
        return join(res, ' ')

    def changeFromProperties(self, props):
        '''
        Returns 1 if changes were specified.
        '''
        if props is None:
            return 0
        res = 0
        s = props.get('guard_permissions', None)
        if s:
            res = 1
            p = map(strip, split(s, ';'))
            self.permissions = tuple(p)
        s = props.get('guard_roles', None)
        if s:
            res = 1
            r = map(strip, split(s, ';'))
            self.roles = tuple(r)
        s = props.get('guard_expr', None)
        if s:
            res = 1
            self.expr = Expression(s)
        return res

    def getPermissionsText(self):
        if not self.permissions:
            return ''
        return join(self.permissions, '; ')

    def getRolesText(self):
        if not self.roles:
            return ''
        return join(self.roles, '; ')

    def getExprText(self):
        if not self.expr:
            return ''
        return str(self.expr.text)

Globals.InitializeClass(Guard)
