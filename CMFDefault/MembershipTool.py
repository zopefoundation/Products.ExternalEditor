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
""" CMFDefault portal_membership tool.

$Id$
"""

from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner
from Acquisition import aq_parent
from Globals import DTMLFile
from Globals import InitializeClass

from Products.CMFCore.MembershipTool import MembershipTool as BaseTool
from Products.CMFCore.PortalFolder import manage_addPortalFolder
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.ActionsTool import ActionInformation as AI
from Products.CMFCore.Expression import Expression
from Products.CMFCore.CMFCorePermissions import ListPortalMembers
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore.CMFCorePermissions import View

from Document import addDocument
from utils import _dtmldir

from interfaces.portal_membership \
        import portal_membership as IMembershipTool


DEFAULT_MEMBER_CONTENT = """\
Default page for %s

  This is the default document created for you when
  you joined this community.

  To change the content just select "Edit"
  in the Tool Box on the left.
"""

class MembershipTool( BaseTool ):
    """ Implement 'portal_membership' interface using "stock" policies.
    """

    __implements__ = (IMembershipTool, ActionProviderBase.__implements__)

    meta_type = 'Default Membership Tool'
    _actions = (
      AI( id='login'
        , title='Login'
        , description='Click here to Login'
        , action=Expression(text='string:${portal_url}/login_form')
        , permissions=(View,)
        , category='user'
        , condition=Expression(text='not: member')
        , visible=1
        )
    , AI( id='preferences'
        , title='Preferences'
        , description='Change your user preferences'
        , action=Expression(text='string:${portal_url}/personalize_form')
        , permissions=(View,)
        , category='user'
        , condition=Expression(text='member')
        , visible=1
        )
    , AI( id='logout'
        , title='Log out'
        , description='Click here to logout'
        , action=Expression(text='string:${portal_url}/logout')
        , permissions=(View,)
        , category='user'
        , condition=Expression(text='member')
        , visible=1
        )
    , AI( id='addFavorite'
        , title='Add to favorites'
        , description='Add this item to your favorites'
        , action=Expression(text='string:${object_url}/addtoFavorites')
        , permissions=(View,)
        , category='user'
        , condition=Expression(text= 'portal/portal_membership'
                                   + '/getHomeFolder')
        , visible=1
        )
    , AI( id='mystuff'
        , title='My stuff'
        , description='Goto your home folder'
        , action=Expression(text='string:${portal/portal_membership'
                               + '/getHomeUrl}/folder_contents')
        , permissions=(View,)
        , category='user'
        , condition=Expression( text='python: member and '
                              + 'portal.portal_membership.getHomeFolder()')
        , visible=1
        )
    , AI( id='favorites'
        , title='My favorites'
        , description='Browse your favorites'
        , action=Expression(text='string:${portal/portal_membership'
                               + '/getHomeUrl}/Favorites/folder_contents')
        , permissions=(View,)
        , category='user'
        , condition=Expression( text='python: member and '
                                   + 'hasattr(portal.portal_membership.'
                                   +  'getHomeFolder(), "Favorites")')
        , visible=1
        )
    )

    membersfolder_id = 'Members'

    security = ClassSecurityInfo()

    #
    #   ZMI methods
    #
    security.declareProtected( ManagePortal, 'manage_overview' )
    manage_overview = DTMLFile( 'explainMembershipTool', _dtmldir )

    security.declareProtected(ManagePortal, 'manage_mapRoles')
    manage_mapRoles = DTMLFile('membershipRolemapping', _dtmldir )

    security.declareProtected(ManagePortal, 'manage_setMembersFolderById')
    def manage_setMembersFolderById(self, id='', REQUEST=None):
        """ ZMI method to set the members folder object by its id.
        """
        self.setMembersFolderById(id)
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect( self.absolute_url()
                    + '/manage_mapRoles'
                    + '?manage_tabs_message=Members+folder+changed.'
                    )

    #
    #   'portal_membership' interface methods
    #
    security.declareProtected( ListPortalMembers, 'getRoster' )
    def getRoster(self):
        """ Return a list of mappings for 'listed' members.
        
        If Manager, return a list of all usernames.  The mapping
        contains the id and listed variables.
        """
        isManager = _checkPermission('Manage portal', self)
        roster = []
        for member in self.listMembers():
            if isManager or member.listed:
                roster.append({'id':member.getId(),
                               'listed':member.listed})
        return roster

    security.declareProtected(ManagePortal, 'setMembersFolderById')
    def setMembersFolderById(self, id=''):
        """ Set the members folder object by its id.
        """
        self.membersfolder_id = id.strip()

    security.declarePublic('getMembersFolder')
    def getMembersFolder(self):
        """ Get the members folder object.
        """
        parent = aq_parent( aq_inner(self) )
        members = getattr(parent, self.membersfolder_id, None)
        return members

    security.declareProtected(ManagePortal, 'createMemberarea')
    def createMemberarea(self, member_id):
        """ Create a member area for 'member_id'.
        """
        members = self.getMembersFolder()
        if members is not None and not hasattr(members, member_id):
            f_title = "%s's Home" % member_id
            members.manage_addPortalFolder( id=member_id, title=f_title )
            f=getattr(members, member_id)

            # Grant ownership to Member
            acl_users = self.__getPUS()
            user = acl_users.getUser(member_id)

            if user is not None:
                user= user.__of__(acl_users)
            else:
                from AccessControl import getSecurityManager
                user= getSecurityManager().getUser()
                # check that we do not do something wrong
                if user.getId() != member_id:
                    raise NotImplementedError, \
                        'cannot get user for member area creation'

            f.changeOwnership(user)
            f.manage_setLocalRoles(member_id, ['Owner'])

            # Create Member's home page.
            # DEFAULT_MEMBER_CONTENT ought to be configurable per
            # instance of MembershipTool.
            addDocument( f
                       , 'index_html'
                       , member_id+"'s Home"
                       , member_id+"'s front page"
                       , "structured-text"
                       , (DEFAULT_MEMBER_CONTENT % member_id)
                       )

            f.index_html._setPortalTypeName( 'Document' )

            # Overcome an apparent catalog bug.
            f.index_html.reindexObject()
            wftool = getToolByName( f, 'portal_workflow' )
            wftool.notifyCreated( f.index_html )

    def getHomeFolder(self, id=None, verifyPermission=0):
        """ Return a member's home folder object, or None.
        """
        if id is None:
            member = self.getAuthenticatedMember()
            if not hasattr(member, 'getMemberId'):
                return None
            id = member.getMemberId()
        members = self.getMembersFolder()
        if members:
            try:
                folder = members[id]
                if verifyPermission and not _checkPermission('View', folder):
                    # Don't return the folder if the user can't get to it.
                    return None
                return folder
            except KeyError: pass
        return None

    def getHomeUrl(self, id=None, verifyPermission=0):
        """ Return the URL to a member's home folder, or None.
        """
        home = self.getHomeFolder(id, verifyPermission)
        if home is not None:
            return home.absolute_url()
        else:
            return None

InitializeClass(MembershipTool)
