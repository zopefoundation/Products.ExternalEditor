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

"""
    Type registration tool interface description.
"""
__version__='$Revision$'[11:-2]



try:
    from Interface import *
except:
    def Attribute( name, value ): pass
    class Base: ' '

class ContentTypeInformation( Base ):
    """
        Registry entry interface.
    """
    def Metatype( self ):
        """
            Return the Zope 'meta_type' for this content object.
        """
    
    def Type( self ):
        """
            Return the "human readable" type name (note that it
            may not map exactly to the 'meta_type', e.g., for
            l10n/i18n or where a single content class is being
            used twice, under different names.
        """
    
    def Description( self ):
        """
            Textual description of the class of objects (intended
            for display in a "constructor list").
        """
    
    def isConstructionAllowed( self, container ):
        """
        Does the current user have the permission required in
        order to construct an instance?
        """

    def allowType( self, contentType ):
        """
            Can objects of 'contentType' be added to containers whose
            type object we are?
        """

    def constructInstance( self, container, id ):
        """
            Build a "bare" instance of the appropriate type in
            'container', using 'id' as its id.  Return the URL
            of its "immediate" view (typically the metadata form).
        """

    def allowDiscussion( self ):
        """
            Can this type of object support discussion?
        """

    def getActionById( self, id ):
        """
            Return the URL of the action whose ID is id.
        """

    def getIcon(self):
        """
            Returns the portal-relative icon for this type.
        """

class portal_types( Base ):
    """
        Provides a configurable registry of portal content types.
    """
    id = Attribute('id', 'Must be set to "portal_types"')

    # getType__roles__ = None  # Public
    def getTypeInfo( self, contentType ):
        """
            Return an instance which implements the
            ContentTypeInformation interface, corresponding to
            the specified 'contentType'.  If contentType is actually
            an object, rather than a string, attempt to look up
            the appropriate type info using its Type or meta_type.
        """

    # listTypeInfo__roles__ = None  # Public
    def listTypeInfo( self, container=None ):
        """
            Return a sequence of instances which implement the
            ContentTypeInformation interface, one for each content
            type regisetered in the portal.  If the container
            is specified, the list will be filtered according to
            the user's permissions.
        """

    def listContentTypes( self, container=None, by_metatype=0 ):
        """
            Return list of content types, or the equivalent
            metatypes;  if 'container' is passed, then filter
            the list to include only types which are addable in
            'container'.
        """
    
    def constructContent( self, contentType, container, id ):
        """
            Build an instance of the appropriate content class in
            'container', using 'id'.
        """
