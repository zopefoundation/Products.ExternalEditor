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
""" Memberdata storage tool interface.

$Id$
"""

from Interface import Attribute
try:
    from Interface import Interface
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import Base as Interface


class portal_memberdata(Interface):
    '''A helper for portal_membership that transparently adds
    member data to user objects.
    '''
    id = Attribute('id', 'Must be set to "portal_memberdata"')

    ## wrapUser__roles__ = ()  # Private.
    def wrapUser(u):
        '''
        If possible, returns the Member object that corresponds
        to the given User object.
        '''
    ## getMemberDataContents__roles__ = ()  # Private.
    def getMemberDataContents():
        '''
        Returns a list containing a dictionary with information 
        about the _members BTree contents: member_count is the 
        total number of member instances stored in the memberdata-
        tool while orphan_count is the number of member instances 
        that for one reason or another are no longer in the 
        underlying acl_users user folder.
        The result is designed to be iterated over in a dtml-in
        '''

    ## pruneMemberDataContents__roles__ = ()  # Private.
    def pruneMemberDataContents():
        '''
        Compare the user IDs stored in the member data
        tool with the list in the actual underlying acl_users
        and delete anything not in acl_users
        '''

    ## searchMemberData__roles__ = ()  # Private.
    def searchMemberData(search_param, search_term, attributes=()):
        '''
        Returns a sequence of dictionaries containing data for members
        that match the query as expressed by search_param and search_term.
        The contents of each member data mapping can be influenced by
        passing in a sequence of desired attributes, by default the only
        data returned is the username and the email address.
        '''

class MemberData(Interface):
    """ MemberData interface.
    """

    def setProperties(properties=None, **kw):
        """ Allows the authenticated member to set his/her own properties.

        Permission -- Set own properties
        """
