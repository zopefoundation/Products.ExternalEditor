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

import Globals
from Acquisition import aq_base

from AccessControl import ClassSecurityInfo
from CMFCorePermissions import ModifyPortalContent, AccessContentsInformation
from utils import getToolByName


class CMFCatalogAware:
    """Mix-in for notifying portal_catalog and portal_workflow
    """

    security = ClassSecurityInfo()

    # Cataloging methods
    # ------------------

    security.declareProtected(ModifyPortalContent, 'indexObject')
    def indexObject(self):
        """
            Index the object in the portal catalog.
        """
        catalog = getToolByName(self, 'portal_catalog', None)
        if catalog is not None:
            catalog.indexObject(self)

    security.declareProtected(ModifyPortalContent, 'unindexObject')
    def unindexObject(self):
        """
            Unindex the object from the portal catalog.
        """
        catalog = getToolByName(self, 'portal_catalog', None)
        if catalog is not None:
            catalog.unindexObject(self)

    security.declareProtected(ModifyPortalContent, 'reindexObject')
    def reindexObject(self, idxs=[]):
        """
            Reindex the object in the portal catalog.
            If idxs is present, only those indexes are reindexed.
            The metadata is always updated.

            Also update the modification date of the object.
        """
        if hasattr(aq_base(self), 'notifyModified'):
            # Update modification date.
            self.notifyModified()
        catalog = getToolByName(self, 'portal_catalog', None)
        if catalog is not None:
            catalog.reindexObject(self, idxs=idxs)

    security.declareProtected(ModifyPortalContent, 'reindexObjectSecurity')
    def reindexObjectSecurity(self):
        """
            Reindex security-related indexes on the object
            (and its descendants).
        """
        catalog = getToolByName(self, 'portal_catalog', None)
        if catalog is not None:
            path = '/'.join(self.getPhysicalPath())
            for brain in catalog.searchResults(path=path):
                ob = brain.getObject()
                s = getattr(ob, '_p_changed', 0)
                catalog.reindexObject(ob, idxs=['allowedRolesAndUsers'])
                if s is None: ob._p_deactivate()
            # Reindex the object itself, as the PathIndex only gave us
            # the descendants.
            self.reindexObject(idxs=['allowedRolesAndUsers'])

    # Workflow methods
    # ----------------

    security.declarePrivate('notifyWorkflowCreated')
    def notifyWorkflowCreated(self):
        """
            Notify the workflow that self was just created.
        """
        wftool = getToolByName(self, 'portal_workflow', None)
        if wftool is not None:
            wftool.notifyCreated(self)

    # Opaque subitems
    # ---------------

    security.declareProtected(AccessContentsInformation, 'opaqueItems')
    def opaqueItems(self):
        """
            Return opaque items (subelements that are contained
            using something that is not an ObjectManager).
        """
        # Since 'talkback' is the only opaque item on content
        # right now, I will return that. Should be replaced with
        # a list of tuples for every opaque item!
        if hasattr(aq_base(self), 'talkback'):
            talkback = self.talkback
            if talkback is not None:
                return ((talkback.id, talkback),)
        return ()

    security.declareProtected(AccessContentsInformation, 'opaqueIds')
    def opaqueIds(self):
        """
            Return opaque ids (subelements that are contained
            using something that is not an ObjectManager).
        """
        return [t[0] for t in self.opaqueItems()]

    security.declareProtected(AccessContentsInformation, 'opaqueValues')
    def opaqueValues(self):
        """
            Return opaque values (subelements that are contained
            using something that is not an ObjectManager).
        """
        return [t[1] for t in self.opaqueItems()]

    # Hooks
    # -----

    def manage_afterAdd(self, item, container):
        """
            Add self to the catalog.
            (Called when the object is created or moved.)
        """
        if aq_base(container) is not aq_base(self):
            self.indexObject()
            self.__recurse('manage_afterAdd', item, container)

    def manage_afterClone(self, item):
        """
            Add self to the workflow.
            (Called when the object is cloned.)
        """
        self.notifyWorkflowCreated()
        self.__recurse('manage_afterClone', item)

    def manage_beforeDelete(self, item, container):
        """
            Remove self from the catalog.
            (Called when the object is deleted or moved.)
        """
        if aq_base(container) is not aq_base(self):
            self.__recurse('manage_beforeDelete', item, container)
            self.unindexObject()

    def __recurse(self, name, *args):
        """
            Recurse in both normal and opaque subobjects.
        """
        values = self.objectValues()
        opaque_values = self.opaqueValues()
        for subobjects in values, opaque_values:
            for ob in subobjects:
                s = getattr(ob, '_p_changed', 0)
                if hasattr(aq_base(ob), name):
                    getattr(ob, name)(*args)
                if s is None: ob._p_deactivate()

Globals.InitializeClass(CMFCatalogAware)
