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

"""Basic portal discussion access tool.
$Id$
"""
__version__='$Revision$'[11:-2]


from utils import UniqueObject
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass
import Acquisition
from CMFCorePermissions import View, ReplyToItem
from AccessControl import ClassSecurityInfo


class OldDiscussable(Acquisition.Implicit):
    """
        Adapter for PortalContent to implement "old-style" discussions.
    """

    _isDiscussable = 1

    security = ClassSecurityInfo()
    

    def __init__( self, content ):
        self.content = content

    security.declareProtected(ReplyToItem, 'createReply')
    def createReply(self, title, text, REQUEST, RESPONSE):
        """
            Create a reply in the proper place
        """

        location, id = self.getReplyLocationAndID(REQUEST)
        location.addDiscussionItem(id, title, title, 'structured-text',
                                   text, self.content)

        RESPONSE.redirect( self.absolute_url() + '/view' )

    def getReplyLocationAndID(self, REQUEST):
        # It is not yet clear to me what the correct location for this hook is

        # Find the folder designated for replies, creating if missing
        home = self.content.portal_membership.getHomeFolder()
        if not hasattr(home, 'Correspondence'):
            home.manage_addPortalFolder('Correspondence')
        location = home.Correspondence
        location.manage_permission('View', ['Anonymous'], 1)
        location.manage_permission('Access contents information',
                                   ['Anonymous'], 1)

        # Find an unused id in location
        id = int(DateTime().timeTime())
        while hasattr(location, `id`):
            id = id + 1

        return location, `id`

    security.declareProtected(View, 'getReplyResults')
    def getReplyResults(self):
        """
            Return the ZCatalog results that represent this object's replies.

            Often, the actual objects are not needed.  This is less expensive
            than fetching the objects.
        """
        catalog = self.content.portal_catalog
        return catalog.searchResults(in_reply_to=
                                      urllib.unquote('/'+self.absolute_url(1)))

    security.declareProtected(View, 'getReplies')
    def getReplies(self):
        """
            Return a sequence of the DiscussionResponse objects which are
            associated with this Discussable
        """
        catalog = self.content.portal_catalog
        results = self.getReplyResults()
        rids    = map(lambda x: x.data_record_id_, results)
        objects = map(catalog.getobject, rids)
        return objects

    def quotedContents(self):
        """
            Return this object's contents in a form suitable for inclusion
            as a quote in a response.
        """

        return ""


class DiscussionTool (UniqueObject, SimpleItem):
    id = 'portal_discussion'
    meta_type = 'Oldstyle CMF Discussion Tool'
    # This tool is used to find the discussion for a given content object.

    security = ClassSecurityInfo()

    security.declarePublic('getDiscussionFor')
    def getDiscussionFor(self, content):
        '''Gets the PortalDiscussion object that applies to content.
        '''
        return OldDiscussable( content ).__of__( content )

    security.declarePublic('isDiscussionAllowedFor')
    def isDiscussionAllowedFor(self, content):
        '''
            Returns a boolean indicating whether a discussion is
            allowed for the specified content.
        '''
        if hasattr( content, 'allow_discussion' ):
            return content.allow_discussion
        typeInfo = self.portal_types.getTypeInfo( content.Type() )
        if typeInfo:
            return typeInfo.allowDiscussion()
        return 0


    def listActions(self, info):
        # Return actions for reply and show replies
        content = info.content
        if content is None or not self.isDiscussionAllowedFor(content):
            return None

        discussion = self.getDiscussionFor(content)
        if discussion.aq_base == content.aq_base:
            discussion_url = info.content_url
        else:
            discussion_url = discussion.absolute_url()

        actions = (
            {'name': 'Reply',
             'url': discussion_url + '/discussion_reply_form',
             'permissions': ['Reply to item'],
             'category': 'object'
             },
            )

        return actions


InitializeClass(DiscussionTool)
