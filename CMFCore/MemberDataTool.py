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

"""Basic member data tool.
$Id$
"""
__version__='$Revision$'[11:-2]


import string
from utils import UniqueObject, getToolByName, _dtmldir
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Globals import Acquisition, Persistent, DTMLFile
import Globals
from AccessControl.Role import RoleManager
from BTrees.OOBTree import OOBTree
from ZPublisher.Converters import type_converters
from Acquisition import aq_inner, aq_parent, aq_base
from AccessControl import ClassSecurityInfo
from CMFCorePermissions import ViewManagementScreens
import CMFCorePermissions

_marker = []  # Create a new marker object.


class MemberDataTool (UniqueObject, SimpleItem, PropertyManager):
    '''This tool wraps user objects, making them act as Member objects.
    '''
    id = 'portal_memberdata'
    meta_type = 'CMF Member Data Tool'
    _v_temps = None
    _properties = ()

    security = ClassSecurityInfo()

    manage_options=( ( { 'label' : 'Overview'
                       , 'action' : 'manage_overview'
                       }
                     , { 'label' : 'Contents'
                       , 'action' : 'manage_showContents'
                       }
                     )
                   + PropertyManager.manage_options
                   + SimpleItem.manage_options
                   )

    #
    #   ZMI methods
    #
    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'manage_overview' )
    manage_overview = DTMLFile( 'explainMemberDataTool', _dtmldir )

    security.declareProtected( CMFCorePermissions.ViewManagementScreens
                             , 'manage_showContents')
    manage_showContents = DTMLFile('memberdataContents', _dtmldir )

    security.declareProtected( CMFCorePermissions.ViewManagementScreens
                             , 'getContentsInformation',)


    def __init__(self):
        self._members = OOBTree()
        # Create the default properties.
        self._setProperty('email', '', 'string')
        self._setProperty('portal_skin', '', 'string')
        self._setProperty('listed', '', 'boolean')
        self._setProperty('login_time', '2000/01/01', 'date')
        self._setProperty('last_login_time', '2000/01/01', 'date')

    #
    #   'portal_memberdata' interface methods
    #
    security.declarePrivate('getMemberDataContents')
    def getMemberDataContents(self):
        '''
        Return the number of members stored in the _members
        BTree and some other useful info
        '''
        membertool   = getToolByName(self, 'portal_membership')
        members      = self._members
        user_list    = membertool.listMemberIds()
        member_list  = members.keys()
        member_count = len(members)
        orphan_count = 0

        for member in member_list:
            if member not in user_list:
                orphan_count = orphan_count + 1

        return [{ 'member_count' : member_count,
                  'orphan_count' : orphan_count }]

    security.declarePrivate( 'searchMemberDataContents' )
    def searchMemberDataContents( self, search_param, search_term ):
        """ Search members """
        res = []

        if search_param == 'username':
            search_param = 'id'

        for user_wrapper in self._members.values():
            searched = getattr( user_wrapper, search_param, None )
            if searched is not None and string.find( searched, search_term ) != -1:
                res.append( { 'username' : getattr( user_wrapper, 'id' )
                            , 'email' : getattr( user_wrapper, 'email', '' )
                            }
                          )

        return res

    security.declarePrivate('pruneMemberDataContents')
    def pruneMemberDataContents(self):
        '''
        Compare the user IDs stored in the member data
        tool with the list in the actual underlying acl_users
        and delete anything not in acl_users
        '''
        membertool= getToolByName(self, 'portal_membership')
        members   = self._members
        user_list = membertool.listMemberIds()

        for tuple in members.items():
            member_name = tuple[0]
            member_obj  = tuple[1]
            if member_name not in user_list:
                del members[member_name]

    security.declarePrivate('wrapUser')
    def wrapUser(self, u):
        '''
        If possible, returns the Member object that corresponds
        to the given User object.
        '''
        id = u.getUserName()
        members = self._members
        if not members.has_key(id):
            # Get a temporary member that might be
            # registered later via registerMemberData().
            temps = self._v_temps
            if temps is not None and temps.has_key(id):
                m = temps[id]
            else:
                base = aq_base(self)
                m = MemberData(base, id)
                if temps is None:
                    self._v_temps = {id:m}
                else:
                    temps[id] = m
        else:
            m = members[id]
        # Return a wrapper with self as containment and
        # the user as context.
        return m.__of__(self).__of__(u)

    security.declarePrivate('registerMemberData')
    def registerMemberData(self, m, id):
        '''
        Adds the given member data to the _members dict.
        This is done as late as possible to avoid side effect
        transactions and to reduce the necessary number of
        entries.
        '''
        self._members[id] = m

Globals.InitializeClass(MemberDataTool)


class MemberData (SimpleItem):
    security = ClassSecurityInfo()

    def __init__(self, tool, id):
        self.id = id
        # Make a temporary reference to the tool.
        # The reference will be removed by notifyModified().
        self._tool = tool

    security.declarePrivate('notifyModified')
    def notifyModified(self):
        # Links self to parent for full persistence.
        tool = getattr(self, '_tool', None)
        if tool is not None:
            del self._tool
            tool.registerMemberData(self, self.getId())

    security.declarePublic('getUser')
    def getUser(self):
        # The user object is our context, but it's possible for
        # restricted code to strip context while retaining
        # containment.  Therefore we need a simple security check.
        parent = aq_parent(self)
        bcontext = aq_base(parent)
        bcontainer = aq_base(aq_parent(aq_inner(self)))
        if bcontext is bcontainer or not hasattr(bcontext, 'getUserName'):
            raise 'MemberDataError', "Can't find user data"
        # Return the user object, which is our context.
        return parent

    def getTool(self):
        return aq_parent(aq_inner(self))

    security.declarePublic('getMemberId')
    def getMemberId(self):
        return self.getUser().getUserName()

    security.declarePrivate('setMemberProperties')
    def setMemberProperties(self, mapping):
        '''Sets the properties of the member.
        '''
        # Sets the properties given in the MemberDataTool.
        tool = self.getTool()
        for id in tool.propertyIds():
            if mapping.has_key(id):
                if not self.__class__.__dict__.has_key(id):
                    value = mapping[id]
                    if type(value)==type(''):
                        proptype = tool.getPropertyType(id) or 'string'
                        if type_converters.has_key(proptype):
                            value = type_converters[proptype](value)
                    setattr(self, id, value)
        # Hopefully we can later make notifyModified() implicit.
        self.notifyModified()

    security.declarePublic('getProperty')
    def getProperty(self, id, default=_marker):
        tool = self.getTool()
        if tool.hasProperty(id):
            return getattr(self, id)
        else:
            if default is _marker:
                raise 'Property not found', id
            else:
                return default

    security.declarePrivate('getPassword')
    def getPassword(self):
        """Return the password of the user."""
        return self.getUser()._getPassword()

    security.declarePrivate('setSecurityProfile')
    def setSecurityProfile(self, password=None, roles=None, domains=None):
        """Set the user's basic security profile"""
        u = self.getUser()
        # This is really hackish.  The Zope User API needs methods
        # for performing these functions.
        if password is not None:
            u.__ = password
        if roles is not None:
            u.roles = roles
        if domains is not None:
            u.domains = domains

    def __str__(self):
        return self.getMemberId()

    ### User object interface ###

    security.declarePublic('getUserName')
    def getUserName(self):
        """Return the username of a user"""
        return self.getUser().getUserName()

    security.declarePublic('getId')
    def getId(self):
        """Get the ID of the user. The ID can be used, at least from
        Python, to get the user from the user's
        UserDatabase"""
        return self.getUser().getId()

    security.declarePublic('getRoles')
    def getRoles(self):
        """Return the list of roles assigned to a user."""
        return self.getUser().getRoles()

    security.declarePublic('getRolesInContext')
    def getRolesInContext(self, object):
        """Return the list of roles assigned to the user,
           including local roles assigned in context of
           the passed in object."""
        return self.getUser().getRolesInContext(object)

    security.declarePublic('getDomains')
    def getDomains(self):
        """Return the list of domain restrictions for a user"""
        return self.getUser().getDomains()

    security.declarePublic('has_role')
    def has_role(self, roles, object=None):
        """Check to see if a user has a given role or roles."""
        return self.getUser().has_role(roles, object)

    # There are other parts of the interface but they are
    # deprecated for use with CMF applications.

Globals.InitializeClass(MemberData)
