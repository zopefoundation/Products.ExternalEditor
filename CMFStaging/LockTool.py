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

from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo, getSecurityManager
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore import CMFCorePermissions

from webdav.WriteLockInterface import WriteLockInterface
from webdav.LockItem import LockItem

# Permission names
LockObjects = 'WebDAV Lock items'
UnlockObjects = 'WebDAV Unlock items'


def pathOf(object):
    return '/'.join(object.getPhysicalPath())


class LockingError(Exception):
    pass


class LockTool(UniqueObject, SimpleItem):
    __doc__ = __doc__ # copy from module
    id = 'portal_lock'
    meta_type = 'Portal Lock Tool'

    security = ClassSecurityInfo()

    manage_options = ( { 'label' : 'Overview', 'action' : 'manage_overview' }
                     , 
                     ) + SimpleItem.manage_options

    #
    #   ZMI methods
    #
    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'manage_overview' )
    #manage_overview = DTMLFile( 'explainDiscussionTool', _dtmldir )

    #
    #   'LockTool' interface methods
    #

    security.declareProtected(LockObjects, 'lock')
    def lock(self, object):
        '''Locks an object'''
        user = getSecurityManager().getUser()
        locker = self.locker(object)

        if locker:
            raise LockingError, '%s is already locked' % pathOf(object)

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

