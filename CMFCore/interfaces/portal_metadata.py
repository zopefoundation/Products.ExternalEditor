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

"""
    Type registration tool interface description.
"""


from Interface import Attribute, Base

class portal_metadata(Base):
    """
        CMF metadata policies interface.
    """

    #
    #   Site-wide queries.
    #
    def getFullName(userid):
        """
            Convert an internal userid to a "formal" name, if
            possible, perhaps using the 'portal_membership' tool.

            Used to map userid's for Creator, Contributor DCMI
            queries.
        """

    def getPublisher():
        """
            Return the "formal" name of the publisher of the
            portal.
        """

    #
    #   Content-specific queries.
    #
    def listAllowedSubjects(content=None):
        """
            List the allowed values of the 'Subject' DCMI element
            'Subject' elements should be keywords categorizing
            their resource.

            Return only values appropriate for content's type, or
            all values if None.
        """

    def listAllowedFormats(content=None):
        """
            List the allowed values of the 'Format' DCMI element.
            These items should be usable as HTTP 'Content-type'
            values.

            Return only values appropriate for content's type, or
            all values if None.
        """

    def listAllowedLanguages(content=None):
        """
            List the allowed values of the 'Language' DCMI element.
            'Language' element values should be suitable for generating
            HTTP headers.

            Return only values appropriate for content's type, or
            all values if None.
        """

    def listAllowedRights(content=None):
        """
            List the allowed values of the 'Rights' DCMI element.
            The 'Rights' element describes copyright or other IP
            declarations pertaining to a resource.

            Return only values appropriate for content's type, or
            all values if None.
        """

    #
    #   Validation policy hooks.
    #
    def setInitialMetadata(content):
        """
            Set initial values for content metatdata, supplying
            any site-specific defaults.
        """

    def validateMetadata(content):
        """
            Enforce portal-wide policies about DCI, e.g.,
            requiring non-empty title/description, etc.  Called
            by the CMF immediately before saving changes to the
            metadata of an object.
        """
