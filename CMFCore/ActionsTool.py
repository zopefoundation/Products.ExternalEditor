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
""" Basic action list tool.

$Id$
"""

from Globals import InitializeClass, DTMLFile, package_home
from Acquisition import aq_base, aq_inner, aq_parent
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
from OFS.SimpleItem import SimpleItem

from Expression import Expression, createExprContext
from ActionInformation import ActionInformation, oai
from ActionProviderBase import ActionProviderBase
from TypesTool import TypeInformation
from CMFCorePermissions import ManagePortal
from utils import _checkPermission
from utils import _dtmldir
from utils import getToolByName
from utils import SimpleItemWithProperties
from utils import UniqueObject

from interfaces.portal_actions import portal_actions as IActionsTool


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
               text='string: ${folder_url}/folder_contents')
                                , condition=Expression(
               text='python: folder is not object') 
                                , permissions=('List folder contents',)
                                , category='object'
                                , visible=1
                                 )
              , ActionInformation(id='folderContents'
                                , title='Folder contents'
                                , action=Expression(
               text='string: ${folder_url}/folder_contents')
                                , condition=Expression(
               text='python: folder is object')
                                , permissions=('List folder contents',)
                                , category='folder'
                                , visible=1
                                 )
               )

    action_providers = ( 'portal_membership'
                       , 'portal_actions'
                       , 'portal_registration'
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
        """
        Return a sequence of action providers known by this tool.
        """
        return self.action_providers

    security.declareProtected(ManagePortal, 'addActionProvider')
    def addActionProvider( self, provider_name ):
        """
        Add the name of a new action provider.
        """
        ap = list( self.action_providers )
        if hasattr( self, provider_name ) and provider_name not in ap:
            ap.append( provider_name )
            self.action_providers = tuple( ap )

    security.declareProtected(ManagePortal, 'deleteActionProvider')
    def deleteActionProvider( self, provider_name ):
        """
        Remove an action provider.
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
        """
        Return a mapping containing of all actions available to the
        user against object, bucketing into categories.
        """
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
        ec = createExprContext(folder, portal, object)
        actions = []
        append = actions.append
        info = oai(self, folder, object)
        # Include actions from specific tools.
        for provider_name in self.listActionProviders():
            provider = getattr(self, provider_name)
            self._listActions(append,provider,info,ec)

        # Include actions from object.
        if object is not None:
            base = aq_base(object)
            types_tool = getToolByName( self, 'portal_types' )
            # we might get None back from getTypeInfo.  We construct
            # a dummy TypeInformation object here in that case (the 'or'
            # case).  This prevents us from needing to check the condition.
            ti = types_tool.getTypeInfo( object ) or TypeInformation('Dummy')
            defs = ti.getActions()
            url = object_url = object.absolute_url()
            for d in defs:
                # we can't modify or expose the original actionsd... this
                # stems from the fact that getActions returns a ref to the
                # actual dictionary used to store actions instead of a
                # copy.  We copy it here to prevent it from being modified.
                d = d.copy()
                d['id'] = d.get('id', None)
                if d['action']:
                    url = '%s/%s' % (object_url, d['action'])
                d['url'] = url
                d['category'] = d.get('category', 'object')
                d['visible'] = d.get('visible', 1)
                actions.append(d)

            if hasattr(base, 'listActions'):
                self._listActions(append,object,info,ec)

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
                # startswith() is used so that we can have several
                # different categories that are checked in the object or
                # folder context.
                if (object is not None and
                    (category.startswith('object') or
                     category.startswith('workflow'))):
                    context = object
                elif (folder is not None and
                      category.startswith('folder')):
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
                # Filter out duplicate actions by identity...
                if not action in catlist:
                    catlist.append(action)
                # ...should you need it, here's some code that filters
                # by equality (use instead of the two lines above)
                #if not [a for a in catlist if a==action]:
                #    catlist.append(action)
        return filtered_actions

    # listFilteredActions() is an alias.
    security.declarePublic('listFilteredActions')
    listFilteredActions = listFilteredActionsFor

    #
    #   Helper methods
    #
    def _listActions(self,append,object,info,ec):
        a = object.listActions(info)
        if a and type(a[0]) is not type({}):
            for ai in a:
                if ai.testCondition(ec):
                    append(ai.getAction(ec))
        else:
            for i in a:
                append(i)
        

InitializeClass(ActionsTool)
