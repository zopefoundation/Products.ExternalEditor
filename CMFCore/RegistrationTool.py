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

"""Basic user registration tool.
$Id$
"""
__version__='$Revision$'[11:-2]


from utils import UniqueObject
from utils import _checkPermission, _getAuthenticatedUser, limitGrantedRoles
from utils import getToolByName, _dtmldir
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from CMFCorePermissions import AddPortalMember, MailForgottenPassword, \
     SetOwnPassword, SetOwnProperties
import CMFCorePermissions
import string, random


class RegistrationTool (UniqueObject, SimpleItem):
    # This tool creates and modifies users by making calls
    # to portal_membership.
    id = 'portal_registration'
    meta_type = 'CMF Registration Tool'

    security = ClassSecurityInfo()

    manage_options = ( { 'label' : 'Overview', 'action' : 'manage_overview' }
                     , 
                     ) + SimpleItem.manage_options

    #
    #   ZMI methods
    #
    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'manage_overview' )
    manage_overview = DTMLFile( 'explainRegistrationTool', _dtmldir )

    #
    #   'portal_registration' interface methods
    #
    security.declarePublic('isRegistrationAllowed')
    def isRegistrationAllowed(self, REQUEST):
        '''Returns a boolean value indicating whether the user
        is allowed to add a member to the portal.
        '''
        return _checkPermission('Add Portal Member', self.aq_inner.aq_parent)

    security.declarePublic('testPasswordValidity')
    def testPasswordValidity(self, password, confirm=None):
        '''If the password is valid, returns None.  If not, returns
        a string explaining why.
        '''
        return None

    security.declarePublic('testPropertiesValidity')
    def testPropertiesValidity(self, new_properties, member=None):
        '''If the properties are valid, returns None.  If not, returns
        a string explaining why.
        '''
        return None

    security.declarePublic('generatePassword')
    def generatePassword(self):
        '''Generates a password which is guaranteed to comply
        with the password policy.
        '''
        chars = string.lowercase[:26] + string.uppercase[:26] + string.digits
        result = []
        for n in range(6):
            result.append(random.choice(chars))
        return string.join(result, '')

    security.declareProtected(AddPortalMember, 'addMember')
    def addMember(self, id, password, roles=('Member',), domains='',
                  properties=None):
        '''Creates a PortalMember and returns it. The properties argument
        can be a mapping with additional member properties. Raises an
        exception if the given id already exists, the password does not
        comply with the policy in effect, or the authenticated user is not
        allowed to grant one of the roles listed (where Member is a special
        role that can always be granted); these conditions should be
        detected before the fact so that a cleaner message can be printed.
        '''
        if not self.isMemberIdAllowed(id):
            raise 'Bad Request', 'The login name you selected is already ' \
                  'in use or is not valid. Please choose another.'
        
        failMessage = self.testPasswordValidity(password)
        if failMessage is not None:
            raise 'Bad Request', failMessage

        if properties is not None:
            failMessage = self.testPropertiesValidity(properties)

            if failMessage is not None:
                raise 'Bad Request', failMessage

        # Limit the granted roles.
        # Anyone is always allowed to grant the 'Member' role.
        limitGrantedRoles(roles, self, ('Member',))

        membership = getToolByName(self, 'portal_membership')
        membership.addMember(id, password, roles, domains, properties)

        member = membership.getMemberById(id)
        self.afterAdd(member, id, password, properties)
        return member

    import re
    __ALLOWED_MEMBER_ID_PATTERN = re.compile( "[A-Za-z][A-Za-z0-9_]*" )
    security.declareProtected(AddPortalMember, 'isMemberIdAllowed')
    def isMemberIdAllowed(self, id):
        '''Returns 1 if the ID is not in use and is not reserved.
        '''
        if len(id) < 1 or id == 'Anonymous User':
            return 0
        if not self.__ALLOWED_MEMBER_ID_PATTERN.match( id ):
            return 0
        membership = getToolByName(self, 'portal_membership')
        if membership.getMemberById(id) is not None:
            return 0
        return 1

    security.declarePublic('afterAdd')
    def afterAdd(self, member, id, password, properties):
        '''Called by portal_registration.addMember()
        after a member has been added successfully.'''
        pass

    security.declareProtected(MailForgottenPassword, 'mailPassword')
    def mailPassword(self, forgotten_userid, REQUEST):
        '''Email a forgotten password to a member.  Raises an exception
        if user ID is not found.
        '''
        raise 'NotImplemented'

    security.declareProtected(SetOwnPassword, 'setPassword')
    def setPassword(self, password, domains=None):
        '''Allows the authenticated member to set his/her own password.
        '''
        membership = getToolByName(self, 'portal_membership')
        if not membership.isAnonymousUser():
            member = membership.getAuthenticatedMember()
            failMessage = self.testPasswordValidity(password)
            if failMessage is not None:
                raise 'Bad Request', failMessage
            member.setSecurityProfile(password=password, domains=domains)
        else:
            raise 'Bad Request', 'Not logged in.'
            
    security.declareProtected(SetOwnProperties, 'setProperties')
    def setProperties(self, properties=None, **kw):
        '''Allows the authenticated member to set his/her own properties.
        Accepts either keyword arguments or a mapping for the "properties"
        argument.
        '''
        if properties is None:
            properties = kw
        membership = getToolByName(self, 'portal_membership')
        if not membership.isAnonymousUser():
            member = membership.getAuthenticatedMember()
            failMessage = self.testPropertiesValidity(properties, member)
            if failMessage is not None:
                raise 'Bad Request', failMessage
            member.setMemberProperties(properties)
        else:
            raise 'Bad Request', 'Not logged in.'


InitializeClass(RegistrationTool)
