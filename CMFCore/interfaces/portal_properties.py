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
""" Properties tool interface.

$Id$
"""

from Interface import Attribute
try:
    from Interface import Interface
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import Base as Interface


class portal_properties(Interface):
    """ CMF Properties Tool interface.

    This interface provides access to "portal-wide" properties.
    """
    id = Attribute('id', 'Must be set to "portal_properties"')

    def editProperties(props):
        """ Change portal settings.

        Permission -- Manage portal
        """

    def title():
        """ Get portal title.

        Returns -- String
        """

    def smtp_server():
        """ Get local SMTP server.

        Returns -- String
        """
