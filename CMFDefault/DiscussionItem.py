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

import Globals
from Globals import HTMLFile, Persistent, PersistentMapping
from Acquisition import Implicit
from Discussions import DiscussionResponse
from Document import Document
from DublinCore import DefaultDublinCoreImpl
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName, _checkPermission
import urllib, string

def addDiscussionItem(self, id, title, description, text_format, text,
                      reply_to, RESPONSE=None):
    """
    Add a discussion item

    'title' is also used as the subject header
    if 'description' is blank, it is filled with the contents of 'title'
    'reply_to' is the object (or path to the object) which this is a reply to

    Otherwise, same as addDocument
    """

    if not description: description = title
        
    item = DiscussionItem( id )
    item.title = title
    item.description = description
    item.text_format = text_format
    item.text = text
    item.setReplyTo(reply_to)

    item._parse()
    self._setObject(id, item)

    if RESPONSE is not None:
        RESPONSE.redirect(self.absolute_url())

    
class DiscussionItem( Document
                    , DiscussionResponse
                    , DefaultDublinCoreImpl
                    ):
    """
    This is the PortalContent object for content which is a response to other
    content.
    """
    meta_type = 'Discussion Item'
    allow_discussion = 1
    creator = 'unknown'

    __ac_permissions__ = (
        ('Change Discussion Items', ('edit',), ('Owner',)),
        ('View', ('', 'absolute_url', 'getReplies', 'view')),
        )

    view = HTMLFile('dtml/discussionView',globals())
    index_html = view
    editForm = HTMLFile('dtml/discussionEdit',globals())

    # Replies should default to published
    review_state='published'

    def absolute_url(self, relative=0):
        portal_url = getToolByName(self, 'portal_url')
        container = self.aq_inner.aq_parent
        content_item = container.aq_inner.aq_parent
        parent_rel_url = portal_url.getRelativeUrl(content_item)

        fmt_string = '%s/%s/talkback/%s'

        if relative:
            prefix = portal_url.getPortalPath()
        else:
            prefix = portal_url()

        return fmt_string % ( prefix, parent_rel_url, str( self.id ) )

    def getPhysicalPath(self):
        """
        Needs to be overridden here because the standard implementation
        doesn't fit my needs in case i am stored in a DiscussionItemContainer
        """
        return tuple(string.split(self.absolute_url(1), '/'))

    def getReplies(self):
        """
        Return a list of all objects that have their "in_reply_to"
        attribute set to my own URL
        """
        result = []
        my_url = urllib.unquote( self.absolute_url(1) )
        wf = getToolByName( self, 'portal_workflow' )
        talkback = self.aq_inner.aq_parent

        for item in talkback._container.values():
            if item.in_reply_to == my_url:
                if wf.getInfoFor( item, 'review_state' ) == 'published':
                    result.append(item.__of__(talkback))

        return result

    def __call__(self, REQUEST, **kw):
        return apply(self.view, (self, REQUEST), kw)

    def edit(self, text_format, text, file='', REQUEST=None):
        """
        Edit the discussion item.
        """

        Document.edit(self, text_format, text, file)
        if REQUEST is not None:
            return self.editForm(self, REQUEST, portal_status_message= \
                                 'Discussion item changed.')

    def Creator( self ):
        """
        """
        return self.creator


Globals.default__class_init__(DiscussionItem)


class DiscussionItemContainer(Persistent, Implicit):
    """
    This class stores DiscussionItem objects. Discussable 
    content that has DiscussionItems associated with it 
    will have an instance of DiscussionItemContainer 
    injected into it to hold the discussion threads.
    """

    # for the security machinery to allow traversal
    __roles__ = None
    __allow_access_to_unprotected_subobjects__ = 1   # legacy code


    __ac_permissions__ = ( ( 'Access contents information'
                           , ( 'objectIds'
                             , 'objectValues'
                             , 'objectItems'
                             )
                           )
                         , ( 'View'
                           , ( 'hasReplies'
                             , 'getReplies'
                             , '__bobo_traverse__'
                             )
                           )
                         , ( 'Reply to item'
                           , ( 'createReply'
                             ,
                             )
                           )
                         ) 

    def __init__(self):
        self.id = 'talkback'
        self._container = PersistentMapping()


    def __bobo_traverse__(self, REQUEST, name):
        """
        This will make this container traversable
        """
        target = getattr(self, name, None)
        if target is not None:
            return target
        else:
            try:
                return self._container.get(name).__of__(self)
            except:
                REQUEST.RESPONSE.notFoundError("%s\n%s" % (name, ''))

    def objectIds(self, spec=None):
        """
        return a list of ids of DiscussionItems in
        this DiscussionItemContainer
        """
        return self._container.keys()

    def objectItems(self, spec=None):
        """
        Returns a list of (id, subobject) tuples of the current object.
        If 'spec' is specified, returns only objects whose meta_type
        match 'spec'
        """
        r=[]
        a=r.append
        g=self._container.get
        for id in self.objectIds(spec): a((id, g(id)))
        return r

    def objectValues(self):
        """
        return the list of objects stored in this
        DiscussionItemContainer
        """
        return self._container.values()

    def createReply(self, title, text, REQUEST, RESPONSE):
        """
            Create a reply in the proper place
        """
        container = self._container

        id = int(DateTime().timeTime())
        while getattr(self._container, `id`, None) is not None:
            id = id + 1

        item = DiscussionItem( `id` )
        item.title = title
        item.description = title
        item.text_format = 'structured-text'
        item.text = text

        if REQUEST.has_key( 'Creator' ):
            item.creator = REQUEST[ 'Creator' ]

        item.__of__(self).setReplyTo(self.aq_parent)
 
        item._parse()
        self._container[`id`] = item

        RESPONSE.redirect( self.aq_inner.aq_parent.absolute_url() + '/view' )

    def hasReplies(self):
        """
        Test to see if there are any dicussion items
        """
        if len(self._container) > 0:
            return 1
        else:
            return 0

    def _getReplyResults(self):
        """
           Get a list of ids within the discussion item container that are 
           in reply to me
        """
        result = []
        portal_url = getToolByName(self, 'portal_url')
        my_url = urllib.unquote( portal_url.getRelativeUrl( self ) )
        wf = getToolByName( self, 'portal_workflow' )

        for item in self._container.values():
            if item.in_reply_to == my_url:
                if wf.getInfoFor( item, 'review_state' ) == 'published':
                    result.append(item.id)

        return result

    def getReplies(self):
        """
            Return a sequence of the DiscussionResponse objects which are
            associated with this Discussable
        """
        objects = []
        result_ids = self._getReplyResults()

        for id in result_ids:
            objects.append(self._container.get(id).__of__(self))

        return objects


    def quotedContents(self):
        """
            Return this object's contents in a form suitable for inclusion
            as a quote in a response.
        """
 
        return ""

Globals.default__class_init__(DiscussionItemContainer)


from Products.CMFCore.register import registerPortalContent
registerPortalContent(DiscussionItem,
                      constructors=(addDiscussionItem,),
                      action="",
                      icon="discussionitem.gif",
                      productGlobals=globals())
