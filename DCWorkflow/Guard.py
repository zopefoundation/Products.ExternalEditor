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
                res.append('<br/>')
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
                res.append('<br/>')
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
