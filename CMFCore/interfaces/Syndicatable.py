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
"""\
Declare interface for synContentValues 
"""
import Interface

class Syndicatable(Interface.Base):
    """\
    Returns back a list of objects which implements the DublinCore.
    """

    def synContentValues(self):
        """
        Returns a list of results which is to be Syndicated.  For example, the normal call
        contentValues (on PortalFolders) returns a list of subObjects of the current object
        (i.e. objectValues with filtering applied).  For the case of a Topic, one would 
        return a sequence of objects from a catalog query, not the subObjects of the Topic.
        What is returned must implement the DublinCore.
        """
