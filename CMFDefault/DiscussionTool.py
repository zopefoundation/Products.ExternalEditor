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

"""Basic portal discussion access tool.
$Id$
"""
__version__='$Revision$'[11:-2]


from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem

from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore import CMFCorePermissions

from utils import _dtmldir
from DiscussionItem import DiscussionItemContainer

class DiscussionNotAllowed( Exception ):
    pass

class DiscussionTool( UniqueObject, SimpleItem ):

    id = 'portal_discussion'
    meta_type = 'Default Discussion Tool'

    security = ClassSecurityInfo()

    manage_options = ( { 'label' : 'Overview', 'action' : 'manage_overview' }
                     , 
                     ) + SimpleItem.manage_options

    #
    #   ZMI methods
    #
    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'manage_overview' )
    manage_overview = DTMLFile( 'explainDiscussionTool', _dtmldir )

    #
    #   'portal_discussion' interface methods
    #

    security.declarePublic( 'overrideDiscussionFor' )
    def overrideDiscussionFor(self, content, allowDiscussion):
        """
            Override discussability for a per object basis or clear and let
            the site default override.
        """
        mtool = getToolByName( self, 'portal_membership' )
        if not mtool.checkPermission( CMFCorePermissions.ModifyPortalContent
                                    , content
                                    ):
            raise "Unauthorized"

        if allowDiscussion is None or allowDiscussion == 'None':
            if hasattr(content, 'allow_discussion'):
                del content.allow_discussion
        else:
            content.allow_discussion = int(allowDiscussion)

    security.declarePublic( 'getDiscussionFor' )
    def getDiscussionFor(self, content):
        """
            Return the talkback for content, creating it if need be.
        """
        if not self.isDiscussionAllowedFor( content ):
            raise DiscussionNotAllowed
            
        talkback = getattr( content, 'talkback', None )
        if not talkback:
            talkback = self._createDiscussionFor( content )
        
        return talkback

    security.declarePublic( 'isDiscussionAllowedFor' )
    def isDiscussionAllowedFor( self, content ):
        '''
            Returns a boolean indicating whether a discussion is
            allowed for the specified content.
        '''
        if hasattr( content, 'allow_discussion' ):
            return content.allow_discussion
        typeInfo = getToolByName(self, 'portal_types').getTypeInfo( content )
        if typeInfo:
            return typeInfo.allowDiscussion()
        return 0

    #
    #   ActionProvider interface
    #
    security.declarePrivate( 'listActions' )
    def listActions(self, info):
        # Return actions for reply and show replies
        content = info.content
        if content is None or not self.isDiscussionAllowedFor(content):
            return None

        discussion = self.getDiscussionFor(content)
        discussion_url = info.content_url

        actions = (
            {'name': 'Reply',
             'url': discussion_url + '/discussion_reply_form',
             'permissions': ['Reply to item'],
             'category': 'object'
             },
            )

        return actions

    #
    #   Utility methods
    #
    security.declarePrivate( '_createDiscussionFor' )
    def _createDiscussionFor( self, content ):
        """
            Create the object that holds discussion items inside
            the object being discussed, if allowed.
        """
        if not self.isDiscussionAllowedFor( content ):
            raise DiscussionNotAllowed

        content.talkback = DiscussionItemContainer()
        return content.talkback

InitializeClass( DiscussionTool )
