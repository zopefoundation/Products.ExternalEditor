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
""" Metadata registration tool interface.

$Id$
"""

from Interface import Attribute
from Interface import Interface


class portal_metadata(Interface):
    """
        CMF metadata policies interface.
    """
    id = Attribute('id', 'Must be set to "portal_metadata"')

    #
    #   Site-wide queries.
    #
    def getFullName(userid):

        """ Convert an internal userid to a "formal" name
        
        o Conversion occurs if possible, perhaps using the
          'portal_membership' tool.

        o Used to map userid's for Creator, Contributor DCMI queries.
        """

    def getPublisher():

        """ Return the "formal" name of the publisher of the portal.
        """

    #
    #   Content-specific queries.
    #
    def listAllowedVocabulary( element, content=None, content_type=None ):

        """ List the allowed values of a given DCMI element.

        o If 'content_type' is passed, include only values allowed for
          that type.

        o Else if 'content' is passed, include only values allowed for
          its type.

        o Else include all known values.
        """

    def listAllowedSubjects(content=None):

        """ List the allowed values of the 'Subject' DCMI element.

        o 'Subject' elements should be keywords categorizing their resource.

        o Return only values appropriate for content's type, or all 
          known values if None is passed.

        o Deprecated;  please use 'listAllowedVocabulary' instead.
        """

    def listAllowedFormats(content=None):

        """ List the allowed values of the 'Format' DCMI element.

        o These items should be usable as HTTP 'Content-type' values.

        o Return only values appropriate for content's type, or all
          known values if None is passed.

        o Deprecated;  please use 'listAllowedVocabulary' instead.
        """

    def listAllowedLanguages(content=None):

        """ List the allowed values of the 'Language' DCMI element.

        o 'Language' element values should be suitable for generating
          HTTP headers.

        o Return only values appropriate for content's type, or all
          known values if None is passed.

        o Deprecated;  please use 'listAllowedVocabulary' instead.
        """

    def listAllowedRights(content=None):

        """ List the allowed values of the 'Rights' DCMI element.

        o The 'Rights' element describes copyright or other IP
          declarations pertaining to a resource.

        o Return only values appropriate for content's type, or all
          known values if None is passed.

        o Deprecated;  please use 'listAllowedVocabulary' instead.
        """

    #
    #   Validation policy hooks.
    #
    def setInitialMetadata(content):

        """ Set initial values for content metatdata.
        
        o Tool should suppl any site-specific defaults.
        """

    def validateMetadata(content):

        """ Enforce portal-wide policies about DCI
        
        o E.g., tool may require non-empty title/description, etc.
        
        o Should be called by the skin methods immediately after saving
          changes to the metadata of an object (or at workflow transitions).
        """

    #
    #   Content lookups
    #
    def getContentMetadata(content, element):

        """ Return the given metadata element for 'content'.

        o Allows indirection of the storage / format of metadata through
          the tool.
        """

    def setContentMetadata(content, element, value):

        """ Update the given metadata element for 'content'.

        o Allows indirection of the storage / format of metadata through
          the tool.
        """
