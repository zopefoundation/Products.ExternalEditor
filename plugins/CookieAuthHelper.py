##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights
# Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this
# distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Class: CookieAuthHelper

$Id$
"""

from base64 import encodestring, decodestring

from AccessControl.SecurityInfo import ClassSecurityInfo
from OFS.Folder import Folder
from App.class_init import default__class_init__ as InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import manage_addPageTemplate

from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.interfaces.plugins import \
        ILoginPasswordHostExtractionPlugin, IChallengePlugin,  \
        ICredentialsUpdatePlugin, ICredentialsResetPlugin


manage_addCookieAuthHelperForm = PageTemplateFile(
    'www/caAdd', globals(), __name__='manage_addCookieAuthHelperForm')


def addCookieAuthHelper( dispatcher
                       , id
                       , title=None
                       , cookie_name=''
                       , REQUEST=None
                       ):
    """ Add a Cookie Auth Helper to a Pluggable Auth Service. """
    sp = CookieAuthHelper(id, title, cookie_name)
    dispatcher._setObject(sp.getId(), sp)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( '%s/manage_workspace'
                                      '?manage_tabs_message='
                                      'CookieAuthHelper+added.'
                                    % dispatcher.absolute_url() )


class CookieAuthHelper(Folder, BasePlugin):
    """ Multi-plugin for managing details of Cookie Authentication. """
    __implements__ = ( ILoginPasswordHostExtractionPlugin
                     , IChallengePlugin
                     , ICredentialsUpdatePlugin
                     , ICredentialsResetPlugin
                     )

    meta_type = 'Cookie Auth Helper'
    cookie_name = '__ginger_snap'
    login_path = 'login_form'
    security = ClassSecurityInfo()

    _properties = ( { 'id'    : 'title'
                    , 'label' : 'Title'
                    , 'type'  : 'string'
                    , 'mode'  : 'w'
                    }
                  , { 'id'    : 'cookie_name'
                    , 'label' : 'Cookie Name'
                    , 'type'  : 'string'
                    , 'mode'  : 'w'
                    }
                  , { 'id'    : 'login_path'
                    , 'label' : 'Login Form'
                    , 'type'  : 'string'
                    , 'mode'  : 'w'
                    }
                  )

    manage_options = ( BasePlugin.manage_options[:1]
                     + Folder.manage_options[:1]
                     + Folder.manage_options[2:]
                     )

    def __init__(self, id, title=None, cookie_name=''):
        self._setId(id)
        self.title = title

        if cookie_name:
            self.cookie_name = cookie_name


    security.declarePrivate('extractCredentials')
    def extractCredentials(self, request):
        """ Extract credentials from cookie or 'request'. """
        creds = {}
        cookie = request.get(self.cookie_name, '')

        if cookie:
            cookie_val = decodestring(cookie)
            login, password = cookie_val.split(':')
            
            creds['login'] = login
            creds['password'] = password
        else:
            # Look in the request for the names coming from the login form
            login = request.get('__ac_name', '')
            password = request.get('__ac_password', '')

            if login:
                creds['login'] = login
                creds['password'] = password

                request.set('__ac_name', '')
                request.set('__ac_password', '')

                cookie_val = encodestring('%s:%s' % (login, password))
                cookie_val = cookie_val.replace( '\n', '' )
                response = request['RESPONSE']
                response.setCookie(self.cookie_name, cookie_val, path='/')

        if creds:
            creds['remote_host'] = request.get('REMOTE_HOST', '')

            try:
                creds['remote_address'] = request.getClientAddr()
            except AttributeError:
                creds['remote_address'] = request.get('REMOTE_ADDR', '')

        return creds


    security.declarePrivate('challenge')
    def challenge(self, request, response, **kw):
        """ Challenge the user for credentials. """
        return self.unauthorized()


    security.declarePrivate('updateCredentials')
    def updateCredentials(self, request, response, login, new_password):
        """ Respond to change of credentials (NOOP for basic auth). """
        cookie_val = encodestring('%s:%s' % (login, new_password))
        
        response.setCookie(self.cookie_name, cookie_val, path='/')


    security.declarePrivate('resetCredentials')
    def resetCredentials(self, request, response):
        """ Raise unauthorized to tell browser to clear credentials. """
        response.expireCookie(self.cookie_name, path='/')


    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container):
        """ Setup tasks upon instantiation """
        manage_addPageTemplate( self
                              , 'login_form'
                              , title='Login Form'
                              , text=BASIC_LOGIN_FORM
                              )


    security.declarePrivate('unauthorized')
    def unauthorized(self):
        resp = self.REQUEST['RESPONSE']
        # No errors of any sort may propagate, and we don't care *what*
        # they are, even to log them.
        try: del resp.unauthorized
        except: pass
        try: del resp._unauthorized
        except: pass

        # If we set the auth cookie before, delete it now.
        if resp.cookies.has_key(self.cookie_name):
            del resp.cookies[self.cookie_name]

        # Redirect if desired.
        url = self.getLoginURL()
        if url is not None:
            raise 'Redirect', url

        # Fall through to the standard unauthorized() call.
        resp.unauthorized()


    security.declarePrivate('getLoginURL')
    def getLoginURL(self):
        """ Where to send people for logging in """
        if self.login_path.startswith('/'):
            return self.login_path
        elif self.login_path != '':
            return '%s/%s' % (self.absolute_url(), self.login_path)
        else:
            return None


InitializeClass(CookieAuthHelper)


BASIC_LOGIN_FORM = """<html>
  <head>
    <title> Login Form </title>
  </head>

  <body>

    <h3> Please log in </h3>

    <form method="post" action=""
          tal:define="acl_path here/acl_users/absolute_url"
          tal:attributes="action string:${acl_path}/login">

      <table cellpadding="2">
        <tr>
          <td><b>Login:</b> </td>
          <td><input type="text" name="__ac_name" size="30" /></td>
        </tr>
        <tr>
          <td><b>Password:</b></td>
          <td><input type="password" name="__ac_password" size="30" /></td>
        </tr>
        <tr>
          <td colspan="2">
            <br />
            <input type="submit" value=" Log In " />
          </td>
        </tr>
      </table>

    </form>

  </body>

</html>
"""

