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
class IndexableContent:
    """
    Interface for indexing by PortalCatalog.
    
    PortalContent implements this interface.  The existing portions of
    this interface are firm.
    """

    def Title(self):
        """
        Dublin Core element - resource name
        
        Used for indexing.  By default, simply returns self.title.
        
        Return: string
        Permission: 'View'
        """

    def Creator(self):
        """
        Dublin Core element - resource creator
        
        Used for indexing, but may be used anywhere.  If there are
        multiple owners, returns only the name of the first found.
        
        Return: string
        Permission: 'View'
        """

    def Date(self):
        """
        Dublin Core element - effective date
        
        Used for indexing.  This is not necessarily the creation or
        modification date-- object can be future-dated so that they
        can automagically appear on the portal at the appropreate
        time.
        
        Return: DateTime
        Permission: 'View'
        """

    def Description(self):
        """
        Dublin Core element - summary
        
        Used for indexing.  This is typically a plain-english
        description of the contents of this particular object.
        
        Return: string
        Permission: 'View'
        """

    def Subject(self):
        """
        Dublin Core elment - Topical keywords

        This is a list of user-defined keywords.

        Return: list of strings
        """

    def SearchableText(self):
        """
        Returns a concatenation of all searchable text
        
        Used for indexing.  Probably shouldn't be used elsewhere.
        PortalContent subclasses should use this to return a
        concatenation of any text you would like the user to be able
        to search against in a standard, full-text search.
        
        Return: string
        Permission: 'View'
        """







