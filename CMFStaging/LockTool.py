##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Lock Tool

Provides access to per-object locking.  This implementation uses
WebDAV locks.

$Id$
"""

import os

from Acquisition import aq_parent
from Globals import InitializeClass
from Globals import DTMLFile
from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from webdav.WriteLockInterface import WriteLockInterface
from webdav.LockItem import LockItem
from zExceptions import Unauthorized

from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import SimpleItemWithProperties
from Products.CMFCore.utils import _checkPermission

from permissions import ManagePortal
from permissions import ModifyPortalContent
from permissions import LockObjects
from permissions import UnlockObjects
from staging_utils import verifyPermission

_wwwdir = os.path.join(os.path.dirname(__file__), 'www') 


def pathOf(obj):
    return '/'.join(obj.getPhysicalPath())


class LockingError(Exception):
    pass


class LockTool(UniqueObject, SimpleItemWithProperties):
    __doc__ = __doc__ # copy from module
    id = 'portal_lock'
    meta_type = 'Portal Lock Tool'

    security = ClassSecurityInfo()

    manage_options = ( { 'label' : 'Overview', 'action' : 'manage_overview' }
                     , 
                     ) + SimpleItemWithProperties.manage_options

    # With auto_version on, locking automatically causes a version checkout
    # and unlocking automatically causes a checkin.  This is one form
    # of autoversioning described in the DeltaV introduction.
    # http://www.webdav.org/deltav/WWW10/deltav-intro.htm
    auto_version = 1
    timeout_days = 14  # 2 weeks

    _properties = (
        {'id': 'auto_version', 'type': 'boolean', 'mode': 'w',
         'label': 'Auto checkout and checkin using portal_versions'},
        {'id': 'timeout_days', 'type': 'int', 'mode': 'w',
         'label': 'Lock timeout in days'},
        )

    #
    #   ZMI methods
    #
    security.declareProtected(ManagePortal, 'manage_overview' )
    manage_overview = DTMLFile('explainLockTool', _wwwdir)

    #
    #   'LockTool' interface methods
    #

    security.declarePublic('lock')
    def lock(self, obj):
        """Locks an object.
        """
        verifyPermission(LockObjects, obj)
        locker = self.locker(obj)
        if locker:
            raise LockingError, '%s is already locked' % pathOf(obj)

        if self.auto_version:
            vt = getToolByName(self, 'portal_versions', None)
            if vt is not None:
                if (vt.isUnderVersionControl(obj)
                    and not vt.isCheckedOut(obj)):
                    vt.checkout(obj)

        user = getSecurityManager().getUser()
        lockitem = LockItem(user, timeout=(self.timeout_days * 86400))
        obj.wl_setLock(lockitem.getLockToken(), lockitem)


    security.declarePublic('breaklock')
    def breaklock(self, obj, message=''):
        """Breaks the lock in an emergency.
        """
        locker = self.locker(obj)
        verifyPermission(UnlockObjects, obj)
        obj.wl_clearLocks()
        if self.auto_version:
            vt = getToolByName(self, 'portal_versions', None)
            if vt is not None:
                if (vt.isUnderVersionControl(obj)
                    and vt.isCheckedOut(obj)):
                    vt.checkin(obj, message)


    security.declarePublic('unlock')
    def unlock(self, obj, message=''):
        """Unlocks an object.
        """
        verifyPermission(UnlockObjects, obj)
        locker = self.locker(obj)
        if not locker:
            raise LockingError, ("Unlocking an unlocked item: %s" %
                                 pathOf(obj))

        user = getSecurityManager().getUser()
        if user.getId() != locker:
            raise LockingError, ("Cannot unlock %s: lock is held by %s" %
                                 (pathOf(obj), locker))

        # According to WriteLockInterface, we shouldn't call
        # wl_clearLocks(), but it seems like the right thing to do anyway.
        obj.wl_clearLocks()

        if self.auto_version:
            vt = getToolByName(self, 'portal_versions', None)
            if vt is not None:
                if (vt.isUnderVersionControl(obj)
                    and vt.isCheckedOut(obj)):
                    vt.checkin(obj, message)


    security.declarePublic('locker')
    def locker(self, obj):
        """Returns the locker of an object.
        """
        if not WriteLockInterface.isImplementedBy(obj):
            raise LockingError, "%s is not lockable" % pathOf(obj)

        values = obj.wl_lockValues()
        if not values:
            return ''
        for lock in values:
            if lock.isValid():
                creator = lock.getCreator()
                if creator:
                    return creator[1]  # The user id without the path
        # All of the locks are expired or invalid
        return ''


    security.declarePublic('isLockedOut')
    def isLockedOut(self, obj):
        """Returns a true value if the current user is locked out.
        """
        locker_id = self.locker(obj)
        if locker_id:
            uid = getSecurityManager().getUser().getId()
            if uid != locker_id:
                return 1
        return 0


    security.declarePublic('locked')
    def locked(self, obj):
        """Returns true if an object is locked.

        Also accepts non-lockable objects, always returning 0.
        """
        if not WriteLockInterface.isImplementedBy(obj):
            return 0
        return not not self.locker(obj)


    security.declarePublic('isLockable')
    def isLockable(self, obj):
        """Return true if object supports locking.

        Does not examine lock state or whether the current user can
        actually lock.
        """
        return WriteLockInterface.isImplementedBy(obj)


    security.declarePublic('canLock')
    def canLock(self, obj):
        """Returns true if the current user can lock the given object.
        """
        if self.locked(obj):
            return 0
        if not WriteLockInterface.isImplementedBy(obj):
            return 0
        if _checkPermission(LockObjects, obj):
            return 1
        return 0


    security.declarePublic('canUnlock')
    def canUnlock(self, obj):
        """Returns true if the current user can unlock the given object."""
        if not self.locked(obj):
            return 0
        if self.isLockedOut(obj):
            return 0
        if _checkPermission(UnlockObjects, obj):
            return 1
        return 0


    security.declarePublic('canChange')
    def canChange(self, obj):
        """Returns true if the current user can change the given object.
        """
        if not WriteLockInterface.isImplementedBy(obj):
            if self.isLockedOut(obj):
                return 0
        if not _checkPermission(ModifyPortalContent, obj):
            return 0
        vt = getToolByName(self, 'portal_versions', None)
        if vt is not None:
            if (vt.isUnderVersionControl(obj)
                and not vt.isCheckedOut(obj)):
                return 0
        return 1


    security.declarePublic('hasLock')
    def hasLock(self, obj):
        """Returns true if the user has a lock on the specified object.
        """
        locker = self.locker(obj)
        if not locker:
            return 0
        user = getSecurityManager().getUser()
        return (user.getId() == locker)

InitializeClass(LockTool)
