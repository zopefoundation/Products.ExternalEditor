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

"""PortalContent: Base class for all CMF content.
$Id$
"""
__version__='$Revision$'[11:-2]

import string, urllib

from DateTime import DateTime
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from CMFCorePermissions import AccessContentsInformation, View, \
     ReviewPortalContent, ModifyPortalContent
import CMFCorePermissions
from interfaces.Contentish import Contentish
from DynamicType import DynamicType
from utils import getToolByName, _checkPermission, _getViewFor
from webdav.Lockable import ResourceLockedError
try: 
    from webdav.WriteLockInterface import WriteLockInterface
    NoWL = 0
except ImportError: NoWL = 1
from Acquisition import aq_base


class PortalContent(DynamicType, SimpleItem):
    """
        Base class for portal objects.
        
        Provides hooks for reviewing, indexing, and CMF UI.

        Derived classes must implement the interface described in
        interfaces/DublinCore.py.
    """
    
    if not NoWL:
        __implements__ = (WriteLockInterface, Contentish,)
    else:
        __implements__ = (Contentish)
    isPortalContent = 1
    _isPortalContent = 1  # More reliable than 'isPortalContent'.

    manage_options = ( ( { 'label'  : 'Dublin Core'
                         , 'action' : 'manage_metadata'
                         }
                       , { 'label'  : 'Edit'
                         , 'action' : 'manage_edit'
                         }
                       , { 'label'  : 'View'
                         , 'action' : 'view'
                         }
                       )
                     + SimpleItem.manage_options
                     )

    security = ClassSecurityInfo()

    security.declareObjectProtected(CMFCorePermissions.View)

    # The security for FTP methods aren't set up by default in our
    # superclasses...  :(
    security.declareProtected(CMFCorePermissions.FTPAccess,
                              'manage_FTPstat',
                              'manage_FTPget',
                              'manage_FTPlist',)

    def failIfLocked(self):
        """
        Check if isLocked via webDav
        """
        if self.wl_isLocked():
            raise ResourceLockedError, 'This resource is locked via webDAV'
        return 0

    # indexed methods
    # ---------------
    
    security.declareProtected(View, 'SearchableText')
    def SearchableText(self):
        "Returns a concatination of all searchable text"
        # Should be overriden by portal objects
        return "%s %s" % (self.Title(), self.Description())

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
            wf = getToolByName(self, 'portal_workflow', None)
            if wf is not None:
                wf.notifyCreated(self)
            self.indexObject()

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
            for it, subitem in self.objectItems():
                si_m_bD = getattr( subitem, 'manage_beforeDelete', None )
                if si_m_bD is not None:
                    si_m_bD( item, container )


    # Contentish interface methods
    # ----------------------------

    def __call__(self):
        '''
        Invokes the default view.
        '''
        view = _getViewFor(self)
        if getattr(aq_base(view), 'isDocTemp', 0):
            return apply(view, (self, self.REQUEST))
        else:
            return view()

    index_html = None  # This special value informs ZPublisher to use __call__

    security.declareProtected(CMFCorePermissions.View, 'view')
    def view(self):
        '''
        Returns the default view even if index_html is overridden.
        '''
        return self()

    # Overridden methods to support cataloging items that might
    # be stored in attributes unknown to the content object, such
    # as the DiscussionItemContainer "talkback"

    security.declareProtected(AccessContentsInformation, 'objectItems')
    def objectItems(self):
        """
        since 'talkback' is the only opaque item on content
        right now, I will return that. Should be replaced with
        a list of tuples for every opaque item!
        """
        talkback = ( hasattr( aq_base( self ), 'talkback' ) and
                      self.talkback or None )
        if talkback is not None:
            return ((talkback.id, talkback),)
        else:
            return ()

InitializeClass(PortalContent)
