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
from CMFCorePermissions import ModifyPortalContent
from utils import getToolByName


class CMFCatalogAware:
    """Mix-in for notifying portal_catalog and portal_workflow
    """

    security = ClassSecurityInfo()

    # Cataloging methods
    # ------------------

    security.declareProtected(ModifyPortalContent, 'indexObject')
    def indexObject(self):
        catalog = getToolByName(self, 'portal_catalog', None)
        if catalog is not None:
            catalog.indexObject(self)

    security.declareProtected(ModifyPortalContent, 'unindexObject')
    def unindexObject(self):
        catalog = getToolByName(self, 'portal_catalog', None)
        if catalog is not None:
            catalog.unindexObject(self)

    security.declareProtected(ModifyPortalContent, 'reindexObject')
    def reindexObject(self, idxs=[]):
        catalog = getToolByName(self, 'portal_catalog', None)
        if catalog is not None:
            catalog.reindexObject(self, idxs=idxs)

    def manage_afterAdd(self, item, container):
        """
            Add self to the workflow and catalog.
        """
        #
        #   Are we being added (or moved)?
        #
        if aq_base(container) is not aq_base(self):
            self.indexObject()
            #
            #   Now let our "aspects" know we were added or moved.
            #   For instance, talkbacks.
            #
            for item_id, subitem in self.objectItems():
                if hasattr(aq_base(subitem), 'manage_afterAdd'):
                    subitem.manage_afterAdd(item, container)

    def manage_afterClone(self, item):
        """
            Add self to workflow, as we have just been cloned.
        """
        wf = getToolByName(self, 'portal_workflow', None)
        if wf is not None:
            wf.notifyCreated(self)
            # After a clone, the workflow may have reset
            # its variables so the object has to be reindexed.
            self.reindexObject()
        #
        #   Now let our "aspects" know we have been cloned.
        #   For instance, talkbacks.
        #
        for item_id, subitem in self.objectItems():
            if hasattr(aq_base(subitem), 'manage_afterClone'):
                subitem.manage_afterClone(item)


    def manage_beforeDelete(self, item, container):
        """
            Remove self from the catalog.
        """
        #
        #   Are we going away?
        #
        if aq_base(container) is not aq_base(self):
            self.unindexObject()
            #
            #   Now let our "aspects" know we are going away.
            #   For instance, talkbacks.
            #
            for item_id, subitem in self.objectItems():
                # Carefully avoid implicit acquisition of the
                # name "manage_beforeDelete"
                if hasattr(aq_base(subitem), 'manage_beforeDelete'):
                    subitem.manage_beforeDelete(item, container)


Globals.InitializeClass(CMFCatalogAware)

