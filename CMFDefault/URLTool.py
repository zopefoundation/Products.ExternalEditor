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

"""CMFDefault portal_url tool.

$Id$
"""
__version__='$Revision$'[11:-2]


from Products.CMFCore.utils import UniqueObject
from OFS.SimpleItem import SimpleItem
import string
from Acquisition import aq_inner, aq_parent

from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.Expression import Expression
from Products.CMFCore import CMFCorePermissions
from utils import _dtmldir


class URLTool (UniqueObject, SimpleItem, ActionProviderBase):
    id = 'portal_url'
    meta_type = 'Default URL Tool'
    _actions = []

    security = ClassSecurityInfo()

    manage_options = ( ActionProviderBase.manage_options +
                      ({ 'label' : 'Overview', 'action' : 'manage_overview' } 
                     , 
                     ) + SimpleItem.manage_options
                     )

    #
    #   ZMI methods
    #
    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'manage_overview' )
    manage_overview = DTMLFile( 'explainURLTool', _dtmldir )

    #
    #   'portal_url' interface methods
    #
    security.declarePublic( '__call__' )
    def __call__(self, relative=0, *args, **kw):
        '''
        Returns the absolute URL of the portal.
        '''
        return aq_parent(aq_inner(self)).absolute_url(relative=relative)

    security.declarePrivate('listActions')
    def listActions(self, info=None):
        """
        Return a list of actions provided via the tool
        """
        return self._actions

    security.declarePublic( 'getPortalObject' )
    def getPortalObject( self ):
        """
            Return the portal object itself.
        """
        return self.aq_inner.aq_parent

    security.declarePublic( 'getRelativeContentPath' )
    def getRelativeContentPath( self, content ):
        """
            Return the path (sequence of IDs) for an object, relative 
            to the portal root
        """
        portal_path_length = len(self.aq_inner.aq_parent.getPhysicalPath())
        content_location = content.getPhysicalPath()
        return content_location[portal_path_length:]

    security.declarePublic( 'getRelativeContentURL' )
    def getRelativeContentURL( self, content ):
        """
            Return the URL (slash-separated string) for an object,
            relative to the portal root
        """
        return string.join( self.getRelativeContentPath( content ), '/' )

    security.declarePublic( 'getRelativeUrl' )
    def getRelativeUrl(self, content):
        """
        Returns a URL for an object that is relative 
        to the portal root. This is helpful for virtual hosting
        situations.
        """
        portal_path_length = len(self.aq_inner.aq_parent.getPhysicalPath())
        content_location = content.getPhysicalPath()
        rel_path = content_location[portal_path_length:]

        return string.join(rel_path, '/')

    security.declarePublic( 'getPortalPath' )
    def getPortalPath(self):
        """
        Returns the portal object's URL without the server URL component
        """
        return string.join(self.aq_inner.aq_parent.getPhysicalPath(), '/')


InitializeClass(URLTool)
