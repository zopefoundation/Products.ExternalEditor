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

"""CMFDefault portal_membership tool.

$Id$
"""
__version__='$Revision$'[11:-2]


from Products.CMFCore.utils import _getAuthenticatedUser, _checkPermission
from Products.CMFCore.utils import getToolByName
import Products.CMFCore.MembershipTool
from Products.CMFCore.PortalFolder import manage_addPortalFolder
import Document

from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from Products.CMFCore.CMFCorePermissions import View, AccessContentsInformation
from Products.CMFCore.CMFCorePermissions import ListPortalMembers
from Products.CMFCore.CMFCorePermissions import ManagePortal
from utils import _dtmldir

default_member_content = '''Default page for %s

  This is the default document created for you when 
  you joined this community.

  To change the content just select "Edit"
  in the Tool Box on the left.
'''


class MembershipTool ( Products.CMFCore.MembershipTool.MembershipTool ):
    """
    """

    meta_type = 'Default Membership Tool'


    security = ClassSecurityInfo()

    #
    #   ZMI methods
    #
    security.declareProtected( ManagePortal, 'manage_overview' )
    manage_overview = DTMLFile( 'explainMembershipTool', _dtmldir )

    #
    #   'portal_membership' interface methods
    #
    security.declareProtected( ListPortalMembers, 'getRoster' )
    def getRoster(self):
        '''
        Return a list of mappings corresponding to those users who have
        made themselves "listed".  If Manager, return a list of all
        usernames.  The mapping contains the id and listed variables.
        '''
        isManager = _checkPermission('Manage portal', self)
        roster = []
        for member in self.listMembers():
            if isManager or member.listed:
                roster.append({'id':member.getUserName(),
                               'listed':member.listed})
        return roster

    def addMember(self, id, password, roles, domains, properties=None):
        '''Adds a new member to the user folder.  Security checks will have
        already been performed.  Called by portal_registration.
        '''
        Products.CMFCore.MembershipTool.MembershipTool.addMember( self
                                                                , id
                                                                , password
                                                                , roles
                                                                , domains
                                                                , properties
                                                                )

        self.createMemberarea(id)


    security.declareProtected(ManagePortal, 'createMemberarea')
    def createMemberarea(self, member_id):
        """
        create a member area
        """
        parent = self.aq_inner.aq_parent
        members =  getattr(parent, 'Members', None)

        if members is not None and not hasattr(members, member_id):
            f_title = "%s's Home" % member_id
            members.manage_addPortalFolder( id=member_id, title=f_title )
            f=getattr(members, member_id)
 
            # Grant ownership to Member
            acl_users = self.__getPUS()
            user = acl_users.getUser(member_id).__of__(acl_users)
            f.changeOwnership(user)
            f.manage_setLocalRoles(member_id, ['Owner'])
 
            # Create Member's home page.
            # default_member_content ought to be configurable per
            # instance of MembershipTool.
            Document.addDocument( f
                                , 'index_html'
                                , member_id+"'s Home"
                                , member_id+"'s front page"
                                , "structured-text"
                                , (default_member_content % member_id)
                                )
 
            f.index_html._setPortalTypeName( 'Document' )

            # Overcome an apparent catalog bug.
            f.index_html.reindexObject()
            

    def getHomeFolder(self, id=None, verifyPermission=0):
        """Returns a member's home folder object."""
        if id is None:
            member = self.getAuthenticatedMember()
            if not hasattr(member, 'getMemberId'):
                return None
            id = member.getMemberId()
        if hasattr(self, 'Members'):
            try:
                folder = self.Members[id]
                if verifyPermission and not _checkPermission('View', folder):
                    # Don't return the folder if the user can't get to it.
                    return None
                return folder
            except KeyError: pass
        return None
        
    def getHomeUrl(self, id=None, verifyPermission=0):
        """Returns the URL to a member's home folder."""
        home = self.getHomeFolder(id, verifyPermission)
        if home is not None:
            return home.absolute_url()
        else:
            return None

    security.declarePrivate( 'listActions' )
    def listActions(self, info):
        '''Lists actions available to the user.'''
        user_actions = None

        if not info.isAnonymous:
            home_folder = self.getHomeFolder()
            homeUrl = self.getHomeUrl()
            if homeUrl is not None:
                content_url = info.content_url
                user_actions = (
                    {'name': 'Add to Favorites',
                     'url': ( content_url + '/addtoFavorites' ),
                     'permissions' : [],
                     'category': 'user'},
                    {'name': 'My Stuff',
                     'url': homeUrl + '/folder_contents',
                     'permissions': [],
                     'category': 'user'},
                    )

                if hasattr( home_folder, 'Favorites' ):
                    added_actions = (
                      {'name': 'My Favorites',
                       'url' : homeUrl + '/Favorites/folder_contents',
                       'permissions': [],
                       'category': 'user'},) 
                    
                    user_actions = added_actions + user_actions

        return user_actions


InitializeClass(MembershipTool)
