##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
##############################################################################
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
