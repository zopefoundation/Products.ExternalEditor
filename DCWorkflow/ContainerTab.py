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
A convenient base class for representing a container as a management tab.
$Id$
'''
__version__='$Revision$'[11:-2]


from OFS.Folder import Folder
from OFS.SimpleItem import Item_w__name__
from Acquisition import aq_base, aq_inner, aq_parent

_marker = []  # Create a new marker object.

class ContainerTab (Folder):

    def __init__(self, id):
        self.id = id
        self._mapping = {}

    def getId(self):
        return self.id

    def manage_options(self):
        parent = aq_parent(aq_inner(self))
        res = []
        options = parent.manage_options
        if callable(options):
            options = options()
        for item in options:
            item = item.copy()
            item['action'] = '../' + item['action']
            res.append(item)
        return res

    def manage_workspace(self, RESPONSE):
        '''
        Redirects to the primary option.
        '''
        RESPONSE.redirect(self.absolute_url() + '/manage_main')

    def _checkId(self, id, allow_dup=0):
        if not allow_dup:
            if self._mapping.has_key(id):
                raise 'Bad Request', 'The id "%s" is already in use.' % id
        return Folder._checkId(self, id, allow_dup)

    def _getOb(self, name, default=_marker):
        mapping = self._mapping
        if mapping.has_key(name):
            res = mapping[name]
            if hasattr(res, '__of__'):
                res = res.__of__(self)
            return res
        else:
            if default is _marker:
                raise KeyError, name
            return default

    def __getattr__(self, name):
        ob = self._mapping.get(name, None)
        if ob is not None:
            return ob
        raise AttributeError, name

    def _setOb(self, name, value):
        mapping = self._mapping
        mapping[name] = aq_base(value)
        self._mapping = mapping  # Trigger persistence.

    def _delOb(self, name):
        mapping = self._mapping
        del mapping[name]
        self._mapping = mapping  # Trigger persistence.

    def get(self, name, default=None):
        if self._mapping.has_key(name):
            return self[name]
        else:
            return default

    def objectIds(self, spec=None):
        # spec is not important for now...
        return self._mapping.keys()

    def keys(self):
        return self._mapping.keys()

    def items(self):
        return map(lambda id, self=self: (id, self._getOb(id)),
                   self._mapping.keys())

    def values(self):
        return map(lambda id, self=self: self._getOb(id),
                   self._mapping.keys())

    def manage_renameObjects(self, ids=[], new_ids=[], REQUEST=None):
        """Rename several sub-objects"""
        if len(ids) != len(new_ids):
            raise 'Bad Request', 'Please rename each listed object.'
        for i in range(len(ids)):
            if ids[i] != new_ids[i]:
                self.manage_renameObject(ids[i], new_ids[i])
        if REQUEST is not None:
            return self.manage_main(REQUEST)
        return None

