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
from DocumentTemplate.DT_Util import TemplateDict, InstanceDict, Eval

from Products.CMFCore.WorkflowCore import ObjectDeleted, ObjectMoved

try:
    # Zope 2.3.x
    from DocumentTemplate.DT_Util import expr_globals
except ImportError:
    expr_globals = None

try:
    # Zope 2.4.x
    from AccessControl.DTML import RestrictedDTML
except ImportError:
    class RestrictedDTML: pass


class Expression (Persistent, RestrictedDTML):
    text = ''
    _v_eval = None

    security = ClassSecurityInfo()

    def __init__(self, text):
        self.text = text
        if expr_globals is not None:
            eval = Eval(text, expr_globals)
        else:
            eval = Eval(text)
        self._v_eval = eval

    security.declarePrivate('validate')
    def validate(self, inst, parent, name, value, md):
        # Zope 2.3.x
        return getSecurityManager().validate(inst, parent, name, value)

    def __call__(self, md):
        # md is a TemplateDict instance.
        eval = self._v_eval
        if eval is None:
            text = self.text
            if expr_globals is not None:
                eval = Eval(text, expr_globals)
            else:
                eval = Eval(text)
            self._v_eval = eval
        md.validate = self.validate  # Zope 2.3.x
        # Zope 2.4.x
        md.guarded_getattr = getattr(self, 'guarded_getattr', None)
        md.guarded_getitem = getattr(self, 'guarded_getitem', None)
        return eval.eval(md)

Globals.InitializeClass(Expression)


def exprNamespace(object, workflow, status=None,
                  transition=None, new_state=None, kwargs=None):
    md = TemplateDict()
    if kwargs is None:
        kwargs = {}
    if status is None:
        tool = aq_parent(aq_inner(workflow))
        status = tool.getStatusOf(workflow.id, object)
        if status is None:
            status = {}
    md._push(status)
    md._push(ExprVars(object, workflow))
    d = {'object': object,
         'workflow': workflow,
         'transition': transition,
         'new_state': new_state,
         'kwargs': kwargs,
         }
    md._push(d)
    md._push(workflow.scripts)  # Make scripts automatically available.
    return md


class ExprVars:
    '''
    Provides names that are more expensive to compute.
    '''
    ObjectDeleted = ObjectDeleted
    ObjectMoved = ObjectMoved

    def __init__(self, ob, wf):
        self._ob = ob
        self._wf = wf

    def __getitem__(self, name):
        if name[:1] != '_' and hasattr(self, name):
            return getattr(self, name)
        raise KeyError, name

    def getHistory(self):
        wf = self._wf
        tool = aq_parent(aq_inner(wf))
        wf_id = wf.id
        h = tool.getHistoryOf(wf_id, self._ob)
        if h:
            return map(lambda dict: dict.copy(), h)  # Don't allow mutation
        else:
            return ()

    def getPortal(self):
        ob = self._ob
        while ob is not None and not getattr(ob, '_isPortalRoot', 0):
            ob = aq_parent(aq_inner(ob))
        return ob

    def getObjectContainer(self):
        return aq_parent(aq_inner(self._ob))
