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
    def reindexObject(self):
        catalog = getToolByName(self, 'portal_catalog', None)
        if catalog is not None:
            catalog.reindexObject(self)
        
    def manage_afterAdd(self, item, container):
        """
            Add self to the workflow and catalog.
        """
        #
        #   Are we being added (or moved)?
        #
        if aq_base(container) is not aq_base(self):
            self.indexObject()

    def manage_afterClone(self, item):
        """
            Add self to workflow, as we have just been cloned.
        """
        if aq_base(item) is aq_base(self):
            wf = getToolByName(self, 'portal_workflow', None)
            if wf is not None:
                wf.notifyCreated(self)

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
            #
            for item_id, subitem in self.objectItems():
                # Carefully avoid implicit acquisition of the
                # name "manage_beforeDelete"
                if hasattr(aq_base(subitem), 'manage_beforeDelete'):
                    subitem.manage_beforeDelete(item, container)


Globals.InitializeClass(CMFCatalogAware)

