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
import Interface

class DublinCore(Interface.Base):
    """
        Define which Dublin Core metadata elements are supported by the PTK,
        and the semantics therof.
    """

    def Title():
        """
            Dublin Core element - resource name

            Return type: string
            Permissions: View
        """
        
    def Creator():
        """
            Dublin Core element - resource creator

            Return the full name(s) of the author(s) of the content object.

            Return type: string
            Permission: View
        """

    def Subject():
        """
            Dublin Core element - resource keywords

            Return zero or more keywords associated with the content object.

            Return type: sequence of strings
            Permission: View
        """

    def Description():
        """
            Dublin Core element - resource summary

            Return a natural language description of this object.

            Return type: string
            Permissions: View
        """

    def Publisher():
        """
            Dublin Core element - resource publisher

            Return full formal name of the entity or person responsible
            for publishing the resource.

            Return type: string
            Permission: View
        """

    def Contributors():
        """
            Dublin Core element - resource collaborators

            Return zero or additional collaborators.

            Return type: sequence of strings
            Permission: View
        """
    
    def Date():
        """
            Dublin Core element - default date

            Return type: string, formatted 'YYYY-MM-DD H24:MN:SS TZ'
            Permissions: View
        """
    
    def CreationDate():
        """
            Dublin Core element - date resource created.

            Return type: string, formatted 'YYYY-MM-DD H24:MN:SS TZ'
            Permissions: View
        """
    
    def EffectiveDate():
        """
            Dublin Core element - date resource becomes effective.

            Return type: string, formatted 'YYYY-MM-DD H24:MN:SS TZ'
            Permissions: View
        """
    
    def ExpirationDate():
        """
            Dublin Core element - date resource expires.

            Return type: string, formatted 'YYYY-MM-DD H24:MN:SS TZ'
            Permissions: View
        """
    
    def ModificationDate():
        """
            Dublin Core element - date resource last modified.

            Return type: string, formatted 'YYYY-MM-DD H24:MN:SS TZ'
            Permissions: View
        """

    def Type():
        """
            Dublin Core element - resource type

            Return a human-readable type name for the resource
            (perhaps mapped from its Zope meta_type).

            Return type: string
            Permissions: View
        """

    def Format():
        """
            Dublin Core element - resource format

            Return the resource's MIME type (e.g., 'text/html',
            'image/png', etc.).

            Return type: string
            Permissions: View
        """

    def Identifier():
        """
            Dublin Core element - resource ID

            Returns unique ID (a URL) for the resource.

            Return type: string
            Permissions: View
        """

    def Language():
        """
            Dublin Core element - resource language

            Return the RFC language code (e.g., 'en-US', 'pt-BR')
            for the resource.

            Return type: string
            Permissions: View
        """

    def Rights():
        """
            Dublin Core element - resource copyright

            Return a string describing the intellectual property status,
            if any, of the resource.
            for the resource.

            Return type: string
            Permissions: View
        """

class CatalogableDublinCore(Interface.Base):
    """
        Provide Zope-internal date objects for cataloging purposes.
    """
    def created():
        """
            Dublin Core element - date resource created,

            Return type: DateTime
            Permissions: View
        """
    
    def effective():
        """
            Dublin Core element - date resource becomes effective,

            Return type: DateBound
            Permissions: View
        """
    
    def expires():
        """
            Dublin Core element - date resource expires,

            Return type: DateBound
            Permissions: View
        """
    
    def modified():
        """
            Dublin Core element - date resource last modified,

            Return type: DateTime
            Permissions: View
        """

class MutableDublinCore(Interface.Base):
    """
        Update interface for mutable metadata.
    """
    def setTitle(title):
        "Dublin Core element - update resource name"

    def setSubject(subject):
        "Dublin Core element - update resource keywords"

    def setDescription(description):
        "Dublin Core element - update resource summary"

    def setContributors(contributors):
        "Dublin Core element - update additional contributors to resource"

    def setEffectiveDate(effective_date):
        """ Dublin Core element - update date resource becomes effective.  """
    
    def setExpirationDate(expiration_date):
        """ Dublin Core element - update date resource expires.  """
    
    def setFormat(format):
        """ Dublin Core element - update resource format """

    def setLanguage(language):
        """ Dublin Core element - update resource language """

    def setRights(rights):
        """ Dublin Core element - update resource copyright """

