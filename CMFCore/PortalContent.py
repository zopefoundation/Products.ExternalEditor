##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" PortalContent: Base class for all CMF content.

$Id$
"""

from Globals import InitializeClass
from Acquisition import aq_base
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from webdav.WriteLockInterface import WriteLockInterface

from interfaces.Contentish import Contentish
from DynamicType import DynamicType
from CMFCatalogAware import CMFCatalogAware
from exceptions import NotFound
from exceptions import ResourceLockedError
from permissions import FTPAccess
from permissions import View


class PortalContent(DynamicType, CMFCatalogAware, SimpleItem):
    """
        Base class for portal objects.

        Provides hooks for reviewing, indexing, and CMF UI.

        Derived classes must implement the interface described in
        interfaces/DublinCore.py.
    """

    __implements__ = (Contentish,
                      WriteLockInterface,
                      DynamicType.__implements__)

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
                     + CMFCatalogAware.manage_options
                     + SimpleItem.manage_options
                     )

    security = ClassSecurityInfo()

    security.declareObjectProtected(View)

    # The security for FTP methods aren't set up by default in our
    # superclasses...  :(
    security.declareProtected(FTPAccess, 'manage_FTPstat')
    security.declareProtected(FTPAccess, 'manage_FTPget')
    security.declareProtected(FTPAccess, 'manage_FTPlist')

    def failIfLocked(self):
        """
        Check if isLocked via webDav
        """
        if self.wl_isLocked():
            raise ResourceLockedError('This resource is locked via webDAV.')
        return 0

    #
    #   Contentish interface methods
    #
    security.declareProtected(View, 'SearchableText')
    def SearchableText(self):
        """ Returns a concatination of all searchable text.

        Should be overriden by portal objects.
        """
        return "%s %s" % (self.Title(), self.Description())

    def __call__(self):
        """ Invokes the default view.
        """
        ti = self.getTypeInfo()
        method_id = ti and ti.queryMethodID('(Default)')
        if method_id:
            method = getattr(self, method_id)
            if getattr(aq_base(method), 'isDocTemp', 0):
                return method(self, self.REQUEST)
            else:
                return method()
        else:
            raise NotFound( 'Cannot find default view for "%s"' %
                            '/'.join( self.getPhysicalPath() ) )

InitializeClass(PortalContent)
