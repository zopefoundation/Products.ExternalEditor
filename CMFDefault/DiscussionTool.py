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
""" Basic portal discussion access tool.

$Id$
"""

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Globals import DTMLFile
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem

from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.Expression import Expression
from Products.CMFCore.interfaces.Discussions \
        import DiscussionResponse as IDiscussionResponse
from Products.CMFCore.interfaces.portal_discussion \
        import portal_discussion as IDiscussionTool
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import UniqueObject

from DiscussionItem import DiscussionItemContainer
from exceptions import AccessControl_Unauthorized
from exceptions import DiscussionNotAllowed
from permissions import ManagePortal
from permissions import ModifyPortalContent
from permissions import ReplyToItem
from utils import _dtmldir


class DiscussionTool( UniqueObject, SimpleItem, ActionProviderBase ):
    """ Links content to discussions.
    """

    __implements__ = (IDiscussionTool, ActionProviderBase.__implements__)

    id = 'portal_discussion'
    meta_type = 'Default Discussion Tool'
    _actions = (ActionInformation(id='reply'
                                , title='Reply'
                                , action=Expression(
                text='string:${object_url}/discussion_reply_form')
                                , condition=Expression(
                text='python: object is not None and ' +
                'portal.portal_discussion.isDiscussionAllowedFor(object)')
                                , permissions=(ReplyToItem,)
                                , category='object'
                                , visible=1
                                 )
               ,
               )

    security = ClassSecurityInfo()

    manage_options = (ActionProviderBase.manage_options +
                     ({ 'label' : 'Overview', 'action' : 'manage_overview' }
                     ,
                     ) + SimpleItem.manage_options)

    #
    #   ZMI methods
    #
    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = DTMLFile( 'explainDiscussionTool', _dtmldir )

    #
    #   'portal_discussion' interface methods
    #

    security.declarePublic( 'overrideDiscussionFor' )
    def overrideDiscussionFor(self, content, allowDiscussion):
        """ Override discussability for the given object or clear the setting.
        """
        mtool = getToolByName( self, 'portal_membership' )
        if not mtool.checkPermission(ModifyPortalContent, content):
            raise AccessControl_Unauthorized

        if allowDiscussion is None or allowDiscussion == 'None':
            if hasattr( aq_base(content), 'allow_discussion'):
                del content.allow_discussion
        else:
            content.allow_discussion = bool(allowDiscussion)

    security.declarePublic( 'getDiscussionFor' )
    def getDiscussionFor(self, content):
        """ Get DiscussionItemContainer for content, create it if necessary.
        """
        if not self.isDiscussionAllowedFor( content ):
            raise DiscussionNotAllowed

        if IDiscussionResponse.isImplementedBy(content):
            # Discussion Items use the DiscussionItemContainer object of the
            # related content item, so talkback needs to be acquired
            talkback = getattr(content, 'talkback')
        else:
            talkback = getattr( aq_base(content), 'talkback', None )
            if not talkback:
                talkback = self._createDiscussionFor( content )

        return talkback

    security.declarePublic( 'isDiscussionAllowedFor' )
    def isDiscussionAllowedFor( self, content ):
        """ Get boolean indicating whether discussion is allowed for content.
        """
        if hasattr( content, 'allow_discussion' ):
            return bool(content.allow_discussion)
        typeInfo = getToolByName(self, 'portal_types').getTypeInfo( content )
        if typeInfo:
            return bool( typeInfo.allowDiscussion() )
        return False

    #
    #   Utility methods
    #
    security.declarePrivate( '_createDiscussionFor' )
    def _createDiscussionFor( self, content ):
        """ Create DiscussionItemContainer for content, if allowed.
        """
        if not self.isDiscussionAllowedFor( content ):
            raise DiscussionNotAllowed

        content.talkback = DiscussionItemContainer()
        return content.talkback

InitializeClass( DiscussionTool )
