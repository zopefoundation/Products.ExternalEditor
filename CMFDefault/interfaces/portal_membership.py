##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Extended membership tool interface.

$Id$
"""

from Products.CMFCore.interfaces.portal_membership \
        import portal_membership as BaseInterface


class portal_membership(BaseInterface):
    """ Declare product-specific APIs for CMFDefault's tool.
    """

    def setMembersFolderById(id=''):
        """ Set the members folder object by its id.

        The members folder has to be in the same container as the membership
        tool. id is the id of an existing folder. If id is empty, member areas
        are disabled.

        Permission -- Manage portal
        """
