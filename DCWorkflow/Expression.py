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
Expressions in a web-configurable workflow.
$Id$
'''
__version__='$Revision$'[11:-2]

import Globals
from Globals import Persistent
from Acquisition import aq_inner, aq_parent
from AccessControl import getSecurityManager, ClassSecurityInfo
from DateTime import DateTime

from Products.CMFCore.WorkflowCore import ObjectDeleted, ObjectMoved
from Products.PageTemplates.Expressions import getEngine
from Products.PageTemplates.TALES import SafeMapping
from Products.PageTemplates.PageTemplate import ModuleImporter


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


class StateChangeInfo:
    '''
    Provides information for expressions and scripts.
    '''
    _date = None

    ObjectDeleted = ObjectDeleted
    ObjectMoved = ObjectMoved

    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

    def __init__(self, object, workflow, status=None, transition=None,
                 old_state=None, new_state=None, kwargs=None):
        if kwargs is None:
            kwargs = {}
        else:
            # Don't allow mutation
            kwargs = SafeMapping(kwargs)
        if status is None:
            tool = aq_parent(aq_inner(workflow))
            status = tool.getStatusOf(workflow.id, object)
            if status is None:
                status = {}
        if status:
            # Don't allow mutation
            status = SafeMapping(status)
        self.object = object
        self.workflow = workflow
        self.old_state = old_state
        self.new_state = new_state
        self.transition = transition
        self.status = status
        self.kwargs = kwargs

    def __getitem__(self, name):
        if name[:1] != '_' and hasattr(self, name):
            return getattr(self, name)
        raise KeyError, name

    def getHistory(self):
        wf = self.workflow
        tool = aq_parent(aq_inner(wf))
        wf_id = wf.id
        h = tool.getHistoryOf(wf_id, self.object)
        if h:
            return map(lambda dict: dict.copy(), h)  # Don't allow mutation
        else:
            return ()

    def getPortal(self):
        ob = self.object
        while ob is not None and not getattr(ob, '_isPortalRoot', 0):
            ob = aq_parent(aq_inner(ob))
        return ob

    def getDateTime(self):
        date = self._date
        if not date:
            date = self._date = DateTime()
        return date

Globals.InitializeClass(StateChangeInfo)


def createExprContext(sci):
    '''
    An expression context provides names for TALES expressions.
    '''
    ob = sci.object
    wf = sci.workflow
    data = {
        'here':         ob,
        'container':    aq_parent(aq_inner(ob)),
        'nothing':      None,
        'root':         wf.getPhysicalRoot(),
        'request':      getattr( ob, 'REQUEST', None ),
        'modules':      ModuleImporter,
        'user':         getSecurityManager().getUser(),
        'state_change': sci,
        'transition':   sci.transition,
        'status':       sci.status,
        'kwargs':       sci.kwargs,
        'workflow':     wf,
        'scripts':      wf.scripts,
        }
    return getEngine().getContext(data)

