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
class DublinCore:
    """
        Define which Dublin Core metadata elements are supported by the PTK,
        and the semantics therof.
    """

    def Title( self ):
        """
            Dublin Core element - resource name

            Return type: string
            Permissions: View
        """
        
    def Creator( self ):
        """
            Dublin Core element - resource creator

            Return the full name(s) of the author(s) of the content object.

            Return type: string
            Permission: View
        """

    def Subject( self ):
        """
            Dublin Core element - resource keywords

            Return zero or more keywords associated with the content object.

            Return type: sequence of strings
            Permission: View
        """

    def Description( self ):
        """
            Dublin Core element - resource summary

            Return a natural language description of this object.

            Return type: string
            Permissions: View
        """

    def Publisher( self ):
        """
            Dublin Core element - resource publisher

            Return full formal name of the entity or person responsible
            for publishing the resource.

            Return type: string
            Permission: View
        """

    def Contributors( self ):
        """
            Dublin Core element - resource collaborators

            Return zero or additional collaborators.

            Return type: sequence of strings
            Permission: View
        """
    
    def Date( self ):
        """
            Dublin Core element - default date

            Return type: string, formatted 'YYYY-MM-DD H24:MN:SS TZ'
            Permissions: View
        """
    
    def CreationDate( self ):
        """
            Dublin Core element - date resource created.

            Return type: string, formatted 'YYYY-MM-DD H24:MN:SS TZ'
            Permissions: View
        """
    
    def EffectiveDate( self ):
        """
            Dublin Core element - date resource becomes effective.

            Return type: string, formatted 'YYYY-MM-DD H24:MN:SS TZ'
            Permissions: View
        """
    
    def ExpirationDate( self ):
        """
            Dublin Core element - date resource expires.

            Return type: string, formatted 'YYYY-MM-DD H24:MN:SS TZ'
            Permissions: View
        """
    
    def ModificationDate( self ):
        """
            Dublin Core element - date resource last modified.

            Return type: string, formatted 'YYYY-MM-DD H24:MN:SS TZ'
            Permissions: View
        """

    def Type( self ):
        """
            Dublin Core element - resource type

            Return a human-readable type name for the resource
            (perhaps mapped from its Zope meta_type).

            Return type: string
            Permissions: View
        """

    def Format( self ):
        """
            Dublin Core element - resource format

            Return the resource's MIME type (e.g., 'text/html',
            'image/png', etc.).

            Return type: string
            Permissions: View
        """

    def Identifier( self ):
        """
            Dublin Core element - resource ID

            Returns unique ID (a URL) for the resource.

            Return type: string
            Permissions: View
        """

    def Language( self ):
        """
            Dublin Core element - resource language

            Return the RFC language code (e.g., 'en-US', 'pt-BR')
            for the resource.

            Return type: string
            Permissions: View
        """

    def Rights( self ):
        """
            Dublin Core element - resource copyright

            Return a string describing the intellectual property status,
            if any, of the resource.
            for the resource.

            Return type: string
            Permissions: View
        """

class CatalogableDublinCore:
    """
        Provide Zope-internal date objects for cataloging purposes.
    """
    def created( self ):
        """
            Dublin Core element - date resource created,

            Return type: DateTime
            Permissions: View
        """
    
    def effective( self ):
        """
            Dublin Core element - date resource becomes effective,

            Return type: DateBound
            Permissions: View
        """
    
    def expires( self ):
        """
            Dublin Core element - date resource expires,

            Return type: DateBound
            Permissions: View
        """
    
    def modified( self ):
        """
            Dublin Core element - date resource last modified,

            Return type: DateTime
            Permissions: View
        """

class MutableDublinCore:
    """
        Update interface for mutable metadata.
    """
    def setTitle( self, title ):
        "Dublin Core element - update resource name"

    def setSubject( self, subject ):
        "Dublin Core element - update resource keywords"

    def setDescription( self, description ):
        "Dublin Core element - update resource summary"

    def setContributors( self, contributors ):
        "Dublin Core element - update additional contributors to resource"

    def setEffectiveDate( self, effective_date ):
        """ Dublin Core element - update date resource becomes effective.  """
    
    def setExpirationDate( self, expiration_date ):
        """ Dublin Core element - update date resource expires.  """
    
    def setFormat( self, format ):
        """ Dublin Core element - update resource format """

    def setLanguage( self, language ):
        """ Dublin Core element - update resource language """

    def setRights( self, rights ):
        """ Dublin Core element - update resource copyright """

