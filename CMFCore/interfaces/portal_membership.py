##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
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
