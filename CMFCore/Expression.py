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
Expressions in a web-configurable workflow.
$Id$
'''
__version__='$Revision$'[11:-2]

import Globals
from Globals import Persistent
from Acquisition import aq_inner, aq_parent
from AccessControl import getSecurityManager, ClassSecurityInfo

from utils import getToolByName
from Products.PageTemplates.Expressions import getEngine
from Products.PageTemplates.TALES import SafeMapping
from Products.PageTemplates.Expressions import SecureModuleImporter

class Expression (Persistent):
    text = ''
    _v_compiled = None

    security = ClassSecurityInfo()

    def __init__(self, text):
        self.text = text
        self._v_compiled = getEngine().compile(text)

    def __call__(self, econtext):
        compiled = self._v_compiled
        if compiled is None:
            compiled = self._v_compiled = getEngine().compile(self.text)
        # ?? Maybe expressions should manipulate the security
        # context stack.
        res = compiled(econtext)
        if isinstance(res, Exception):
            raise res
        #print 'returning %s from %s' % (`res`, self.text)
        return res

Globals.InitializeClass(Expression)


def createExprContext(folder, portal, object):
    '''
    An expression context provides names for TALES expressions.
    '''
    pm = getToolByName(portal, 'portal_membership')
    if object is None:
        object_url = ''
    else:
        object_url = object.absolute_url()
    if pm.isAnonymousUser():
        member = None
    else:
        member = pm.getAuthenticatedMember()
    data = {
        'object_url':   object_url,
        'folder_url':   folder.absolute_url(),
        'portal_url':   portal.absolute_url(),
        'object':       object,
        'folder':       folder,
        'portal':       portal,
        'nothing':      None,
        'request':      getattr( object, 'REQUEST', None ),
        'modules':      SecureModuleImporter,
        'member':       member,
        }
    return getEngine().getContext(data)

