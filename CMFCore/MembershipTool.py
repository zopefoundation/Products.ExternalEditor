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

"""Basic membership tool.
$Id$
"""
__version__='$Revision$'[11:-2]


from utils import UniqueObject, _getAuthenticatedUser, _checkPermission
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass, HTMLFile, MessageDialog, \
     PersistentMapping
from AccessControl.User import nobody
from AccessControl import ClassSecurityInfo
from CMFCorePermissions import ManagePortal
import CMFCorePermissions

default_member_content = '''Default page for %s
 
  This is the default document created for you when
  you joined this community.
 
  To change the content just select "Edit"
  in the Tool Box on the left.
'''

class MembershipTool (UniqueObject, SimpleItem):
    # This tool accesses member data through an acl_users object.
    # It can be replaced with something that accesses member data in
    # a different way.
    id = 'portal_membership'
    meta_type = 'CMF Membership Tool'

    security = ClassSecurityInfo()

    manage_options=(
        ({ 'label' : 'Role Mapping', 'action' : 'manage_mapRoles' },) +
        SimpleItem.manage_options
        )
 
    security.declareProtected(ManagePortal, 'manage_mapRoles')
    manage_mapRoles = HTMLFile('dtml/membershipRolemapping', globals())
 
    security.declarePublic('getAuthenticatedMember')
    def getAuthenticatedMember(self):
        '''
        Returns the currently authenticated member object
        or the Anonymous User.  Never returns None.
        '''
        u = _getAuthenticatedUser(self)
        if u is None:
            u = nobody
        return self.wrapUser(u)

    security.declarePrivate('wrapUser')
    def wrapUser(self, u, wrap_anon=0):
        '''
        Sets up the correct acquisition wrappers for a user
        object and provides an opportunity for a portal_memberdata
        tool to retrieve and store member data independently of
        the user object.
        '''
        b = getattr(u, 'aq_base', None)
        if b is None:
            # u isn't wrapped at all.  Wrap it in self.acl_users.
            b = u
            u = u.__of__(self.acl_users)
        if (b is nobody and not wrap_anon) or hasattr(b, 'getMemberId'):
            # This user is either not recognized by acl_users or it is
            # already registered with something that implements the 
            # member data tool at least partially.
            return u
        
        parent = self.aq_inner.aq_parent
        base = getattr(parent, 'aq_base', None)
        if hasattr(base, 'portal_memberdata'):
            # Apply any role mapping if we have it
            if hasattr(self, 'role_map'):
                for portal_role in self.role_map.keys():
                    if (self.role_map.get(portal_role) in u.roles and
                            portal_role not in u.roles):
                        u.roles.append(portal_role)

            # Get portal_memberdata to do the wrapping.
            md = parent.portal_memberdata
            try:
                portal_user = md.wrapUser(u)

                # Check for the member area creation flag and
                # take appropriate (non-) action
                if getattr(self, 'memberareaCreationFlag', 0) != 0:
                    if self.getHomeUrl(portal_user.id) is None:
                        self.createMemberarea(portal_user.id)

                return portal_user

            except:
                # DEBUGGING CODE
                import traceback
                traceback.print_exc()
                pass
        # Failed.
        return u

    security.declareProtected(ManagePortal, 'getPortalRoles')
    def getPortalRoles(self):
        """
        Return all local roles defined by the portal itself,
        which means roles that are useful and understood 
        by the portal object
        """
        parent = self.aq_inner.aq_parent
        roles = list(parent.__ac_roles__)

        # This is *not* a local role in the portal but used by it
        roles.append('Manager')

        return roles

    security.declareProtected(ManagePortal, 'setRoleMapping')
    def setRoleMapping(self, portal_role, userfolder_role):
        """
        set the mapping of roles between roles understood by 
        the portal and roles coming from outside user sources
        """
        if not hasattr(self, 'role_map'): self.role_map = PersistentMapping()

        if len(userfolder_role) < 1:
            del self.role_map[portal_role]
        else:
            self.role_map[portal_role] = userfolder_role

        return MessageDialog(
               title  ='Mapping updated',
               message='The Role mappings have been updated',
               action ='manage_mapRoles')

    security.declareProtected(ManagePortal, 'getMappedRole')
    def getMappedRole(self, portal_role):
        """
        returns a role name if the portal role is mapped to
        something else or an empty string if it is not
        """
        if hasattr(self, 'role_map'):
            return self.role_map.get(portal_role, '')
        else:
            return ''

    security.declareProtected(ManagePortal, 'getMemberareaCreationFlag')
    def getMemberareaCreationFlag(self):
        """
        Returns the flag indicating whether the membership tool
        will create a member area if an authenticated user from
        an underlying user folder logs in first without going 
        through the join process
        """
        if not hasattr(self, 'memberareaCreationFlag'):
            self.memberareaCreationFlag = 0

        return self.memberareaCreationFlag

    security.declareProtected(ManagePortal, 'setMemberareaCreationFlag')
    def setMemberareaCreationFlag(self):
        """
        sets the flag indicating whether the membership tool
        will create a member area if an authenticated user from
        an underlying user folder logs in first without going
        through the join process
        """
        if not hasattr(self, 'memberareaCreationFlag'):
            self.memberareaCreationFlag = 0

        if self.memberareaCreationFlag == 0:
            self.memberareaCreationFlag = 1
        else:
            self.memberareaCreationFlag = 0

        return MessageDialog(
               title  ='Member area creation flag changed',
               message='Member area creation flag has been updated',
               action ='manage_mapRoles')

    security.declareProtected(ManagePortal, 'createMemberarea')
    def createMemberarea(self, member_id):
        """
        create a member area
        """
        parent = self.aq_inner.aq_parent
        members =  getattr(parent, 'Members', None)
        if members is not None:
            members.manage_addPortalFolder(member_id)
            f=getattr(members, member_id)
 
            f.manage_permission(CMFCorePermissions.View,
                                ['Owner','Manager','Reviewer'], 0)
            f.manage_permission(CMFCorePermissions.AccessContentsInformation,
                                ['Owner','Manager','Reviewer'], 0)  


    security.declarePublic('isAnonymousUser')
    def isAnonymousUser(self):
        '''
        Returns 1 if the user is not logged in.
        '''
        u = _getAuthenticatedUser(self)
        if u is None or u.getUserName() == 'Anonymous User':
            return 1
        return 0

    security.declarePublic('checkPermission')
    def checkPermission(self, permissionName, object, subobjectName=None):
        '''
        Checks whether the current user has the given permission on
        the given object or subobject.
        '''
        if subobjectName is not None:
            object = getattr(object, subobjectName)
        return _checkPermission(permissionName, object)

    security.declarePublic('credentialsChanged')
    def credentialsChanged(self, password):
        '''
        Notifies the authentication mechanism that this user has changed
        passwords.  This can be used to update the authentication cookie.
        Note that this call should *not* cause any change at all to user
        databases.
        '''
        if not self.isAnonymousUser():
            acl_users = self.acl_users
            user = _getAuthenticatedUser(self)
            id = user.getUserName()
            if hasattr(acl_users.aq_base, 'credentialsChanged'):
                # Use an interface provided by LoginManager.
                acl_users.credentialsChanged(user, id, password)
            else:
                req = self.REQUEST
                p = getattr(req, '_credentials_changed_path', None)
                if p is not None:
                    # Use an interface provided by CookieCrumbler.
                    change = self.restrictedTraverse(p)
                    change(user, id, password)

    security.declareProtected(ManagePortal, 'getMemberById')
    def getMemberById(self, id):
        '''
        Returns the given member.
        '''
        u = self.acl_users.getUser(id)
        if u is not None:
            u = self.wrapUser(u)
        return u

    def __getPUS(self):
        # Gets something we can call getUsers() and getUserNames() on.
        acl_users = self.acl_users
        if hasattr(acl_users, 'getUsers'):
            return acl_users
        else:
            # This hack works around the absence of getUsers() in LoginManager.
            # Gets the PersistentUserSource object that stores our users
            for us in acl_users.UserSourcesGroup.objectValues():
                if us.meta_type == 'Persistent User Source':
                    return us.__of__(acl_users)

    security.declareProtected(ManagePortal, 'listMemberIds')
    def listMemberIds(self):
        '''Lists the ids of all members.  This may eventually be
        replaced with a set of methods for querying pieces of the
        list rather than the entire list at once.
        '''
        return self.__getPUS().getUserNames()
    
    security.declareProtected(ManagePortal, 'listMembers')
    def listMembers(self):
        '''Gets the list of all members.
        '''
        return map(self.wrapUser, self.__getPUS().getUsers())

    security.declarePrivate('addMember')
    def addMember(self, id, password, roles, domains):
        '''Adds a new member to the user folder.  Security checks will have
        already been performed.  Called by portal_registration.
        '''
        acl_users = self.acl_users
        if hasattr(acl_users, '_addUser'):
            acl_users._addUser(id, password, password, roles, domains)
        else:
            # The acl_users folder is a LoginManager.  Search for a UserSource
            # with the needed support.
            for source in acl_users.UserSourcesGroup.objectValues():
                if hasattr(source, 'addUser'):
                    source.__of__(self).addUser(id, password, roles, domains)
                    return
            raise "Can't add Member", "No supported UserSources"

    security.declarePrivate('listActions')
    def listActions(self, info):
        return None

    security.declarePublic('getHomeFolder')
    def getHomeFolder(self, id=None, verifyPermission=0):
        """Returns a member's home folder object or None.
        Set verifyPermission to 1 to return None when the user
        doesn't have the View permission on the folder.
        """
        return None
        
    security.declarePublic('getHomeUrl')
    def getHomeUrl(self, id=None, verifyPermission=0):
        """Returns the URL to a member's home folder or None.
        Set verifyPermission to 1 to return None when the user
        doesn't have the View permission on the folder.
        """
        return None


InitializeClass(MembershipTool)
