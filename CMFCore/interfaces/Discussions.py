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
def HTMLFile( unused ):
    """
       Stub for method loaded from DTML document.
    """

class Discussable:
    """
    Discussable is the interface for things which can have responses.
    It is implemented by PTKBase.Discussions.Discussable.  That class
    is designed to mix-in with a PortalContent-derived class.  It has
    already been mixed-in with the actual PortalContent class, so at
    present, any PTK object can support replies.

    This interface contains some bogosity.  Things like replyForm,
    replyPreview and createReply really shouldn't be done here.  The
    interface presently assumes that there is only one sort of object
    which the user would ever want to use to create a reply.  This is
    a bad assumption, and needs to be addressed!
    """

    threadView = HTMLFile('...')
    """
    The threadView method should return an HTML page which displays
    this item's children (and optionally parents, though not all
    Discussables can have parents).

    Permission: View
    """
    
    replyForm = HTMLFile('...')
    """
    The replyForm method should return an HTML page which presents an
    interface to enter a reply.  It should have buttons for submiting
    the form contents to replyPreview and createReply.

    Permission: Reply to item
    """

    replyPreview = HTMLFile('...')
    """
    This method needs to present the contents submitted from the
    replyForm form with a template similar to what the actual response
    object would use.  It should provide submit buttons linked to
    replyForm (for 'Edit') and createReply (for 'Reply').

    Permission: Reply to item
    """
    
    def createReply(self, title, text, REQUEST, RESPONSE):
        """
        Create a reply in the proper place.  See the next method for more
        information.

        Permission: Reply to item
        Returns: HTML (directly or via redirect)
        """

    def getReplyLocationAndID(self, REQUEST):
        """
        This method determines where a user's reply should be stored, and
        what it's ID should be.

        You don't really want to force users to have to select a
        unique ID each time they want to reply to something.  The
        present implementation selects a folder in the Member's home
        folder called 'Correspondence' (creating it if it is missing)
        and finds a free ID in that folder.

        createReply should use this method to determine what the reply
        it creates should be called, and where it should be placed.

        This method (and createReply, I expect) do not really belong in
        this interface.  There should be a DiscussionManager singleton
        (probably the portal object itself) which handles this.

        Permissions: None assigned
        Returns: 2-tuple, containing the container object, and a string ID.
        """

    def getReplyResults(self):
        """
        Return the ZCatalog results that represent this object's replies.

        Often, the actual objects are not needed.  This is less expensive
        than fetching the objects.

        Permissions: View
        Returns: sequence of ZCatalog results representing DiscussionResponses
        """

                       
    def getReplies(self):
        """
        Return a sequence of the DiscussionResponse objects which are
        associated with this Discussable

        Permissions: View
        Returns: sequence of DiscussionResponses
        """

    def quotedContents(self):
        """
        Return this object's contents in a form suitable for inclusion
        as a quote in a response.  The default implementation returns
        an empty string.  It might be overridden to return a '>' quoted
        version of the item.
        """

    def allowReplies(self):
        """
        This method must return a logically true value if an object is
        willing to support replies.

        Permissions: None assigned
        Returns: truth value
        """
        
class DiscussionResponse:
    """
    
    This interface describes the behaviour of a Discussion Response.
    It is implemented in PTKBase.Discussions.DiscussionResponse.  This
    implementation is also designed to be mixed together with
    PortalContent.  This has been done in the
    PTK.DiscussionItem.DiscussionItem class, which the PTK presently
    uses for all replies.
    """

    def inReplyTo(self, REQUEST=None):
        """
        Return the Discussable object which this item is associated with

        Permissions: None assigned
        Returns: a Discussable object
        """

    def setReplyTo(self, reply_to):
        """
        Make this object a response to the passed object.  (Will also
        accept a path in the form of a string.)  If reply_to does not
        support or accept replies, a ValueError will be raised.  (This
        does not seem like the right exception.)

        Permissions: None assigned
        Returns: None
        """

    def parentsInThread(self, size=0):
        """
        Return the list of object which are this object's parents, from the
        point of view of the threaded discussion.  Parents are ordered
        oldest to newest.

        If 'size' is not zero, only the closest 'size' parents will be
        returned.
        """
