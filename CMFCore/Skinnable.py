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
""" Base class for object managers which can be "skinned".

Skinnable object managers inherit attributes from a skin specified in
the browser request.  Skins are stored in a fixed-name subobject.

$Id$
"""

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Acquisition import ImplicitAcquisitionWrapper
from Globals import InitializeClass
from OFS.ObjectManager import ObjectManager


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
        up to the root skins folder.

        This should be fast, flexible, and predictable.
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

    security.declarePrivate('getSkin')
    def getSkin(self, name=None):
        """Returns the requested skin.
        """
        skinob = None
        skinstool = None
        sfn = self.getSkinsFolderName()

        if sfn is not None:
            sf = getattr(self, sfn, None)
            if sf is not None:
               if name is not None:
                   skinob = sf.getSkinByName(name)
               if skinob is None:
                   skinob = sf.getSkinByName(sf.getDefaultSkin())
                   if skinob is None:
                       skinob = sf.getSkinByPath('')
        return skinob

    security.declarePublic('getSkinNameFromRequest')
    def getSkinNameFromRequest(self, REQUEST=None):
        '''Returns the skin name from the Request.'''
        sfn = self.getSkinsFolderName()
        if sfn is not None:
            sf = getattr(self, sfn, None)
            if sf is not None:
                return REQUEST.get(sf.getRequestVarname(), None)

    security.declarePublic('changeSkin')
    def changeSkin(self, skinname):
        '''Change the current skin.

        Can be called manually, allowing the user to change
        skins in the middle of a request.
        '''
        self._v_skindata = None
        skinobj = self.getSkin(skinname)
        if skinobj is not None:
            self._v_skindata = (self.REQUEST, skinobj, {})

    security.declarePublic('setupCurrentSkin')
    def setupCurrentSkin(self, REQUEST=None):
        '''
        Sets up _v_skindata so that __getattr__ can find it.

        Can NOT be called manually to change skins in the middle of a
        request! Use changeSkin for that.
        '''
        if REQUEST is None:
            REQUEST = getattr(self, 'REQUEST', None)
        if REQUEST is None:
            # self is not fully wrapped at the moment.  Don't
            # change anything.
            return
        if self._v_skindata is not None and self._v_skindata[0] is REQUEST:
            # Already set up for this request.
            return
        skinname = self.getSkinNameFromRequest(REQUEST)
        self.changeSkin(skinname)

    def __of__(self, parent):
        '''
        Sneakily sets up the portal skin then returns the wrapper
        that Acquisition.Implicit.__of__() would return.
        '''
        w_self = ImplicitAcquisitionWrapper(self, parent)
        try:
            w_self.setupCurrentSkin()
        except:
            # This shouldn't happen, even if the requested skin
            # does not exist.
            import sys
            from zLOG import LOG, ERROR
            LOG('CMFCore', ERROR, 'Unable to setupCurrentSkin()',
                error=sys.exc_info())
        return w_self

    def _checkId(self, id, allow_dup=0):
        '''
        Override of ObjectManager._checkId().

        Allows the user to create objects with IDs that match the ID of
        a skin object.
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

InitializeClass(SkinnableObjectManager)
