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
""" Dynamic type interface.

$Id$
"""

try:
    from Interface import Interface
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import Base as Interface


class DynamicType(Interface):
    """ General interface for dynamic items.
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
