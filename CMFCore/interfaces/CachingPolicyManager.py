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

"""Caching tool interface description.

$Id$
"""

from Interface import Attribute, Base

class CachingPolicyManager( Base ):
    """
        Manage HTTP cache policies for skin methods.
    """
    id = Attribute( 'id', 'Must be set to "caching_policy_manager"' )

    def getHTTPCachingHeaders( content, view_method, keywords ):
        """
            Update HTTP caching headers in REQUEST based on 'content',
            'view_method', and 'keywords'.
        """
