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
 
import string, re
from OFS.PropertyManager import PropertyManager
from DateTime.DateTime import DateTime
from Acquisition import aq_base
from Products.CMFCore.WorkflowCore import WorkflowAction
from Products.CMFCore.interfaces.DublinCore import DublinCore
from Products.CMFCore.interfaces.DublinCore import CatalogableDublinCore
from Products.CMFCore.interfaces.DublinCore import MutableDublinCore

from utils import tuplize, _dtmldir, semi_split
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions


class DefaultDublinCoreImpl( PropertyManager ):
    """
        Mix-in class which provides Dublin Core methods
    """
    __implements__ = DublinCore, CatalogableDublinCore, MutableDublinCore

    security = ClassSecurityInfo()

    def __init__( self
                , title=''
                , subject=()
                , description=''
                , contributors=()
                , effective_date=None
                , expiration_date=None
                , format='text/html'
                , language=''
                , rights=''
                ):
            self.creation_date = DateTime()
            self._editMetadata( title
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
    security.declarePublic( 'Title' )
    def Title( self ):
        "Dublin Core element - resource name"
        return self.title

    security.declarePublic( 'Creator' )
    def Creator( self ):
        # XXX: fixme using 'portal_membership' -- should iterate over
        #       *all* owners
        "Dublin Core element - resource creator"
        owner = self.getOwner()
        if hasattr( owner, 'getUserName' ):
            return owner.getUserName()
        return 'No owner'

    security.declarePublic( 'Subject' )
    def Subject( self ):
        "Dublin Core element - resource keywords"
        return self.subject

    security.declarePublic( 'Publisher' )
    def Publisher( self ):
        "Dublin Core element - resource publisher"
        # XXX: fixme using 'portal_metadata'
        return 'No publisher'

    security.declarePublic( 'Description' )
    def Description( self ):
        "Dublin Core element - resource summary"
        return self.description

    security.declarePublic( 'Contributors' )
    def Contributors( self ):
        "Dublin Core element - additional contributors to resource"
        # XXX: fixme
        return self.contributors
    
    security.declarePublic( 'Date' )
    def Date( self ):
        "Dublin Core element - default date"
        # Return effective_date if set, modification date otherwise
        date = getattr(self, 'effective_date', None )
        if date is None:
            date = self.bobobase_modification_time()
        return date.ISO()
    
    security.declarePublic( 'CreationDate' )
    def CreationDate( self ):
        """
            Dublin Core element - date resource created.
        """
        return self.creation_date.ISO()
    
    security.declarePublic( 'EffectiveDate' )
    def EffectiveDate( self ):
        """
            Dublin Core element - date resource becomes effective.
        """
        return self.effective_date and self.effective_date.ISO() or 'None'
    
    security.declarePublic( 'ExpirationDate' )
    def ExpirationDate( self ):
        """
            Dublin Core element - date resource expires.
        """
        return self.expiration_date and self.expiration_date.ISO() or 'None'
    
    security.declarePublic( 'ModificationDate' )
    def ModificationDate( self ):
        """
            Dublin Core element - date resource last modified.
        """
        return self.bobobase_modification_time().ISO()

    security.declarePublic( 'Type' )
    def Type( self ):
        "Dublin Core element - Object type"
        if hasattr(aq_base(self), 'getTypeInfo'):
            ti = self.getTypeInfo()
            if ti is not None:
                return ti.Type()
        return self.meta_type

    security.declarePublic( 'Format' )
    def Format( self ):
        """
            Dublin Core element - resource format
        """
        return self.format

    security.declarePublic( 'Identifier' )
    def Identifier( self ):
        "Dublin Core element - Object ID"
        # XXX: fixme using 'portal_metadata' (we need to prepend the
        #      right prefix to self.getPhysicalPath().
        return self.absolute_url()

    security.declarePublic( 'Language' )
    def Language( self ):
        """
            Dublin Core element - resource language
        """
        return self.language

    security.declarePublic( 'Rights' )
    def Rights( self ):
        """
            Dublin Core element - resource copyright
        """
        return self.rights

    #
    #  DublinCore utility methods
    #
    def content_type( self ):
        """
            WebDAV needs this to do the Right Thing (TM).
        """
        return self.Format()

    security.declarePublic( 'isEffective' )
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
    security.declarePublic( 'created' )
    def created( self ):
        """
            Dublin Core element - date resource created,
              returned as DateTime.
        """
        return self.creation_date
    
    __FLOOR_DATE = DateTime( 1000, 0 ) # alwasy effective

    security.declarePublic( 'effective' )
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

    security.declarePublic( 'expires' )
    def expires( self ):
        """
            Dublin Core element - date resource expires,
              returned as DateTime.
        """
        date = getattr( self, 'expiration_date', None )
        return date is None and self.__CEILING_DATE or date
    
    security.declarePublic( 'modified' )
    def modified( self ):
        """
            Dublin Core element - date resource last modified,
              returned as DateTime.
        """
        return self.bobobase_modification_time()

    security.declarePublic( 'getMetadataHeaders' )
    def getMetadataHeaders( self ):
        """
            Return RFC-822-style headers.
        """
        hdrlist = []
        hdrlist.append( ( 'Title', self.Title() ) )
        hdrlist.append( ( 'Subject', string.join( self.Subject(), ', ' ) ) )
        hdrlist.append( ( 'Publisher', self.Publisher() ) )
        hdrlist.append( ( 'Description', self.Description() ) )
        hdrlist.append( ( 'Contributors', string.join(
            self.Contributors(), '; ' ) ) )
        hdrlist.append( ( 'Effective_date', self.EffectiveDate() ) )
        hdrlist.append( ( 'Expiration_date', self.ExpirationDate() ) )
        hdrlist.append( ( 'Type', self.Type() ) )
        hdrlist.append( ( 'Format', self.Format() ) )
        hdrlist.append( ( 'Language', self.Language() ) )
        hdrlist.append( ( 'Rights', self.Rights() ) )
        return hdrlist

    #
    #  MutableDublinCore methods
    #
    security.declarePrivate( '_datify' )
    def _datify( self, attrib ):
        if attrib == 'None':
            attrib = None
        elif not isinstance( attrib, DateTime ):
            if attrib is not None:
                attrib = DateTime( attrib )
        return attrib

    security.declareProtected( CMFCorePermissions.ModifyPortalContent
                             , 'setTitle' )
    def setTitle( self, title ):
        "Dublin Core element - resource name"
        self.title = title

    security.declareProtected( CMFCorePermissions.ModifyPortalContent
                             , 'setSubject' )
    def setSubject( self, subject ):
        "Dublin Core element - resource keywords"
        self.subject = tuplize( 'subject', subject )

    security.declareProtected( CMFCorePermissions.ModifyPortalContent
                             , 'setDescription' )
    def setDescription( self, description ):
        "Dublin Core element - resource summary"
        self.description = description

    security.declareProtected( CMFCorePermissions.ModifyPortalContent
                             , 'setContributors' )
    def setContributors( self, contributors ):
        "Dublin Core element - additional contributors to resource"
        # XXX: fixme
        self.contributors = tuplize('contributors', contributors, semi_split)

    security.declareProtected( CMFCorePermissions.ModifyPortalContent
                             , 'setEffectiveDate' )
    def setEffectiveDate( self, effective_date ):
        """
            Dublin Core element - date resource becomes effective.
        """
        self.effective_date = self._datify( effective_date )
    
    security.declareProtected( CMFCorePermissions.ModifyPortalContent
                             , 'setExpirationDate' )
    def setExpirationDate( self, expiration_date ):
        """
            Dublin Core element - date resource expires.
        """
        self.expiration_date = self._datify( expiration_date )
    
    security.declareProtected( CMFCorePermissions.ModifyPortalContent
                             , 'setFormat' )
    def setFormat( self, format ):
        """
            Dublin Core element - resource format
        """
        self.format = format

    security.declareProtected( CMFCorePermissions.ModifyPortalContent
                             , 'setLanguage' )
    def setLanguage( self, language ):
        """
            Dublin Core element - resource language
        """
        self.language = language

    security.declareProtected( CMFCorePermissions.ModifyPortalContent
                             , 'setRights' )
    def setRights( self, rights ):
        """
            Dublin Core element - resource copyright
        """
        self.rights = rights

    #
    #  Management tab methods
    #

    security.declarePrivate( '_editMetadata' )
    def _editMetadata( self
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
        self.reindexObject()

    security.declareProtected( CMFCorePermissions.ModifyPortalContent
                             , 'manage_metadata' )
    manage_metadata = DTMLFile( 'zmi_metadata', _dtmldir )

    security.declareProtected( CMFCorePermissions.ModifyPortalContent
                             , 'manage_editMetadata' )
    def manage_editMetadata( self
                           , title
                           , subject
                           , description
                           , contributors
                           , effective_date
                           , expiration_date
                           , format
                           , language
                           , rights
                           , REQUEST
                           ):
        """
            Update metadata from the ZMI.
        """
        self._editMetadata( title, subject, description, contributors
                          , effective_date, expiration_date
                          , format, language, rights
                          )
        REQUEST[ 'RESPONSE' ].redirect( self.absolute_url()
                                + '/manage_metadata'
                                + '?manage_tabs_message=Metadata+updated.' )

    security.declareProtected( CMFCorePermissions.ModifyPortalContent
                             , 'editMetadata' )
    def editMetadata(self
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
        used to be:  editMetadata = WorkflowAction(_editMetadata)
        Need to add check for webDAV locked resource for TTW methods.
        """
        self.failIfLocked()
        self._editMetadata(title=title
                     , subject=subject
                     , description=description
                     , contributors=contributors
                     , effective_date=effective_date
                     , expiration_date=expiration_date
                     , format=format
                     , language=language
                     , rights=rights
                     )
InitializeClass(DefaultDublinCoreImpl)
