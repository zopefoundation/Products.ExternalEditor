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

"""Cookie Crumbler: Enable cookies for non-cookie user folders.
$Id$
"""
__version__='$Revision$'[11:-2]


from base64 import encodestring
from urllib import quote, unquote
from DateTime import DateTime
from utils import SimpleItemWithProperties
from AccessControl import ClassSecurityInfo
from ZPublisher import BeforeTraverse
import Globals
import CMFCorePermissions
from Globals import HTMLFile
from zLOG import LOG, ERROR
import sys

from ZPublisher.HTTPRequest import HTTPRequest

# Constants.
ATTEMPT_DISABLED = -1  # Disable cookie crumbler
ATTEMPT_NONE = 0       # No attempt at authentication
ATTEMPT_LOGIN = 1      # Attempt to log in
ATTEMPT_RESUME = 2     # Attempt to resume session


class CookieCrumbler (SimpleItemWithProperties):
    '''
    Reads cookies during traversal and simulates the HTTP
    authentication headers.
    '''
    meta_type = 'Cookie Crumbler'

    security = ClassSecurityInfo()
    security.declareProtected(CMFCorePermissions.ModifyCookieCrumblers,
                              'manage_editProperties',
                              'manage_changeProperties')
    security.declareProtected(CMFCorePermissions.ViewManagementScreens,
                              'manage_propertiesForm')


    _properties = ({'id':'auth_cookie', 'type': 'string', 'mode':'w',
                    'label':'Authentication cookie name'},
                   {'id':'name_cookie', 'type': 'string', 'mode':'w',
                    'label':'User name form variable'},
                   {'id':'pw_cookie', 'type': 'string', 'mode':'w',
                    'label':'User password form variable'},
                   {'id':'persist_cookie', 'type': 'string', 'mode':'w',
                    'label':'User name persistence form variable'},
                   {'id':'auto_login_page', 'type': 'string', 'mode':'w',
                    'label':'Auto-login page ID'},
                   {'id':'logout_page', 'type': 'string', 'mode':'w',
                    'label':'Logout page ID'},
                   )

    auth_cookie = '__ac'
    name_cookie = '__ac_name'
    pw_cookie = '__ac_password'
    persist_cookie = '__ac_persistent'
    auto_login_page = 'login_form'
    logout_page = 'logged_out'

    security.declarePrivate('delRequestVar')
    def delRequestVar(self, req, name):
        try: del req.other[name]
        except: pass
        try: del req.form[name]
        except: pass
        try: del req.cookies[name]
        except: pass
        try: del req.environ[name]
        except: pass

    # Allow overridable cookie set/expiration methods.
    security.declarePrivate('getCookieMethod')
    def getCookieMethod( self, name='setAuthCookie', default=None ):
        return getattr( self.aq_inner.aq_parent, name, default )

    security.declarePrivate('setDefaultAuthCookie')
    def defaultSetAuthCookie( self, resp, cookie_name, cookie_value ):
        resp.setCookie( cookie_name, cookie_value, path='/')

    security.declarePrivate('defaultExpireAuthCookie')
    def defaultExpireAuthCookie( self, resp, cookie_name ):
        resp.expireCookie( cookie_name, path='/')

    security.declarePrivate('modifyRequest')
    def modifyRequest(self, req, resp):
        # Returns flags indicating what the user is trying to do.

        if req.__class__ is not HTTPRequest:
            return ATTEMPT_DISABLED

        if not req[ 'REQUEST_METHOD' ] in ( 'GET', 'PUT', 'POST' ):
            return ATTEMPT_DISABLED

        if req.environ.has_key( 'WEBDAV_SOURCE_PORT' ):
            return ATTEMPT_DISABLED

        if req._auth and not getattr(req, '_cookie_auth', 0):
            # Using basic auth.
            return ATTEMPT_DISABLED
        else:
            if req.has_key(self.pw_cookie) and req.has_key(self.name_cookie):
                # Attempt to log in and set cookies.
                name = req[self.name_cookie]
                pw = req[self.pw_cookie]
                ac = encodestring('%s:%s' % (name, pw))
                req._auth = 'basic %s' % ac
                req._cookie_auth = 1
                resp._auth = 1
                if req.get(self.persist_cookie, 0):
                    # Persist the user name (but not the pw or session)
                    expires = (DateTime() + 365).toZone('GMT').rfc822()
                    resp.setCookie(self.name_cookie, name, path='/',
                                   expires=expires)
                else:
                    # Expire the user name
                    resp.expireCookie(self.name_cookie, path='/')
                method = self.getCookieMethod( 'setAuthCookie'
                                             , self.defaultSetAuthCookie )
                method( resp, self.auth_cookie, quote( ac ) )
                self.delRequestVar(req, self.name_cookie)
                self.delRequestVar(req, self.pw_cookie)
                return ATTEMPT_LOGIN
            elif req.has_key(self.auth_cookie):
                # Copy __ac to the auth header.
                ac = unquote(req[self.auth_cookie])
                req._auth = 'basic %s' % ac
                req._cookie_auth = 1
                resp._auth = 1
                self.delRequestVar(req, self.auth_cookie)
                return ATTEMPT_RESUME
            return ATTEMPT_NONE

    def __call__(self, container, req):
        '''The __before_publishing_traverse__ hook.'''
        resp = self.REQUEST['RESPONSE']
        attempt = self.modifyRequest(req, resp)
        if attempt == ATTEMPT_DISABLED:
            return
        if not req.get('disable_cookie_login__', 0):
            if attempt == ATTEMPT_LOGIN or attempt == ATTEMPT_NONE:
                # Modify the "unauthorized" response.
                req._hold(ResponseCleanup(resp))
                resp.unauthorized = self.unauthorized
                resp._unauthorized = self._unauthorized
        if attempt != ATTEMPT_NONE:
            phys_path = self.getPhysicalPath()
            if self.logout_page:
                # Cookies are in use.
                page = getattr(container, self.logout_page, None)
                if page is not None:
                    # Provide a logout page.
                    req._logout_path = phys_path + ('logout',)
            req._credentials_changed_path = (
                phys_path + ('credentialsChanged',))

    security.declarePublic('credentialsChanged')
    def credentialsChanged(self, user, name, pw):
        ac = encodestring('%s:%s' % (name, pw))
        method = self.getCookieMethod( 'setAuthCookie'
                                       , self.defaultSetAuthCookie )
        resp = self.REQUEST['RESPONSE']
        method( resp, self.auth_cookie, quote( ac ) )

    def _cleanupResponse(self):
        resp = self.REQUEST['RESPONSE']
        try: del resp.unauthorized
        except: pass
        try: del resp._unauthorized
        except: pass
        return resp

    security.declarePrivate('unauthorized')
    def unauthorized(self):
        resp = self._cleanupResponse()
        # If we set the auth cookie before, delete it now.
        if resp.cookies.has_key(self.auth_cookie):
            del resp.cookies[self.auth_cookie]
        # Redirect if desired.
        url = self.getLoginURL()
        if url is not None:
            raise 'Redirect', url
        # Fall through to the standard unauthorized() call.
        resp.unauthorized()

    def _unauthorized(self):
        resp = self._cleanupResponse()
        # If we set the auth cookie before, delete it now.
        if resp.cookies.has_key(self.auth_cookie):
            del resp.cookies[self.auth_cookie]
        # Redirect if desired.
        url = self.getLoginURL()
        if url is not None:
            resp.redirect(url, lock=1)
            # We don't need to raise an exception.
            return
        # Fall through to the standard _unauthorized() call.
        resp._unauthorized()

    security.declarePublic('getLoginURL')
    def getLoginURL(self):
        '''
        Redirects to the login page.
        '''
        if self.auto_login_page:
            req = self.REQUEST
            resp = req['RESPONSE']
            iself = getattr(self, 'aq_inner', self)
            parent = getattr(iself, 'aq_parent', None)
            page = getattr(parent, self.auto_login_page, None)
            if page is not None:
                retry = getattr(resp, '_auth', 0) and '1' or ''
                came_from = req.get('came_from', None)
                if came_from is None:
                    came_from = req['URL']
                url = '%s?came_from=%s&retry=%s' % (
                    page.absolute_url(), quote(came_from), retry)
                return url
        return None

    security.declarePublic('logout')
    def logout(self):
        '''
        Logs out the user and redirects to the logout page.
        '''
        req = self.REQUEST
        resp = req['RESPONSE']
        method = self.getCookieMethod( 'expireAuthCookie'
                                     , self.defaultExpireAuthCookie )
        method( resp, cookie_name=self.auth_cookie )
        redir = 0
        if self.logout_page:
            iself = getattr(self, 'aq_inner', self)
            parent = getattr(iself, 'aq_parent', None)
            page = getattr(parent, self.logout_page, None)
            if page is not None:
                redir = 1
                resp.redirect(page.absolute_url())
        if not redir:
            # Should not normally happen.
            return 'Logged out.'

    # Installation and removal of traversal hooks.

    def manage_beforeDelete(self, item, container):
        if item is self:
            handle = self.meta_type + '/' + self.getId()
            BeforeTraverse.unregisterBeforeTraverse(container, handle)

    def manage_afterAdd(self, item, container):
        if item is self:
            handle = self.meta_type + '/' + self.getId()
            container = container.this()
            nc = BeforeTraverse.NameCaller(self.getId())
            BeforeTraverse.registerBeforeTraverse(container, nc, handle)

Globals.InitializeClass(CookieCrumbler)


class ResponseCleanup:
    def __init__(self, resp):
        self.resp = resp

    def __del__(self):
        # Free the references.
        try: del self.resp.unauthorized
        except: pass
        try: del self.resp._unauthorized
        except: pass
        try: del self.resp
        except: pass


manage_addCCForm = HTMLFile('dtml/addCC', globals())
manage_addCCForm.__name__ = 'addCC'

def manage_addCC(self, id, REQUEST=None):
    ' '
    ob = CookieCrumbler()
    ob.id = id
    self._setObject(id, ob)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)

