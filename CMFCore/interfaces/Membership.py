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
class Member:
    """
    The Member interface includes the Zope BasicUser interface.  This
    document describes the additional methods the PTK Member interface
    requires.

    A Member is also a PTK Toolbox Actions provider.

    Unlike ZClass property sheets, properties defined by a member's
    propertysheets are not necessarily available as attributes of the
    member.  They should be explicitly referenced through the
    PropertySheet or PropertySheets interfaces.  If you depend on them
    being available as attributes of the member, or upon members
    having a 'propertysheets' attribute, your code will break in the
    not-so-distant future.
    """

    def getHomeUrl(self):
        """
        Returns a URL to this user's Member folder.  This URL is not
        necesarily sanity- or reality-checked in any way.

        This method is implemented by BTKBase.MemberBase and by
        PersistentUserSource.MemberMixin.

        Returns: string
        Permissions: None assigned
        """

    def setMemberProperties(self, REQUEST):
        """
        Search the user's propertysheets for properties with values in
        the REQUEST variable, and update them with the REQUEST's
        value.

        This method is implemented by BTKBase.MemberBase and by
        PersistentUserSource.MemberMixin.

        Returns: None
        Permissions: None assigned
        """

    def PropertySheets(self):
        """
        Return a list of all of the member's property sheets.

        This method is implemented by BTKBase.MemberBase and by
        PersistentUserSource.MemberMixin.

        Returns: list
        Permissions: none assigned
        """

    def changeUser(self, password, roles, domains):
        """
        Set the user's basic security properties.

        LoginManager will contain these basic properties in a
        designated propertysheet.  Since this sheet does not yet
        exist, and since (in the interm) the PTK is supporting
        multiple user folder-like objects with different methods of
        handling these properties, changeUser is being provided as a
        Member method.  Eventually, it will just be a shorthand which
        attempts to set the values of the appropreate property sheet.

        This method is implemented by BTKBase.MemberBase and by
        PersistentUserSource.MemberMixin.

        Returns: None
        Permissions: None assigned (this is probably an important one to fix)
        """

class MemberFolder:
    """
    The Member Folder is the PTK's acl_users object.  This interface
    has been threatening to dissapear for a couple weeks.  This is
    because this interface does not add anything to the
    BasicUserFolder interface that could not be better placed
    elsewhere.  (For example, the PortalObject.)

    * addMember has been moved to the Portal interface.
    
    This interface document describes the additional methods over
    BasicUserFolder which this interface requires.
    """
    
    def is_ssl(self, REQUEST):
        """
        This method does not seem to be used anywhere presently.  It
        was inherited from my initial codebase.

        This will go away when PTK officially moves to LoginManager.
        If you need information like this, you can discover it with an
        appropreate LoginMethod.

        Returns: true if REQUEST came via an SSL connection, false
        otherwise
        Permissions: None assigned
        """

    def __bobo_traverse__(self, REEQUEST, name=None):
        """
        Handle object traversal to Member objects.

        LoginManager also provides this service.
        
        Returns: Member object, or a containted Zope object
        Raises: 'Not Found' if 'name' refers to an unknown resource
        Permissions: None assigned
        """
