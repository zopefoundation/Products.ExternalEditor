""" CMFHotfix_20031026 product.

Please see the README.txt for affected versions, installation, etc.

$Id$
"""
from zLOG import LOG, INFO
from AccessControl.PermissionRole import PermissionRole

from Products.CMFCore.CMFCorePermissions import View, ListPortalMembers
from Products.CMFCore.MembershipTool import MembershipTool as MTool
from Products.CMFCore.utils import getToolByName

from Products.CMFDefault.RegistrationTool import RegistrationTool as RTool

def _update_MembershipTool_searchMembers_permission():

    """ Repair Collector #189 by careful surgery on the class dictionary
        of MembershipTool.
    """

    new_permissions = []
    for k, v in MTool.__ac_permissions__:

        if k == View:
            new_v = [ x for x in v if x != 'searchMembers' ]
            v = tuple( new_v )

        new_permissions.append( ( k, v ) )

    new_permissions.append( ( ListPortalMembers, ( 'searchMembers', ) ) )

    MTool.__ac_permissions__ = tuple( new_permissions )
    MTool.searchMembers__roles__ = PermissionRole( ListPortalMembers
                                                 , ( 'Manager', )
                                                 )

    LOG( "CMFHotfix_20031026", INFO
       , "Updated permission on "
         + "CMFCore.MembershipTool.MembershipTool.searchMembers"
         + " from 'View' to 'List portal members'"
       )

def _safer_registeredNotify( self, new_member_id ):

    """ Handle mailing the registration / welcome message.
    """
    membership = getToolByName( self, 'portal_membership' )
    member = membership.getMemberById( new_member_id )

    if member is None:
        raise 'NotFound', 'The username you entered could not be found.'

    password = member.getPassword()

    email = member.getProperty( 'email' )

    if email is None:
        raise ValueError( 'No email address is registered for member: %s'
                        % new_member_id )

    # Rather than have the template try to use the mailhost, we will
    # render the message ourselves and send it from here (where we
    # don't need to worry about 'UseMailHost' permissions).
    mail_text = self.registered_notify_template( self
                                               , self.REQUEST
                                               , member=member
                                               , password=password
                                               , email=email
                                               )
 
    host = self.MailHost
    host.send( mail_text )

    return self.mail_password_response( self, self.REQUEST )

def _monkeyPatch_RegistrationTool_registerNotify():

    """ Don't allow the user to smuggle in an email address via the request.
    """
    
    RTool.registeredNotify = _safer_registeredNotify

    LOG( "CMFHotfix_20031026", INFO
       , "Monkey patched "
         + "CMFDefault.RegistrationTool.RegistrationTool.registerdNotify"
         + " to prevent email forgery"
       )


def initialize( context ):

    _update_MembershipTool_searchMembers_permission()

    _monkeyPatch_RegistrationTool_registerNotify()
