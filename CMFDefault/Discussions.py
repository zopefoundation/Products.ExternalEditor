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
 
import urllib, string

from ExtensionClass import Base
from Globals import HTMLFile, default__class_init__
from DateTime import DateTime
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.utils import getToolByName
from utils import _dtmldir

VIEW_PERMISSION             = 'View'
REPLY_TO_ITEM_PERMISSION    = 'Reply to item'

class Discussable(Base):
    """
    This is the mixin for PortalContent items which are discussable
    """

    _isDiscussable = 1

    __ac_permissions__ = ( ( VIEW_PERMISSION
                           , ( 'getReplyResults'
                             , 'getReplies'
                             )
                           )
                         , ( REPLY_TO_ITEM_PERMISSION
                           , ( 'createReply'
                             ,
                             )
                           )
                         )

    def createReply(self, title, text, REQUEST, RESPONSE):
        """
            Create a reply in the proper place
        """

        location, id = self.getReplyLocationAndID(REQUEST)
        location.addDiscussionItem(id, title, title, 'structured-text',
                                   text, self)

        RESPONSE.redirect( self.absolute_url() + '/view' )

    def getReplyLocationAndID(self, REQUEST):
        # It is not yet clear to me what the correct location for this hook is

        # Find the folder designated for replies, creating if missing
        home = getToolByName(self, 'portal_membership').getHomeFolder()
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

    def getReplyResults(self):
        """
            Return the ZCatalog results that represent this object's replies.

            Often, the actual objects are not needed.  This is less expensive
            than fetching the objects.
        """
        catalog = getToolByName(self, 'portal_catalog')
        return catalog.searchResults(in_reply_to=
                                      urllib.unquote('/'+self.absolute_url(1)))

    def getReplies(self):
        """
            Return a sequence of the DiscussionResponse objects which are
            associated with this Discussable
        """
        catalog = getToolByName(self, 'portal_catalog')
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

                       

class DiscussionResponse(Base):
    """
        This is the mixin for PortalContent items which may be responses
    """

    in_reply_to = ''

    # XXX I could probably remove a case from the resolution code
    
    def inReplyTo(self, REQUEST=None):
        """
            Return the Discussable object which this item is associated with
        """
        # Stolen from ZCatalog.resolve_url
        
        if REQUEST is None:
            REQUEST = self.REQUEST

        portal_url = getToolByName(self, 'portal_url')
        script = REQUEST.script
        path = portal_url.getPortalPath() + '/' + self.in_reply_to
        if string.find(path, script) != 0:
            path='%s/%s' % (script, path)
        return REQUEST.resolve_url(path)

    def setReplyTo(self, reply_to):
        """
            Make this object a response to the passed object
        """

        if type(reply_to) == type(''):
            REQUEST = self.REQUEST
            script = REQUEST.script
            if string.find(reply_to, script) != 0:
                reply_to='%s/%s' % (script,reply_to)
            reply_to = REQUEST.resolve_url(reply_to)

        if not reply_to.portal_discussion.isDiscussionAllowedFor(reply_to):
            raise ValueError, "Reply target does not accept replies"

        if hasattr(reply_to, 'meta_type') and reply_to.meta_type == 'Discussion Item':
            reply_url = reply_to.absolute_url(1)
        else:
            portal_url = getToolByName(self, 'portal_url')
            reply_url = portal_url.getRelativeUrl(reply_to)
    
        self.in_reply_to = urllib.unquote(reply_url)

        if hasattr(self, 'reindexObject'):
            self.reindexObject()

    def parentsInThread(self, size=0):
        """
            Return the list of object which are this object's parents,
            from the point of view of the threaded discussion.
            Parents are ordered oldest to newest.

            If 'size' is not zero, only the closest 'size' parents
            will be returned.
        """

        parents = []
        parent = self.inReplyTo()

        while parent and (not size or len(parents) < size):
            if parent in parents:
                # Paranoia: circular thread
                print self.absolute_url(), "is in a circular thread"
                break
            parents.append(parent)
            parent = hasattr(parent, 'inReplyTo') and parent.inReplyTo()
        parents.reverse()
        return parents

default__class_init__(Discussable)
