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

"""CMFDefault portal_registration tool.

$Id$
"""
__version__='$Revision$'[11:-2]


from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import _checkPermission, getToolByName
from Products.CMFCore.RegistrationTool import RegistrationTool

from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from utils import _dtmldir

class RegistrationTool (RegistrationTool):
    meta_type = 'Default Registration Tool'

    security = ClassSecurityInfo()

    #
    #   ZMI methods
    #
    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'manage_overview' )
    manage_overview = DTMLFile( 'explainRegistrationTool', _dtmldir )

    #
    #   'portal_registration' interface methods
    #
    security.declarePublic( 'testPasswordValidity' )
    def testPasswordValidity(self, password, confirm=None):
        '''If the password is valid, returns None.  If not, returns
        a string explaining why.
        '''
        if len(password) < 5 and not _checkPermission('Manage portal', self):
            return 'Your password must contain at least 5 characters.'
        if confirm is not None and confirm != password:
            return 'Your password and confirmation did not match. ' \
                   'Please try again.'
        return None

    security.declarePublic('listActions')
    def listActions(self, info):
        """
        """

    security.declarePublic( 'testPropertiesValidity' )
    def testPropertiesValidity(self, props, member=None):
        '''If the properties are valid, returns None.  If not, returns
        a string explaining why.
        '''
        if member is None:
            # New member.
            username = props.get('username', '')
            if not username:
                return 'You must enter a valid name.'
            if not self.isMemberIdAllowed(username):
                return 'The login name you selected is already ' \
                       'in use or is not valid. Please choose another.'
            if not props.get('email', ''):
                return 'You must enter a valid email address.'
        return None

    security.declarePublic( 'mailPassword' )
    def mailPassword(self, forgotten_userid, REQUEST):
        '''Email a forgotten password to a member.  Raises an exception
        if user ID is not found.
        '''
        membership = getToolByName(self, 'portal_membership')
        member = membership.getMemberById(forgotten_userid)
        if member is None:
            raise 'NotFound', 'The username you entered could not be found.'
    
        # Rather than have the template try to use the mailhost, we will
        # render the message ourselves and send it from here (where we
        # don't need to worry about 'UseMailHost' permissions).
        mail_text = self.mail_password_template( self
                                               , REQUEST
                                               , member=member
                                               , password=member.getPassword()
                                               )
    
        host = self.MailHost
        host.send( mail_text )

        return self.mail_password_response( self, REQUEST )

    security.declarePublic( 'registeredNotify' )
    def registeredNotify( self, new_member_id ):
        """
            Handle mailing the registration / welcome message.
        """
        membership = getToolByName( self, 'portal_membership' )
        member = membership.getMemberById( new_member_id )

        if member is None:
            raise 'NotFound', 'The username you entered could not be found.'

        password = member.getPassword()
    
        # Rather than have the template try to use the mailhost, we will
        # render the message ourselves and send it from here (where we
        # don't need to worry about 'UseMailHost' permissions).
        mail_text = self.registered_notify_template( self
                                                   , self.REQUEST
                                                   , member=member
                                                   , password=password
                                                   )
    
        host = self.MailHost
        host.send( mail_text )

        return self.mail_password_response( self, self.REQUEST )

InitializeClass(RegistrationTool)
