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

class Contentish(Interface.Base):
    """
    General interface for "contentish" items.

    These methods need to be implemented by any class that wants to be a 
    first-class citizen in the Portal Content world.
    
    PortalContent implements this interface.
    """
    
    def getIcon(relative_to_portal=0):
        """
        This method returns the path to an object's icon. It is used 
        in the folder_contents view to generate an appropriate icon 
        for the items found in the folder.

        If the content item does not define an attribute named "icon"
        this method will return the path "/misc_/dtmldoc.gif", which is 
        the icon used for DTML Documents.

        If 'relative_to_portal' is true, return only the portion of
        the icon's URL which finds it "within" the portal;  otherwise,
        return it as an absolute URL.
        """

    def listActions():
        """
        listAction returns a tuple containing dictionaries that describe 
        a specific "action". An "action" shows up as a link in the PTK
        toolbox which has a title, a URL, a category (the action can be 
        applied at the object- or user-level or everywhere) and the 
        permissions needed to show the action link.

        listActions can be used to provide actions specific to your 
        content object.
        """

    def SearchableText():
        """
        SearchableText is called to provide the Catalog with textual 
        information about your object. It is a string usually generated 
        by concatenating the string attributes of your content class. This
        string can then be used by the catalog to index your document and
        make it findable through the catalog.
        """

    def allowedRolesAndUsers(permission='View'):
        """
        Return a list of roles and users with View permission.
        Used by PortalCatalog to filter out items you're not allowed to see.
        """
