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

from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo, getSecurityManager
from Products.CMFCore.utils import UniqueObject, getToolByName, \
     SimpleItemWithProperties
from Products.CMFCore.CMFCorePermissions import ManagePortal

from webdav.WriteLockInterface import WriteLockInterface
from webdav.LockItem import LockItem

# Permission names
LockObjects = 'WebDAV Lock items'
UnlockObjects = 'WebDAV Unlock items'

_wwwdir = os.path.join(os.path.dirname(__file__), 'www') 


def pathOf(object):
    return '/'.join(object.getPhysicalPath())


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

    _properties = (
        {'id': 'auto_version', 'type': 'boolean', 'mode': 'w',
         'label': 'Auto checkout and checkin using portal_versions'},
        )

    #
    #   ZMI methods
    #
    security.declareProtected(ManagePortal, 'manage_overview' )
    manage_overview = DTMLFile('explainLockTool', _wwwdir)

    #
    #   'LockTool' interface methods
    #

    security.declareProtected(LockObjects, 'lock')
    def lock(self, object):
        '''Locks an object'''
        locker = self.locker(object)
        if locker:
            raise LockingError, '%s is already locked' % pathOf(object)

        if self.auto_version:
            vt = getToolByName(self, 'portal_versions', None)
            if vt is not None:
                if not vt.isCheckedOut(object):
                    object = vt.checkout(object)

        user = getSecurityManager().getUser()
        lockitem = LockItem(user)
        object.wl_setLock(lockitem.getLockToken(), lockitem)


    security.declareProtected(UnlockObjects, 'unlock')
    def unlock(self, object):
        '''Unlocks an object'''
        locker = self.locker(object)
        if not locker:
            raise LockingError, ("Unlocking an unlocked item: %s" %
                                 pathOf(object))

        user = getSecurityManager().getUser()
        if user.getId() != locker:
            raise LockingError, ("Cannot unlock %s: lock is held by %s" %
                                 (pathOf(object), locker))

        # According to WriteLockInterface, we shouldn't call
        # wl_clearLocks(), but it seems like the right thing to do anyway.
        object.wl_clearLocks()

        if self.auto_version:
            vt = getToolByName(self, 'portal_versions', None)
            if vt is not None:
                vt.checkin(object)


    security.declarePublic('locker')
    def locker(self, object):
        '''Returns the locker of an object'''
        if not WriteLockInterface.isImplementedBy(object):
            raise LockingError, "%s is not lockable" % pathOf(object)

        values = object.wl_lockValues()
        if not values:
            return ''

        creator = values[0].getCreator()
        if creator:
            return creator[1]  # The user id without the path
        return ''  # An expired lock?


    security.declarePublic('isLockedOut')
    def isLockedOut(self, object):
        '''Returns a true value if the current user is locked out.'''
        locker_id = self.locker(object)
        if locker_id:
            uid = getSecurityManager().getUser().getId()
            if uid != locker_id:
                return 1
        return 0


    security.declarePublic('locked')
    def locked(self, object):
        '''Returns true if an object is locked.

        Also accepts non-lockable objects, always returning 0.'''
        if not WriteLockInterface.isImplementedBy(object):
            return 0
        return not not self.locker(object)
        

InitializeClass(LockTool)

