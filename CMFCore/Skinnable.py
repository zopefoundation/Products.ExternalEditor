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
Skinnable object managers inherit attributes from a skin specified in
the browser request.  Skins are stored in a fixed-name subobject.
$Id$
'''

import Globals
from OFS.ObjectManager import ObjectManager
from Acquisition import ImplicitAcquisitionWrapper, aq_base, aq_inner
from ExtensionClass import Base
from AccessControl import ClassSecurityInfo


# superGetAttr is assigned to whatever ObjectManager.__getattr__
# used to do.
try:
    superGetAttr = ObjectManager.__getattr__
except:
    try:
        superGetAttr = ObjectManager.inheritedAttribute('__getattr__')
    except:
        def superGetAttr(self, name):
            raise AttributeError, name

_marker = []  # Create a new marker object.


class SkinnableObjectManager (ObjectManager):

    _v_skindata = None

    security = ClassSecurityInfo()

    security.declarePrivate('getSkinsFolderName')
    def getSkinsFolderName(self):
        # Not implemented.
        return None

    def __getattr__(self, name, _marker=_marker):
        '''
        Looks for the name in an object with wrappers that only reach
        up to the root skins folder.  This should be fast, flexible,
        and predictable.
        '''
        if name[:1] != '_' and name[:3] != 'aq_':
            sd = self._v_skindata
            if sd is not None:
                ob, ignore = sd
                if not ignore.has_key(name):
                    subob = getattr(ob, name, _marker)
                    if subob is not _marker:
                        # Return it in context of self, forgetting
                        # its location and acting as if it were located
                        # in self.
                        return aq_base(subob)
                    else:
                        ignore[name] = 1
        return superGetAttr(self, name)

    security.declarePublic('setupCurrentSkin')
    def setupCurrentSkin(self, REQUEST=None):
        '''
        Sets up _v_skindata so that __getattr__ can find it.
        Can also be called manually, allowing the user to change
        skins in the middle of a request.
        '''
        if REQUEST is None:
            REQUEST = getattr(self, 'REQUEST', None)
        if REQUEST is None:
            # We are traversing without a REQUEST at the root.
            # Don't change the skin right now. (Otherwise
            # [un]restrictedTraverse messes up the skin data.)
            return
        self._v_skindata = None
        sfn = self.getSkinsFolderName()
        if sfn is not None:
            # Note that our custom __getattr__ won't get confused
            # by skins at the moment because _v_skindata is None.
            sf = getattr(self, sfn, None)
            if sf is not None:
                sd = sf.getSkin(REQUEST)
                if sd is not None:
                    # Hide from acquisition.
                    self._v_skindata = (sd, {})

    def __of__(self, parent):
        '''
        Sneakily sets up the portal skin then returns the wrapper
        that Acquisition.Implicit.__of__() would return.
        '''
        w_self = ImplicitAcquisitionWrapper(self, parent)
        w_self.setupCurrentSkin()
        return w_self

    def _checkId(self, id, allow_dup=0):
        '''
        Override of ObjectManager._checkId().  Allows the user
        to create objects with IDs that match the ID of a skin
        object.
        '''
        superCheckId = SkinnableObjectManager.inheritedAttribute('_checkId')
        if not allow_dup:
            # Temporarily disable _v_skindata.
            # Note that this depends heavily on Zope's current thread
            # behavior.
            sd = self._v_skindata
            self._v_skindata = None
            try:
                base = getattr(self,  'aq_base', self)
                if not hasattr(base, id):
                    # Cause _checkId to not check for duplication.
                    return superCheckId(self, id, allow_dup=1)
            finally:
                self._v_skindata = sd
        return superCheckId(self, id, allow_dup)

Globals.InitializeClass(SkinnableObjectManager)
