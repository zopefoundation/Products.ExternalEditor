##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Folderish type interface.

$Id$
"""

from Interface import Interface


class Folderish(Interface):
    """ General interface for "folderish" items.
    """

    def contentItems(filter=None):
        """ List contentish and folderish sub-objects and their IDs.

        Provide a filtered view onto 'objectItems', allowing only
        PortalFolders and PortalContent-derivatives to show through.

        Permission -- Always available (not publishable)

        Returns -- List of (object ID, object) tuples
        """

    def contentIds(filter=None):
        """ List IDs of contentish and folderish sub-objects.

        Provide a filtered view onto 'objectIds', allowing only PortalFolders
        and PortalContent-derivatives to show through.

        Permission -- Always available (not publishable)

        Returns -- List of object IDs
        """

    def contentValues(filter=None):
        """ List contentish and folderish sub-objects.

        Provide a filtered view onto 'objectValues', allowing only
        PortalFolders and PortalContent-derivatives to show through.

        Permission -- Always available (not publishable)

        Returns -- List of objects
        """

    def listFolderContents(contentFilter=None):
        """ List viewable contentish and folderish sub-objects.

        Hook around 'contentValues' to let 'folder_contents' be protected.
        Duplicating skip_unauthorized behavior of dtml-in.

        Permission -- List folder contents

        Returns -- List of objects
        """
