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

# Permission name
UseVersionControl = 'Use version control'

_wwwdir = os.path.join(os.path.dirname(__file__), 'www') 


class VersionsTool(UniqueObject, SimpleItemWithProperties):
    __doc__ = __doc__ # copy from module
    id = 'portal_versions'
    meta_type = 'Portal Versions tool'

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

    def _getVersionRepository(self):
        repo = aq_acquire(self, self.repository_name, containment=1)
        return repo


    security.declareProtected(UseVersionControl, 'checkout')
    def checkout(self, object):
        """Opens the object for development.
        
        Returns the object, which might be different from what was passed to
        the method if the object was replaced."""
        repo = self._getVersionRepository()
        old_state = None
        if not repo.isUnderVersionControl(object):
            get_transaction().commit(1)  # Get _p_jar attributes set.
            repo.applyVersionControl(object)
        elif self.auto_copy_forward and not repo.isResourceUpToDate(object):
            # Copy the old state forward after the object has been checked out.
            info = repo.getVersionInfo(object)
            old_state = repo.getVersionOfResource(
                info.history_id, info.version_id)
            # Momentarily revert to the mainline.
            object = repo.updateResource(object, 'mainline')
            repo.checkoutResource(object)

            # Copy the old state into the mainline object, minus __vc_info__.
            # XXX There ought to be some way to do this more cleanly.
            object._p_changed = 1
            for key in object.__dict__.keys():
                if key != '__vc_info__':
                    if not old_state.__dict__.has_key(key):
                        del object.__dict__[key]
            for key in old_state.__dict__.keys():
                if key != '__vc_info__':
                    object.__dict__[key] = old_state.__dict__[key]
            # Check in as a copy.
            repo.checkinResource(
                object, 'Copied from revision %s' % info.version_id)

        repo.checkoutResource(object)

        return object


    security.declareProtected(UseVersionControl, 'checkin')
    def checkin(self, object, message=''):
        """Checks in a new version on the development stage."""
        # Make sure we copy the current data.
        # XXX ZopeVersionControl tries to do this but isn't quite correct yet.
        get_transaction().commit(1)

        # Check in or add the object to the repository.
        repo = self._getVersionRepository()
        if not repo.isUnderVersionControl(object):
            repo.applyVersionControl(object)
        else:
            repo.checkinResource(object, message)


    security.declareProtected(UseVersionControl, 'isUnderVersionControl')
    def isUnderVersionControl(self, object):
        """Returns a true value if the object is under version control."""
        repo = self._getVersionRepository()
        return repo.isUnderVersionControl(object)


    security.declareProtected(UseVersionControl, 'isCheckedOut')
    def isCheckedOut(self, object):
        """Returns a true value if the object is checked out."""
        repo = self._getVersionRepository()
        if not repo.isUnderVersionControl(object):
            return 0
        info = repo.getVersionInfo(object)
        return (info.status == info.CHECKED_OUT)


    security.declareProtected(UseVersionControl, 'getLogEntries')
    def getLogEntries(self, object, only_checkins=0):
        """Returns the log entries for an object as a sequence of
        mappings."""
        repo = self._getVersionRepository()
        if not repo.isUnderVersionControl(object):
            return []
        entries = repo.getLogEntries(object)
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


    security.declareProtected(UseVersionControl, 'getVersionId')
    def getVersionId(self, object):
        """Returns the version ID of the current revision."""
        repo = self._getVersionRepository()
        if repo.isUnderVersionControl(object):
            return repo.getVersionInfo(object).version_id
        else:
            return ''


    security.declareProtected(UseVersionControl, 'revertToVersion')
    def revertToVersion(self, object, version_id):
        """Reverts the object to the given version.

        If make_new_revision, a new revision is created, so that
        the object's state can progress along a new line without
        making the user deal with branches, labels, etc.
        """
        repo = self._getVersionRepository()
        # Verify the object is under version control.
        repo.getVersionInfo(object)
        if self.isCheckedOut(object):
            # Save the current data.
            self.checkin(object, 'Auto-saved')
        return repo.updateResource(object, version_id)

InitializeClass(VersionsTool)

