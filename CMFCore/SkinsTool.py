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

"""Portal skins tool.
$Id$
"""
__version__='$Revision$'[11:-2]


from string import split
from utils import UniqueObject, getToolByName
from PortalFolder import PortalFolder
import Globals
from Globals import HTMLFile, PersistentMapping
from SkinsContainer import SkinsContainer
from Acquisition import aq_base
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from CMFCorePermissions import ManagePortal, AccessContentsInformation
import CMFCorePermissions


def modifiedOptions():
    # Remove the existing "Properties" option and add our own.
    rval = []
    pos = -1
    for o in PortalFolder.manage_options:
        label = o.get('label', None)
        if label != 'Properties':
            rval.append(o)
    rval[1:1] = [{'label':'Properties',
                  'action':'manage_propertiesForm'}]
    return tuple(rval)

class SkinsTool(UniqueObject, SkinsContainer, PortalFolder):
    '''
    This tool is used to supply skins to a portal.
    '''

    id = 'portal_skins'
    meta_type = 'CMF Skins Tool'

    manage_options = modifiedOptions()

    security = ClassSecurityInfo()

    default_skin = ''
    request_varname = 'portal_skin'
    allow_any = 0
    selections = None

    def __init__(self):
        self.selections = PersistentMapping()

    def _getSelections(self):
        sels = self.selections
        if sels is None:
            # Backward compatibility.
            self.selections = sels = PersistentMapping()
        return sels

    security.declareProtected(ManagePortal, 'manage_propertiesForm')
    manage_propertiesForm = HTMLFile('dtml/skinProps', globals())

    security.declareProtected(ManagePortal, 'manage_properties')
    def manage_properties(self, default_skin='', request_varname='',
                          allow_any=0, chosen=(), add_skin=0,
                          del_skin=0, skinname='', skinpath='',
                          REQUEST=None):
        '''
        Changes portal_skin properties.
        '''
        sels = self._getSelections()
        if add_skin:
            skinpath = str(skinpath)
            self.testSkinPath(skinpath)
            sels[str(skinname)] = skinpath
        elif del_skin:
            for name in chosen:
                del sels[name]
        else:
            self.default_skin = str(default_skin)
            self.request_varname = str(request_varname)
            self.allow_any = allow_any and 1 or 0
            if REQUEST is not None:
                for key in sels.keys():
                    fname = 'skinpath_%s' % key
                    val = str(REQUEST[fname])
                    if sels[key] != val:
                        self.testSkinPath(val)
                        sels[key] = val
        if REQUEST is not None:
            return self.manage_propertiesForm(
                self, REQUEST, manage_tabs_message='Properties changed.')

    security.declarePrivate('testSkinPath')
    def testSkinPath(self, p):
        '''
        Calls SkinsContainer.getSkinByName().
        '''
        self.getSkinByPath(p, raise_exc=1)

    security.declareProtected(AccessContentsInformation, 'getSkinPath')
    def getSkinPath(self, name):
        '''
        Converts a skin name to a skin path.  Used by SkinsContainer.
        '''
        sels = self._getSelections()
        p = sels.get(name, None)
        if p is None:
            if self.allow_any:
                return name
        return p  # Can be None

    security.declareProtected(AccessContentsInformation, 'getDefaultSkin')
    def getDefaultSkin(self):
        '''
        Returns the default skin name.  Used by SkinsContainer.
        '''
        return self.default_skin

    security.declareProtected(AccessContentsInformation, 'getRequestVarname')
    def getRequestVarname(self):
        '''
        Returns the variable name to look for in the REQUEST.  Used by
        SkinsContainer.
        '''
        return self.request_varname

    security.declareProtected(AccessContentsInformation, 'getAllowAny')
    def getAllowAny(self):
        '''
        Used by the management UI.  Returns a flag indicating whether
        users are allowed to use arbitrary skin paths.
        '''
        return self.allow_any

    security.declareProtected(AccessContentsInformation, 'getSkinPaths')
    def getSkinPaths(self):
        '''
        Used by the management UI.  Returns the list of skin name to
        skin path mappings as a sorted list of tuples.
        '''
        sels = self._getSelections()
        rval = []
        for key, value in sels.items():
            rval.append((key, value))
        rval.sort()
        return rval

    security.declarePublic('getSkinSelections')
    def getSkinSelections(self):
        '''
        Returns the sorted list of available skin names.
        '''
        sels = self._getSelections()
        rval = list(sels.keys())
        rval.sort()
        return rval

    security.declareProtected('View', 'updateSkinCookie')
    def updateSkinCookie(self):
        '''
        If needed, updates the skin cookie based on the member preference.
        '''
        pm = getToolByName(self, 'portal_membership')
        member = pm.getAuthenticatedMember()
        if hasattr(aq_base(member), 'portal_skin'):
            mskin = member.portal_skin
            if mskin:
                req = self.REQUEST
                cookie = req.cookies.get(self.request_varname, None)
                if cookie != mskin:
                    resp = req.RESPONSE
                    expires = (DateTime('GMT') + 365).rfc822()
                    resp.setCookie(self.request_varname, mskin,
                                   path='/', expires=expires)
                    # Ensure updateSkinCookie() doesn't try again
                    # within this request.
                    req.cookies[self.request_varname] = mskin
                    req[self.request_varname] = mskin
                    return 1
        return 0

    security.declareProtected(ManagePortal, 'addSkinSelection')
    def addSkinSelection(self, skinname, skinpath, test=0, make_default=0):
        '''
        Adds a skin selection.
        '''
        sels = self._getSelections()
        skinpath = str(skinpath)
        if test:
            self.testSkinPath(skinpath)
        sels[str(skinname)] = skinpath
        if make_default:
            self.default_skin = skinname

Globals.InitializeClass(SkinsTool)
