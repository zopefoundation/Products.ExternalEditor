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

"""Basic membership tool.
$Id$
"""
__version__='$Revision$'[11:-2]

from string import find
from utils import UniqueObject, _getAuthenticatedUser, _checkPermission
from utils import getToolByName, _dtmldir
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass, DTMLFile, MessageDialog, \
     PersistentMapping
from AccessControl.User import nobody
from AccessControl import ClassSecurityInfo
from CMFCorePermissions import ManagePortal
import CMFCorePermissions
from ActionProviderBase import ActionProviderBase
import Acquisition

default_member_content = '''Default page for %s
 
  This is the default document created for you when
  you joined this community.
 
  To change the content just select "Edit"
  in the Tool Box on the left.
'''

class MembershipTool (UniqueObject, SimpleItem, ActionProviderBase):
    # This tool accesses member data through an acl_users object.
    # It can be replaced with something that accesses member data in
    # a different way.
    id = 'portal_membership'
    meta_type = 'CMF Membership Tool'
    _actions = []
    security = ClassSecurityInfo()

    manage_options=( ({ 'label' : 'Configuration'
                     , 'action' : 'manage_mapRoles'
                     },) +
                     ActionProviderBase.manage_options + 
                   ( { 'label' : 'Overview'
                     , 'action' : 'manage_overview'
                     },
                   ) + SimpleItem.manage_options)

    #
    #   ZMI methods
    #
    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'manage_overview' )
    manage_overview = DTMLFile( 'explainMembershipTool', _dtmldir )
 
    #
    #   'portal_membership' interface methods
    #
    security.declareProtected(ManagePortal, 'manage_mapRoles')
    manage_mapRoles = DTMLFile('membershipRolemapping', _dtmldir )
 
    security.declareProtected(CMFCorePermissions.SetOwnPassword, 'setPassword')
    def setPassword(self, password, domains=None):
        '''Allows the authenticated member to set his/her own password.
        '''
        registration = getToolByName(self, 'portal_registration', None)
        if not self.isAnonymousUser():
            member = self.getAuthenticatedMember()
            if registration:
                failMessage = registration.testPasswordValidity(password)
                if failMessage is not None:
                    raise 'Bad Request', failMessage
            member.setSecurityProfile(password=password, domains=domains)
        else:
            raise 'Bad Request', 'Not logged in.'

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
            md = getToolByName(parent, 'portal_memberdata')
            try:
                portal_user = md.wrapUser(u)

                # Check for the member area creation flag and
                # take appropriate (non-) action
                if getattr(self, 'memberareaCreationFlag', 0) != 0:
                    if self.getHomeUrl(portal_user.getId()) is None:
                        self.createMemberarea(portal_user.getId())

                return portal_user

            except:
                from zLOG import LOG, ERROR
                import sys
                type,value,tb = sys.exc_info()
                try:
                    LOG('CMFCore.MembershipTool',
                        ERROR,
                        'Error during wrapUser:',
                        "\nType:%s\nValue:%s\n" % (type,value))
                finally:
                    tb = None       # Avoid leaking frame
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
        roles.append('Owner')

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
        user = self.acl_users.getUser( member_id ).__of__( self.acl_users )
        
        if members is not None and user is not None:
            f_title = "%s's Home" % member_id
            members.manage_addPortalFolder( id=member_id, title=f_title )
            f=getattr(members, member_id)
 
            f.manage_permission(CMFCorePermissions.View,
                                ['Owner','Manager','Reviewer'], 0)
            f.manage_permission(CMFCorePermissions.AccessContentsInformation,
                                ['Owner','Manager','Reviewer'], 0)  

            # Grant ownership to Member
            try: f.changeOwnership(user)
            except AttributeError: pass  # Zope 2.1.x compatibility
            f.manage_setLocalRoles(member_id, ['Owner'])


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

    security.declareProtected(CMFCorePermissions.View, 'searchMembers')
    def searchMembers( self, search_param, search_term ):
        """ Search the membership """
        md = getToolByName( self, 'portal_memberdata' )

        return md.searchMemberDataContents( search_param, search_term )

        
    security.declareProtected(CMFCorePermissions.View, 'getCandidateLocalRoles')
    def getCandidateLocalRoles( self, obj ):
        """ What local roles can I assign? """
        member = self.getAuthenticatedMember()

        if 'Manager' in member.getRoles():
            return self.getPortalRoles()
        else:
            member_roles = list( member.getRolesInContext( obj ) )
            del member_roles[member_roles.index( 'Member')]

        return tuple( member_roles )

    security.declareProtected(CMFCorePermissions.View, 
                                'setLocalRoles')
    def setLocalRoles( self, obj, member_ids, member_role ):
        """ Set local roles on an item """
        member = self.getAuthenticatedMember()
        my_roles = member.getRolesInContext( obj )
        
        if 'Manager' in my_roles or member_role in my_roles:
            for member_id in member_ids:
                roles = list(obj.get_local_roles_for_userid( userid=member_id ))
            
                if member_role not in roles:
                    roles.append( member_role )
                    obj.manage_setLocalRoles( member_id, roles )

    security.declareProtected( CMFCorePermissions.View,
                                    'deleteLocalRoles' )
    def deleteLocalRoles( self, obj, member_ids ):
        """ Delete local roles for members member_ids """
        member = self.getAuthenticatedMember()
        my_roles = member.getRolesInContext( obj )

        if 'Manager' in my_roles or 'Owner' in my_roles:
            obj.manage_delLocalRoles( userids=member_ids )

    security.declarePrivate('addMember')
    def addMember(self, id, password, roles, domains, properties=None):
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
            raise "Can't add Member", "No supported UserSources"

        if properties is not None:
            membership = getToolByName(self, 'portal_membership')
            member = membership.getMemberById(id)
            member.setMemberProperties(properties)


    security.declarePrivate('listActions')
    def listActions(self, info=None):
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
