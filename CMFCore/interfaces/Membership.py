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
