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

"""Basic action list tool.

$Id$
"""
__version__='$Revision$'[11:-2]


from utils import UniqueObject, _getAuthenticatedUser, _checkPermission
from utils import getToolByName, _dtmldir
import CMFCorePermissions
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass, DTMLFile, package_home
from urllib import quote
from Acquisition import aq_base, aq_inner, aq_parent
from AccessControl import ClassSecurityInfo
from string import join

class ActionInformation:
    # Provides information that may be needed when constructing the list of
    # available actions.
    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, tool, folder, object=None):
        self.portal = portal = aq_parent(aq_inner(tool))
        membership = getToolByName(tool, 'portal_membership')
        self.isAnonymous = membership.isAnonymousUser()
        self.portal_url = portal.absolute_url()
        if folder is not None:
            self.folder_url = folder.absolute_url()
            self.folder = folder
        else:
            self.folder_url = self.portal_url
            self.folder = portal
        self.content = object
        if object is not None:
            self.content_url = object.absolute_url()
        else:
            self.content_url = None

    def __getitem__(self, name):
        # Mapping interface for easy string formatting.
        if name[:1] == '_':
            raise KeyError, name
        if hasattr(self, name):
            return getattr(self, name)
        raise KeyError, name


class ActionsTool (UniqueObject, SimpleItem):
    """
        Weave together the various sources of "actions" which are apropos
        to the current user and context.
    """
    id = 'portal_actions'
    meta_type = 'CMF Actions Tool'

    action_providers = (
        'portal_actions',
        'portal_discussion',
        'portal_membership',
        'portal_workflow',
        )

    security = ClassSecurityInfo()

    manage_options = ( { 'label' : 'Overview', 'action' : 'manage_overview' }
                     , 
                     ) + SimpleItem.manage_options

    #
    #   ZMI methods
    #
    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'manage_overview' )
    manage_overview = DTMLFile( 'explainActionsTool', _dtmldir )


    #
    # Programmatically manipulate the list of action providers
    #

    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'listActionProviders'
                             )
    def listActionProviders( self ):
       """ returns a sequence of action providers known by this tool """
       return self.action_providers

    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'addActionProvider'
                             )
    def addActionProvider( self, provider_name ):
        """ add the name of a new action provider """
        if hasattr( self, provider_name ):
            p_old = self.action_providers
            p_new = p_old + ( provider_name, )
            self.action_providers = p_new

    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'deleteActionProvider'
                             )
    def deleteActionProvider( self, provider_name ):
        """ remove an action provider """
        if provider_name in self.action_providers:
            p_old = list( self.action_providers )
            del p_old[p_old.index( provider_name)]
            self.action_providers = tuple( p_old )

    #
    #   'portal_actions' interface methods
    #
    security.declarePublic('listFilteredActionsFor')
    def listFilteredActionsFor(self, object=None):
        '''Gets all actions available to the user and returns a mapping
        containing user actions, object actions, and global actions.
        '''
        portal = aq_parent(aq_inner(self))
        if object is None or not hasattr(object, 'aq_base'):
            folder = portal
        else:
            folder = object
            # Search up the containment hierarchy until we find an
            # object that claims it's a folder.
            while folder is not None:
                if getattr(aq_base(folder), 'isPrincipiaFolderish', 0):
                    # found it.
                    break
                else:
                    folder = aq_parent(aq_inner(folder))

        info = ActionInformation(self, folder, object)

        actions = []
        # Include actions from specific tools.
        for provider_name in self.action_providers:
            provider = getattr(self, provider_name)
            a = provider.listActions(info)
            if a:
                actions.extend(list(a))

        # Include actions from object.
        if object is not None:
            base = aq_base(object)
            types_tool = getToolByName( self, 'portal_types' )
            ti = types_tool.getTypeInfo( object )
            if ti is not None:
                defs = ti.getActions()
                if defs:
                    c_url = info.content_url
                    for d in defs:
                        a = d['action']
                        if a:
                            url = c_url + '/' + a
                        else:
                            url = c_url
                        actions.append({
                            'id': d.get('id', None),
                            'name': d['name'],
                            'url': url,
                            'permissions': d['permissions'],
                            'category': d.get('category', 'object'),
                            'visible': d.get('visible', 1),
                            })
            if hasattr(base, 'listActions'):
                a = object.listActions(info)
                if a:
                    actions.extend(list(a))

        # Reorganize the actions by category,
        # filtering out disallowed actions.
        filtered_actions={'user':[],
                          'folder':[],
                          'object':[],
                          'global':[],
                          'workflow':[],
                          }
        for action in actions:
            category = action['category']
            permissions = action.get('permissions', None)
            visible = action.get('visible', 1)
            if not visible:
                continue
            verified = 0
            if not permissions:
                # This action requires no extra permissions.
                verified = 1
            else:
                if category in ('object', 'workflow') and object is not None:
                    context = object
                elif category == 'folder' and folder is not None:
                    context = folder
                else:
                    context = portal
                for permission in permissions:
                    # The user must be able to match at least one of
                    # the listed permissions.
                    if _checkPermission(permission, context):
                        verified = 1
                        break
            if verified:
                catlist = filtered_actions.get(category, None)
                if catlist is None:
                    filtered_actions[category] = catlist = []
                # If a bug occurs where actions appear more than once,
                # a little code right here can fix it.
                catlist.append(action)
        return filtered_actions

    # listFilteredActions() is an alias.
    security.declarePublic('listFilteredActions')
    listFilteredActions = listFilteredActionsFor

    security.declarePrivate('listActions')
    def listActions(self, info):
        # This will eventually be configurable through the portal_actions UI.
        portal_url = info.portal_url
        if info.isAnonymous:
            actions = [
                {'name': 'Log in',
                 'url': portal_url + '/login_form',
                 'permissions': [],
                 'category': 'user'},
                {'name': 'Join',
                 'url': portal_url + '/join_form',
                 'permissions': [CMFCorePermissions.AddPortalMember],
                 'category': 'user'},
                ]
        else:
            actions = [
                {'name': 'Preferences',
                 'url': portal_url + '/personalize_form',
                 'permissions': [],
                 'category': 'user'},
                {'name': 'Log out',
                 'url': portal_url + '/logout',
                 'permissions' : [],
                 'category': 'user'},
                {'name': 'Undo',
                 'url': 'undo_form',
                 'permissions': ['Undo changes'],
                 'category': 'global'},
                {'name': 'Reconfigure portal',
                 'url': portal_url + '/reconfig_form',
                 'permissions': ['Manage portal'],
                 'category': 'global'},
                ]

            folder_url = info.folder_url
            content_url = info.content_url

            if folder_url is not None:
                actions.append({
                    'name': 'Folder contents',
                    'url': folder_url + '/folder_contents',
                    'permissions' : ['List folder contents'],
                    'category': 'folder',
                    })

        return actions


InitializeClass(ActionsTool)
