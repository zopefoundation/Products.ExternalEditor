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

# Constants.
ATTEMPT_NONE = 0
ATTEMPT_LOGIN = 1
ATTEMPT_CONT = 2


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
    def defaultExpireAuthCookie( self, cookie_name ):
        resp.expireCookie( cookie_name, path='/')

    security.declarePrivate('modifyRequest')
    def modifyRequest(self, req, resp):
        # Returns flags indicating what the user is trying to do.
        if not req._auth:
            if (req.has_key(self.pw_cookie) and
                req.has_key(self.name_cookie)):
                # Attempt to log in and set cookies.
                name = req[self.name_cookie]
                pw = req[self.pw_cookie]
                ac = encodestring('%s:%s' % (name, pw))
                req._auth = 'basic %s' % ac
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
                resp._auth = 1
                self.delRequestVar(req, self.auth_cookie)
                return ATTEMPT_CONT
        return ATTEMPT_NONE

    def __call__(self, container, req):
        '''The __before_publishing_traverse__ hook.'''
        resp = self.REQUEST['RESPONSE']
        attempt = self.modifyRequest(req, resp)
        if self.auto_login_page:
            if not req.get('disable_cookie_login__', 0):
                if (attempt == ATTEMPT_LOGIN or
                    not getattr(resp, '_auth', 0)):
                    page = getattr(container, self.auto_login_page, None)
                    if page is not None:
                        # Provide a login page.
                        req._hold(ResponseCleanup(resp))
                        resp.unauthorized = self.unauthorized
                        resp._unauthorized = self._unauthorized
        if attempt:
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
        resp = self.REQUEST['RESPONSE']
        ac = encodestring('%s:%s' % (name, pw))
        self.setAuthCookie(resp, ac)

    def _cleanupResponse(self):
        resp = self.REQUEST['RESPONSE']
        try: del resp.unauthorized
        except: pass
        try: del resp._unauthorized
        except: pass
        return resp

    security.declarePrivate('unauthorized')
    def unauthorized(self):
        url = self.getLoginURL()
        if url:
            raise 'Redirect', url
        # Use the standard unauthorized() call.
        resp = self._cleanupResponse()
        resp.unauthorized()

    def _unauthorized(self):
        url = self.getLoginURL()
        if url:
            resp = self.REQUEST['RESPONSE']
            resp.redirect(url, lock=1)
            # We don't need to raise an exception.
            return
        # Use the standard _unauthorized() call.
        resp = self._cleanupResponse()
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
            if page:
                retry = getattr(resp, '_auth', 0) and '1' or ''
                url = '%s?came_from=%s&retry=%s' % (
                    page.absolute_url(), quote(req['URL']), retry)
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
        method( cookie_name=self.auth_cookie )
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

