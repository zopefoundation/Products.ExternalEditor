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
"""Versions Tool

Provides a way to interact with a version repository.

$Id$
"""

import os

from Acquisition import aq_acquire
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import UniqueObject, SimpleItemWithProperties
from Products.CMFCore.CMFCorePermissions import ManagePortal

from staging_utils import getPortal, verifyPermission, unproxied


# Permission name
UseVersionControl = 'Use version control'

_wwwdir = os.path.join(os.path.dirname(__file__), 'www') 


class VersionsTool(UniqueObject, SimpleItemWithProperties):
    __doc__ = __doc__ # copy from module
    id = 'portal_versions'
    meta_type = 'Portal Versions Tool'

    security = ClassSecurityInfo()

    manage_options = ({'label' : 'Overview', 'action' : 'manage_overview'}, 
                      ) + SimpleItemWithProperties.manage_options


    # With auto_copy_forward turned on, the versions tool lets users
    # check out an object even if it is not updated to the latest
    # revision.  It copies the old revision forward.  Note that
    # this feature really shouldn't be enabled unless users also have the
    # ability to revert to specific revisions.
    auto_copy_forward = 1

    repository_name = 'VersionRepository'

    _properties = (
        {'id': 'repository_name', 'type': 'string', 'mode': 'w',
         'label': 'ID of the version repository'},
        {'id': 'auto_copy_forward', 'type': 'boolean', 'mode': 'w',
         'label': 'Copy old revisions forward rather than disallow checkout'},
        )

    security.declareProtected(ManagePortal, 'manage_overview' )
    manage_overview = DTMLFile( 'explainVersionsTool', _wwwdir )

    # helper methods

    def _getVersionRepository(self):
        repo = aq_acquire(self, self.repository_name, containment=1)
        return repo

    def _getBranchName(self, info):
        parts = info.version_id.split('.')
        if len(parts) > 1:
            return parts[-2]
        return 'mainline'

    # public methods

    security.declarePublic('isUnderVersionControl')
    def isUnderVersionControl(self, obj):
        """Returns a true value if the object is under version control.
        """
        obj = unproxied(obj)
        repo = self._getVersionRepository()
        return repo.isUnderVersionControl(obj)

    security.declarePublic('isCheckedOut')
    def isCheckedOut(self, obj):
        """Returns a true value if the object is checked out.
        """
        obj = unproxied(obj)
        repo = self._getVersionRepository()
        if not repo.isUnderVersionControl(obj):
            return 0
        info = repo.getVersionInfo(obj)
        return (info.status == info.CHECKED_OUT)

    security.declarePublic('isResourceUpToDate')
    def isResourceUpToDate(self, obj, require_branch=0):
        """Return true if a version-controlled resource is up to date.
        """
        obj = unproxied(obj)
        repo = self._getVersionRepository()
        return repo.isResourceUpToDate(obj, require_branch)

    # protected methods

    security.declarePublic('checkout')
    def checkout(self, obj):
        """Opens the object for development.
        
        Returns the object, which might be different from what was passed to
        the method if the object was replaced.
        """
        verifyPermission(UseVersionControl, obj)
        obj = unproxied(obj)
        repo = self._getVersionRepository()
        old_state = None
        if not repo.isUnderVersionControl(obj):
            repo.applyVersionControl(obj)
        elif self.auto_copy_forward:
            if not repo.isResourceUpToDate(obj, require_branch=1):
                # The object is not at the latest revision or has a
                # sticky tag.  Get it unstuck by copying the old state
                # forward after the object has been checked out.
                info = repo.getVersionInfo(obj)
                old_state = repo.getVersionOfResource(
                    info.history_id, info.version_id)
                # Momentarily revert to the branch.
                obj = repo.updateResource(obj, self._getBranchName(info))
                obj = repo.checkoutResource(obj)

                # Copy the old state into the object, minus __vc_info__.
                # XXX There ought to be some way to do this more cleanly.
                obj._p_changed = 1
                for key in obj.__dict__.keys():
                    if key != '__vc_info__':
                        if not old_state.__dict__.has_key(key):
                            del obj.__dict__[key]
                for key, value in old_state.__dict__.items():
                    if key != '__vc_info__':
                        obj.__dict__[key] = value
                # Check in as a copy.
                obj = repo.checkinResource(
                    obj, 'Copied from revision %s' % info.version_id)
        repo.checkoutResource(obj)
        return None


    security.declarePublic('checkin')
    def checkin(self, obj, message=None):
        """Checks in a new version.
        """
        verifyPermission(UseVersionControl, obj)
        obj = unproxied(obj)
        repo = self._getVersionRepository()
        if not repo.isUnderVersionControl(obj):
            repo.applyVersionControl(obj, message)
        else:
            if (not repo.isResourceUpToDate(obj, require_branch=1)
                and self.isCheckedOut(obj)):
                # This is a strange state, but it can be fixed.
                # Revert the object to the branch, replace the
                # reverted state with the new state, and check in.
                new_dict = obj.__dict__.copy()
                # Uncheckout
                obj = repo.uncheckoutResource(obj)
                info = repo.getVersionInfo(obj)
                obj = repo.updateResource(obj, self._getBranchName(info))
                # Checkout
                obj = repo.checkoutResource(obj)
                # Restore the new state
                for key in obj.__dict__.keys():
                    if key != '__vc_info__':
                        if not new_dict.has_key(key):
                            del obj.__dict__[key]
                for key, value in new_dict.items():
                    if key != '__vc_info__':
                        obj.__dict__[key] = value
            repo.checkinResource(obj, message or '')
        return None


    security.declarePublic('getLogEntries')
    def getLogEntries(self, obj, only_checkins=0):
        """Returns the log entries for an object as a sequence of mappings.
        """
        verifyPermission(UseVersionControl, obj)
        obj = unproxied(obj)
        repo = self._getVersionRepository()
        if not repo.isUnderVersionControl(obj):
            return []
        entries = repo.getLogEntries(obj)
        res = []
        for entry in entries:
            a = entry.action
            if a == entry.ACTION_CHECKOUT:
                action = 'checkout'
            elif a == entry.ACTION_CHECKIN:
                action = 'checkin'
            elif a == entry.ACTION_UNCHECKOUT:
                action = 'uncheckout'
            elif a == entry.ACTION_UPDATE:
                action = 'update'
            else:
                action = '?'
            if only_checkins and action != 'checkin':
                continue
            res.append({'timestamp': entry.timestamp,
                        'version_id': entry.version_id,
                        'action': action,
                        'message': entry.message,
                        'user_id': entry.user_id,
                        'path': entry.path,
                        })
        return res


    security.declarePublic('getVersionId')
    def getVersionId(self, obj, plus=0):
        """Returns the version ID of the current revision.

        If the 'plus' flag is set and the object is checked out, the
        version ID will include a plus sign to indicate that when the
        object is checked in, it will have a higher version number.
        """
        obj = unproxied(obj)
        repo = self._getVersionRepository()
        if repo.isUnderVersionControl(obj):
            info = repo.getVersionInfo(obj)
            res = info.version_id
            if plus and info.status == info.CHECKED_OUT:
                res += '+'
            return res
        else:
            return ''

    security.declarePublic('getVersionIds')
    def getVersionIds(self, obj):
        """Returns the version IDs of all revisions for an object.
        """
        verifyPermission(UseVersionControl, obj)
        obj = unproxied(obj)
        repo = self._getVersionRepository()
        ids = repo.getVersionIds(obj)
        ids = map(int, ids)
        ids.sort()
        return map(str, ids)

    security.declarePublic('getHistoryId')
    def getHistoryId(self, obj):
        """Returns the version history ID of the object.
        """
        verifyPermission(UseVersionControl, obj)
        obj = unproxied(obj)
        repo = self._getVersionRepository()
        return repo.getVersionInfo(obj).history_id


    security.declarePublic('revertToVersion')
    def revertToVersion(self, obj, version_id):
        """Reverts the object to the given version.

        If make_new_revision, a new revision is created, so that
        the object's state can progress along a new line without
        making the user deal with branches, labels, etc.
        """
        verifyPermission(UseVersionControl, obj)
        obj = unproxied(obj)
        repo = self._getVersionRepository()
        # Verify the object is under version control.
        repo.getVersionInfo(obj)
        if self.isCheckedOut(obj):
            # Save the current data.
            self.checkin(obj, 'Auto-saved')
        repo.updateResource(obj, version_id)

InitializeClass(VersionsTool)

