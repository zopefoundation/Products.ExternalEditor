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
Skinnable object managers inherit attributes from a skin specified in
the browser request.  Skins are stored in a fixed-name subobject.
$Id$
'''

__version__='$Revision$'[11:-2]

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
        superGetAttr = None

_marker = []  # Create a new marker object.


class SkinnableObjectManager (ObjectManager):

    _v_skindata = None

    security = ClassSecurityInfo()

    security.declarePrivate('getSkinsFolderName')
    def getSkinsFolderName(self):
        # Not implemented.
        return None

    def __getattr__(self, name):
        '''
        Looks for the name in an object with wrappers that only reach
        up to the root skins folder.  This should be fast, flexible,
        and predictable.
        '''
        if not name.startswith('_') and not name.startswith('aq_'):
            sd = self._v_skindata
            if sd is not None:
                request, ob, ignore = sd
                if not ignore.has_key(name):
                    subob = getattr(ob, name, _marker)
                    if subob is not _marker:
                        # Return it in context of self, forgetting
                        # its location and acting as if it were located
                        # in self.
                        return aq_base(subob)
                    else:
                        ignore[name] = 1
        if superGetAttr is None:
            raise AttributeError, name
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
        if self._v_skindata is not None and self._v_skindata[0] is REQUEST:
            # Already set up for this request.
            return
        sfn = self.getSkinsFolderName()
        if sfn is not None:
            # Note that our custom __getattr__ won't get confused
            # by skins at the moment because _v_skindata is None.
            sf = getattr(self, sfn, None)
            if sf is not None:
                try:
                    sd = sf.getSkin(REQUEST)
                except:
                    import sys
                    from zLOG import LOG, ERROR
                    LOG('CMFCore', ERROR, 'Unable to get skin',
                        error=sys.exc_info())
                else:
                    if sd is not None:
                        # Hide from acquisition.
                        self._v_skindata = (REQUEST, sd, {})

    def __of__(self, parent):
        '''
        Sneakily sets up the portal skin then returns the wrapper
        that Acquisition.Implicit.__of__() would return.
        '''
        w_self = ImplicitAcquisitionWrapper(aq_base(self), parent)
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
