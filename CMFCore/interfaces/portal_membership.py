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

"""Membership tool interface description.
$Id$
"""
__version__='$Revision$'[11:-2]


from Interface import Attribute, Base

class portal_membership(Base):
    '''Deals with the details of how and where to store and retrieve
    members and their member folders.
    '''
    id = Attribute('id', 'Must be set to "portal_membership"')

    #getAuthenticatedMember__roles__ = None  # Allow all.
    def getAuthenticatedMember():
        '''
        Returns the currently authenticated member object
        or the Anonymous User.
        '''

    #isAnonymousUser__roles__ = None  # Allow all.
    def isAnonymousUser():
        '''
        Returns 1 if the user is not logged in.
        '''

    #checkPermission__roles__ = None  # Allow all.
    def checkPermission(permissionName, object, subobjectName=None):
        '''
        Checks whether the current user has the given permission on
        the given object or subobject.
        '''

    #credentialsChanged__roles__ = None  # Allow all.
    def credentialsChanged(password):
        '''
        Notifies the authentication mechanism that this user has changed
        passwords.  This can be used to update the authentication cookie.
        Note that this call should *not* cause any change at all to user
        databases.
        '''

    # getHomeFolder__roles__ = None # Anonymous permission
    def getHomeFolder(id=None, verifyPermission=0):
        """Returns a member's home folder object or None.
        Set verifyPermission to 1 to return None when the user
        doesn't have the View permission on the folder.
        """
        
    # getHomeUrl__roles__ = None # Anonymous permission
    def getHomeUrl(id=None, verifyPermission=0):
        """Returns the URL to a member's home folder or None.
        Set verifyPermission to 1 to return None when the user
        doesn't have the View permission on the folder.
        """

    # permission: 'Manage portal'
    def getMemberById(id):
        '''
        Returns the given member.
        '''

    # permission: 'Manage portal'
    def listMemberIds():
        '''Lists the ids of all members.  This may eventually be
        replaced with a set of methods for querying pieces of the
        list rather than the entire list at once.
        '''
    
    # permission: 'Manage portal'
    def listMembers():
        '''Gets the list of all members.
        '''

    #addMember__roles__ = ()  # No permission.
    def addMember(id, password, roles, domains):
        '''Adds a new member to the user folder.  Security checks will have
        already been performed.  Called by portal_registration.
        '''

    # getPortalRoles__roles__ = ()  # Private
    def getPortalRoles():
        """
        Return all local roles defined by the portal itself,
        which means roles that are useful and understood
        by the portal object
        """

    # setRoleMapping__roles__ = ()  # Private
    def setRoleMapping(portal_role, userfolder_role):
        """
        set the mapping of roles between roles understood by
        the portal and roles coming from outside user sources
        """

    # getMappedRole__roles__ = ()  # Private
    def getMappedRole(portal_role):
        """
        returns a role name if the portal role is mapped to
        something else or an empty string if it is not
        """ 

    # getMemberareaCreationFlag__roles__ = ()  # Private
    def getMemberareaCreationFlag():
        """
        Returns the flag indicating whether the membership tool
        will create a member area if an authenticated user from
        an underlying user folder logs in first without going
        through the join process
        """ 

    # setMemberareaCreationFlag__roles__ = ()  # Private
    def setMemberareaCreationFlag():
        """
        sets the flag indicating whether the membership tool
        will create a member area if an authenticated user from
        an underlying user folder logs in first without going
        through the join process
        """

    # createMemberarea__roles__ = ()  # Private
    def createMemberarea(member_id):
        """
        create a member area, only used if members are sourced
        from an independent underlying user folder and not just 
        from the join process
        """
