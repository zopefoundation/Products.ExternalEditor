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
 
import string
from OFS.PropertyManager import PropertyManager
from Globals import default__class_init__, HTMLFile
from DateTime.DateTime import DateTime
from utils import tuplize
from Products.CMFCore.WorkflowCore import WorkflowAction
from Acquisition import aq_base

class DefaultDublinCoreImpl( PropertyManager ):
    """
        Mix-in class which provides Dublin Core methods
    """

    __ac_permissions__ = (
        ( 'View'
        , ( 'Title'
          , 'Creator'
          , 'Subject'
          , 'Description'
          , 'Publisher'
          , 'Contributors'
          , 'Date'
          , 'CreationDate'
          , 'EffectiveDate'
          , 'ExpirationDate'
          , 'ModificationDate'
          , 'Type'
          , 'Format'
          , 'Identifier'
          , 'Language'
          , 'Rights'
          , 'getMetadataHeaders'
          )
        , ( 'Owner','Manager','Reviewer' )
        ),
        ( 'Modify portal content'
        , ( 'editMetadata'
          , 'setTitle'
          , 'setSubject'
          , 'setDescription'
          , 'setContributors'
          , 'setEffectiveDate'
          , 'setExpirationDate'
          , 'setFormat'
          , 'setLanguage'
          , 'setRights'
          )
        ),
    )

    def __init__( self
                , title=''
                , subject=()
                , description=''
                , contributors=()
                , effective_date=None
                , expiration_date=None
                , format='text/html'
                , language='en-US'
                , rights=''
            ):
            self.creation_date = DateTime()
            self.editMetadata( title
                             , subject
                             , description
                             , contributors
                             , effective_date
                             , expiration_date
                             , format
                             , language
                             , rights
                             )

    #
    #  DublinCore interface query methods
    #
    def Title( self ):
        "Dublin Core element - resource name"
        return self.title

    def Creator( self ):
        # XXX: fixme using 'portal_membership' -- should iterate over
        #       *all* owners
        "Dublin Core element - resource creator"
        owner = self.getOwner()
        if hasattr( owner, 'getUserName' ):
            return owner.getUserName()
        return 'No owner'

    def Subject( self ):
        "Dublin Core element - resource keywords"
        return self.subject

    def Publisher( self ):
        "Dublin Core element - resource publisher"
        # XXX: fixme using 'portal_metadata'
        return 'No publisher'

    def Description( self ):
        "Dublin Core element - resource summary"
        return self.description

    def Contributors( self ):
        "Dublin Core element - additional contributors to resource"
        # XXX: fixme
        return self.contributors
    
    def Date( self ):
        "Dublin Core element - default date"
        # Return effective_date if set, modification date otherwise
        date = getattr(self, 'effective_date', None )
        if date is None:
            date = self.bobobase_modification_time()
        return date.ISO()
    
    def CreationDate( self ):
        """
            Dublin Core element - date resource created.
        """
        return self.creation_date.ISO()
    
    def EffectiveDate( self ):
        """
            Dublin Core element - date resource becomes effective.
        """
        return self.effective_date and self.effective_date.ISO() or 'None'
    
    def ExpirationDate( self ):
        """
            Dublin Core element - date resource expires.
        """
        return self.expiration_date and self.expiration_date.ISO() or 'None'
    
    def ModificationDate( self ):
        """
            Dublin Core element - date resource last modified.
        """
        return self.bobobase_modification_time().ISO()

    def Type( self ):
        "Dublin Core element - Object type"
        if hasattr(aq_base(self), 'getTypeInfo'):
            ti = self.getTypeInfo()
            if ti is not None:
                return ti.Type()
        return self.meta_type

    def Format( self ):
        """
            Dublin Core element - resource format
        """
        return self.format

    def Identifier( self ):
        "Dublin Core element - Object ID"
        # XXX: fixme using 'portal_metadata' (we need to prepend the
        #      right prefix to self.getPhysicalPath().
        return self.absolute_url()

    def Language( self ):
        """
            Dublin Core element - resource language
        """
        return self.language

    def Rights( self ):
        """
            Dublin Core element - resource copyright
        """
        return self.rights

    #
    #  DublinCore utility methods
    #
    def isEffective( self, date ):
        """
            Is the date within the resource's effective range?
        """
        pastEffective = ( self.effective_date is None
                       or self.effective_date <= date )
        beforeExpiration = ( self.expiration_date is None
                          or self.expiration_date >= date )
        return pastEffective and beforeExpiration

    #
    #  CatalogableDublinCore methods
    #
    def created( self ):
        """
            Dublin Core element - date resource created,
              returned as DateTime.
        """
        return self.creation_date
    
    __FLOOR_DATE = DateTime( 1000, 0 ) # alwasy effective

    def effective( self ):
        """
            Dublin Core element - date resource becomes effective,
              returned as DateTime.
        """
        marker = []
        date = getattr( self, 'effective_date', marker )
        if date is marker:
            date = getattr( self, 'creation_date', None )
        return date is None and self.__FLOOR_DATE or date
    
    __CEILING_DATE = DateTime( 9999, 0 ) # never expires

    def expires( self ):
        """
            Dublin Core element - date resource expires,
              returned as DateTime.
        """
        date = getattr( self, 'expiration_date', None )
        return date is None and self.__CEILING_DATE or date
    
    def modified( self ):
        """
            Dublin Core element - date resource last modified,
              returned as DateTime.
        """
        return self.bobobase_modification_time()

    #
    #  MutableDublinCore methods
    #
    def _datify( self, attrib ):
        if attrib == 'None':
            attrib = None
        elif not isinstance( attrib, DateTime ):
            if attrib is not None:
                attrib = DateTime( attrib )
        return attrib

    def setTitle( self, title ):
        "Dublin Core element - resource name"
        self.title = title

    def setSubject( self, subject ):
        "Dublin Core element - resource keywords"
        self.subject = tuplize( 'subject', subject )

    def setDescription( self, description ):
        "Dublin Core element - resource summary"
        self.description = description

    def setContributors( self, contributors ):
        "Dublin Core element - additional contributors to resource"
        # XXX: fixme
        self.contributors = tuplize( 'contributors', contributors )

    def setEffectiveDate( self, effective_date ):
        """
            Dublin Core element - date resource becomes effective.
        """
        self.effective_date = self._datify( effective_date )
    
    def setExpirationDate( self, expiration_date ):
        """
            Dublin Core element - date resource expires.
        """
        self.expiration_date = self._datify( expiration_date )
    
    def setFormat( self, format ):
        """
            Dublin Core element - resource format
        """
        self.format = format

    def setLanguage( self, language ):
        """
            Dublin Core element - resource language
        """
        self.language = language

    def setRights( self, rights ):
        """
            Dublin Core element - resource copyright
        """
        self.rights = rights

    def getMetadataHeaders( self ):
        """
            Return RFC-822-style headers.
        """
        hdrlist = []
        hdrlist.append( ( 'Title', self.Title() ) )
        hdrlist.append( ( 'Subject', string.join( self.Subject() ) ) )
        hdrlist.append( ( 'Publisher', self.Publisher() ) )
        hdrlist.append( ( 'Description', self.Description() ) )
        hdrlist.append( ( 'Contributors', string.join(
            self.Contributors() ) ) )
        hdrlist.append( ( 'Effective_date', self.EffectiveDate() ) )
        hdrlist.append( ( 'Expiration_date', self.ExpirationDate() ) )
        hdrlist.append( ( 'Type', self.Type() ) )
        hdrlist.append( ( 'Format', self.Format() ) )
        hdrlist.append( ( 'Language', self.Language() ) )
        hdrlist.append( ( 'Rights', self.Rights() ) )
        return hdrlist

    #
    #  Management tab methods
    #

    def editMetadata( self
                    , title=''
                    , subject=()
                    , description=''
                    , contributors=()
                    , effective_date=None
                    , expiration_date=None
                    , format='text/html'
                    , language='en-US'
                    , rights=''
                    ):
        """
            Update the editable metadata for this resource.
        """
        self.setTitle( title )
        self.setSubject( subject )
        self.setDescription( description )
        self.setContributors( contributors )
        self.setEffectiveDate( effective_date )
        self.setExpirationDate( expiration_date )
        self.setFormat( format )
        self.setLanguage( language )
        self.setRights( rights )

    editMetadata = WorkflowAction(editMetadata)


default__class_init__(DefaultDublinCoreImpl)
