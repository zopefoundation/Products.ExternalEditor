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
from Globals import HTMLFile, Persistent, PersistentMapping, InitializeClass
from AccessControl import ClassSecurityInfo
from Acquisition import Implicit, aq_base, aq_inner, aq_parent
from OFS.Traversable import Traversable
from DateTime import DateTime

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.PortalContent import PortalContent

from Document import Document
from DublinCore import DefaultDublinCoreImpl


factory_type_information = ( { 'id'             : 'Discussion Item'
                             , 'meta_type'      : 'Discussion Item'
                             , 'description'    : """\
Discussion Items are documents which reply to other content.
They should *not* be addable through the standard 'folder_factories'
interface."""
                             , 'icon'           : 'discussionitem_icon.gif'
                             , 'product'        : '' # leave blank to suppress
                             , 'factory'        : ''
                             , 'immediate_view' : ''
                             , 'actions'        :
                                ( { 'name'          : 'View'
                                  , 'action'        : 'discussionitem_view'
                                  , 'permissions'   : (
                                      CMFCorePermissions.View, )
                                  }
                                ,
                                )
                             }
                           ,
                           )


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
                    , DefaultDublinCoreImpl
                    ):
    """
        Class for content which is a response to other content.
    """
    meta_type           = 'Discussion Item'
    allow_discussion    = 1
    creator             = 'unknown'
    in_reply_to         = None
    review_state        ='published'

    security = ClassSecurityInfo()

    security.declareProtected( CMFCorePermissions.View, 'Creator' )
    def Creator( self ):
        """
            We need to return user who replied, rather than executable
            owner.
        """
        #   XXX:  revisit if Creator becomes "real" attribute for stock DC.
        return self.creator
    
    #
    #   DiscussionResponse interface
    #
    security.declareProtected( CMFCorePermissions.View, 'inReplyTo' )
    def inReplyTo( self, REQUEST=None ):
        """
            Return the Discussable object to which we are a reply.

            Two cases obtain:

              - We are a "top-level" reply to a non-DiscussionItem piece
                of content;  in this case, our 'in_reply_to' field will
                be None.
            
              - We are a nested reply;  in this case, our 'in_reply_to'
                field will be the ID of the parent DiscussionItem.
        """
        tool = getToolByName( self, 'portal_discussion' )
        talkback = tool.getDiscussionFor( self )
        return talkback._getReplyParent( self.in_reply_to )

    security.declarePrivate( CMFCorePermissions.View, 'setReplyTo' )
    def setReplyTo( self, reply_to ):
        """
            Make this object a response to the passed object.
        """
        if getattr( reply_to, 'meta_type', None ) == self.meta_type:
            self.in_reply_to = reply_to.getId()
        else:
            self.in_reply_to = None
    
    security.declareProtected( CMFCorePermissions.View, 'parentsInThread' )
    def parentsInThread( self, size=0 ):
        """
            Return the list of items which are "above" this item in
            the discussion thread.

            If 'size' is not zero, only the closest 'size' parents
            will be returned.
        """
        parents = []
        current = self
        while not size or len( parents ) < size:
            parent = current.inReplyTo()
            assert not parent in parents  # sanity check
            parents.insert( 0, parent )
            if parent.meta_type != self.meta_type:
                break
            current = parent
        return parents

InitializeClass( DiscussionItem )

class DiscussionItemContainer( Persistent, Implicit, Traversable ):
    """
        Store DiscussionItem objects. Discussable content that
        has DiscussionItems associated with it will have an
        instance of DiscussionItemContainer injected into it to
        hold the discussion threads.
    """

    # for the security machinery to allow traversal
    #__roles__ = None

    security = ClassSecurityInfo()

    def __init__(self):
        self.id = 'talkback'
        self._container = PersistentMapping()

    security.declareProtected( CMFCorePermissions.View, 'getId' )
    def getId( self ):
        return self.id

    # Is this right?
    security.declareProtected( CMFCorePermissions.View, '__bobo_traverse__' )
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

    security.declarePrivate( 'manage_beforeDelete' )
    def manage_beforeDelete(self, item, container):
        """
            Remove the contained items from the catalog.
        """
        if aq_base(container) is not aq_base(self):
            for obj in self.objectValues():
                obj.__of__( self ).manage_beforeDelete( item, container )

    #
    #   OFS.ObjectManager query interface.
    #
    security.declareProtected( CMFCorePermissions.AccessContentsInformation
                             , 'objectIds' )
    def objectIds( self, spec=None ):
        """
            Return a list of the ids of our DiscussionItems.
        """
        if spec and spec is not DiscussionItem.meta_type:
            return []
        return self._container.keys()


    security.declareProtected( CMFCorePermissions.AccessContentsInformation
                             , 'objectItems' )
    def objectItems(self, spec=None):
        """
            Return a list of (id, subobject) tuples for our DiscussionItems.
        """
        r=[]
        a=r.append
        g=self._container.get
        for id in self.objectIds(spec):
            a( (id, g( id ) ) )
        return r


    security.declareProtected( CMFCorePermissions.AccessContentsInformation
                             , 'objectValues' )
    def objectValues(self):
        """
            Return a list of our DiscussionItems.
        """
        return self._container.values()

    #
    #   Discussable interface
    #
    security.declareProtected( CMFCorePermissions.ReplyToItem, 'createReply' )
    def createReply( self, title, text, Creator=None ):
        """
            Create a reply in the proper place
        """
        container = self._container

        id = int(DateTime().timeTime())
        while self._container.get( str(id), None ) is not None:
            id = id + 1
        id = str( id )

        item = DiscussionItem( id, title=title, description=title )
        item._edit( text_format='structured-text', text=text )

        if Creator:
            item.creator = Creator

        item.__of__( self ).indexObject()

        item.setReplyTo( self._getDiscussable() )
 
        self._container[ id ] = item

        return id

    security.declareProtected( CMFCorePermissions.View, 'hasReplies' )
    def hasReplies( self ):
        """
            Test to see if there are any dicussion items
        """
        return len( self._container )

    security.declareProtected( CMFCorePermissions.View, 'getReplies' )
    def getReplies( self ):
        """
            Return a sequence of the DiscussionResponse objects which are
            associated with this Discussable
        """
        objects = []
        a = objects.append
        result_ids = self._getReplyResults()

        for id in result_ids:
            a( self._container.get( id ).__of__( self ) )

        return objects

    security.declareProtected( CMFCorePermissions.View, 'quotedContents' )
    def quotedContents(self):
        """
            Return this object's contents in a form suitable for inclusion
            as a quote in a response.
        """
 
        return ""
    
    #
    #   Utility methods
    #
    security.declarePrivate( '_getReplyParent' )
    def _getReplyParent( self, in_reply_to ):
        """
            Return the object indicated by the 'in_reply_to', where
            'None' represents the "outer" content object.
        """
        outer = self._getDiscussable( outer=1 )
        if in_reply_to is None:
            return outer
        parent = self._container[ in_reply_to ].__of__( aq_inner( self ) )
        return parent.__of__( outer )
        

    security.declarePrivate( '_getDiscussable' )
    def _getDiscussable( self, outer=0 ):
        """
        """
        tb = outer and aq_inner( self ) or self
        return getattr( tb, 'aq_parent', None )

    security.declarePrivate( '_getReplyResults' )
    def _getReplyResults( self ):
        """
           Get a list of ids of DiscussionItems which are replies to
           our Discussable.
        """
        discussable = self._getDiscussable()
        outer = self._getDiscussable( outer=1 )

        if discussable == outer:
            in_reply_to = None
        else:
            in_reply_to = discussable.getId()

        result = []
        a = result.append
        for key, value in self._container.items():
            if value.in_reply_to == in_reply_to:
                a( key )

        return result

InitializeClass( DiscussionItemContainer )


