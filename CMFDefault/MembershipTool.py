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
            members.manage_addPortalFolder(member_id)
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
                                , (default_member_content % id)
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
        if not info.isAnonymous:
            homeUrl = self.getHomeUrl()
            if homeUrl is not None:
                return (
                    {'name': 'My Stuff',
                     'url': homeUrl + '/folder_contents',
                     'permissions': [],
                     'category': 'user'},
                    )
        return None

InitializeClass(MembershipTool)
