##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Basic action list tool.

$Id$
"""

from AccessControl import ClassSecurityInfo
from Globals import DTMLFile
from Globals import InitializeClass
from OFS.Folder import Folder

from ActionInformation import ActionInformation
from ActionProviderBase import ActionProviderBase
from Expression import Expression
from interfaces.portal_actions import ActionProvider as IActionProvider
from interfaces.portal_actions import portal_actions as IActionsTool
from permissions import ListFolderContents
from permissions import ManagePortal
from utils import _dtmldir
from utils import SimpleItemWithProperties
from utils import UniqueObject


class ActionsTool(UniqueObject, Folder, ActionProviderBase):
    """
        Weave together the various sources of "actions" which are apropos
        to the current user and context.
    """

    __implements__ = (IActionsTool, ActionProviderBase.__implements__)

    id = 'portal_actions'
    meta_type = 'CMF Actions Tool'
    _actions = (ActionInformation(id='folderContents'
                                , title='Folder contents'
                                , action=Expression(
               text='string:${folder_url}/folder_contents')
                                , condition=Expression(
               text='python: folder is not object')
                                , permissions=(ListFolderContents,)
                                , category='folder'
                                , visible=1
                                 )
               ,
               )

    action_providers = ( 'portal_membership'
                       , 'portal_actions'
                       , 'portal_registration'
                       , 'portal_types'
                       , 'portal_discussion'
                       , 'portal_undo'
                       , 'portal_syndication'
                       , 'portal_workflow'
                       , 'portal_properties'
                       )

    security = ClassSecurityInfo()

    manage_options = ( ActionProviderBase.manage_options
                     + ( { 'label' : 'Action Providers'
                         , 'action' : 'manage_actionProviders'
                         }
                       , { 'label' : 'Overview'
                         , 'action' : 'manage_overview'
                         }
                     ) + Folder.manage_options
                     )

    #
    #   ZMI methods
    #
    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = DTMLFile( 'explainActionsTool', _dtmldir )
    manage_actionProviders = DTMLFile('manageActionProviders', _dtmldir)

    security.declareProtected(ManagePortal, 'manage_aproviders')
    def manage_aproviders(self
                        , apname=''
                        , chosen=()
                        , add_provider=0
                        , del_provider=0
                        , REQUEST=None):
        """
        Manage action providers through-the-web.
        """
        providers = list(self.listActionProviders())
        new_providers = []
        if add_provider:
            providers.append(apname)
        elif del_provider:
            for item in providers:
                if item not in chosen:
                    new_providers.append(item)
            providers = new_providers
        self.action_providers = tuple(providers)
        if REQUEST is not None:
            return self.manage_actionProviders(self , REQUEST
                          , manage_tabs_message='Providers changed.')

    #
    #   Programmatically manipulate the list of action providers
    #
    security.declareProtected(ManagePortal, 'listActionProviders')
    def listActionProviders(self):
        """ List the ids of all Action Providers queried by this tool.
        """
        return self.action_providers

    security.declareProtected(ManagePortal, 'addActionProvider')
    def addActionProvider( self, provider_name ):
        """ Add an Action Provider id to the providers queried by this tool.
        """
        ap = list( self.action_providers )
        if hasattr( self, provider_name ) and provider_name not in ap:
            ap.append( provider_name )
            self.action_providers = tuple( ap )

    security.declareProtected(ManagePortal, 'deleteActionProvider')
    def deleteActionProvider( self, provider_name ):
        """ Delete an Action Provider id from providers queried by this tool.
        """
        ap = list( self.action_providers )
        if provider_name in ap:
            ap.remove( provider_name )
            self.action_providers = tuple( ap )

    #
    #   'portal_actions' interface methods
    #
    security.declarePublic('listFilteredActionsFor')
    def listFilteredActionsFor(self, object=None):
        """ List all actions available to the user.
        """
        actions = []

        # Include actions from specific tools.
        for provider_name in self.listActionProviders():
            provider = getattr(self, provider_name)
            if IActionProvider.isImplementedBy(provider):
                actions.extend( provider.listActionInfos(object=object) )

        # Include actions from object.
        if object is not None:
            if IActionProvider.isImplementedBy(object):
                actions.extend( object.listActionInfos(object=object) )

        # Reorganize the actions by category.
        filtered_actions={'user':[],
                          'folder':[],
                          'object':[],
                          'global':[],
                          'workflow':[],
                          }
        for action in actions:
            category = action['category']
            catlist = filtered_actions.get(category, None)
            if catlist is None:
                filtered_actions[category] = catlist = []
            catlist.append(action)
            # ...should you need it, here's some code that filters
            # by equality (use instead of the line above)
            #if not action in catlist:
            #    catlist.append(action)
        return filtered_actions

InitializeClass(ActionsTool)
