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

"""Basic action list tool.

$Id$
"""
__version__='$Revision$'[11:-2]

from utils import SimpleItemWithProperties, _dtmldir, getToolByName
import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner, aq_parent
from Globals import InitializeClass, DTMLFile

class ActionInformation(SimpleItemWithProperties):
    """
    Represent a single action which the user can select from a list
    and execut in some context.
    """
    _isActionInformation = 1
    __allow_access_to_unprotected_subobjects__ = 1

    manage_options = (SimpleItemWithProperties.manage_options[:1] +
                      ({'label': 'Actions',
                       'action': 'manage_editActionsForm'},) +
                       SimpleItemWithProperties.manage_options[1:])
    security = ClassSecurityInfo()
    security.declareProtected(CMFCorePermissions.ManagePortal
                            , 'manage_editProperties'
                            , 'manage_changeProperties'
                            , 'manage_propertiesForm'
                             )

    _basic_properties = (
                         {'id': 'title', 'type': 'string', 'mode': 'w', 'label': 'Title'}
                       , {'id': 'description', 'type': 'text', 'mode': 'w', 
                         'label': 'Description'}
                       , {'id': 'category', 'type': 'string', 'mode': 'w', 
                         'label': 'Category'}
                       , {'id': 'priority', 'type': 'boolean', 'mode':  'w', 'label': 'Priority'}
                         )

    title = ''
    description = ''
    category = ''
    priority = 0
    visible = 1
    _action = ''

    def __init__(self
               , id
               , title=''
               , description=''
               , category='object'
               , condition=''
               , permissions=()
               , priority=10
               , visible=1
               , action=''):
       """
       Setup an instance
       """
       self.id = id
       self.title = title
       self.description = description
       self.category = category 
       self.condition = condition
       self.permissions = permissions
       self.priority = priority 
       self.visible = visible
       self._action = action


    security.declareProtected(CMFCorePermissions.View, 'Title')
    def Title(self):
        """
        Return the Action title - name
        """
        if self.title:
            return self.title
        else:
            return self.getId()

    security.declareProtected(CMFCorePermissions.View, 'Description')
    def Description(self):
        """
        Return a description of the action
        """
        return self.description

    security.declarePrivate('testCondition')
    def testCondition(self, ec):
        """
        Evaluate condition and return 0 or 1
        """
        if self.condition:
            return self.condition(ec)
        else:
            return 1

    security.declarePublic('getAction')
    def getAction(self, ec):
        """
        Return the action, which is an TALES expresssion
        """
        if self._action:
            aa = self._action(ec)
        else:
            aa = ''
        action = {}
        action['id'] = self.id
        action['name'] = self.Title()
        action['url'] = aa 
        action['permissions'] = self.getPermissions()
        action['category'] = self.getCategory()
        action['visible'] = self.getVisibility()
        return action 

    security.declarePublic('getActionExpression')
    def getActionExpression(self):
        """
        If not an empty string or None, return the 
        text of the expression otherwise return '' 
        """
        if self._action:
            return self._action.text
        else:
            return self._action

    security.declarePublic('getCondition')
    def getCondition(self):
        """
        If not an empty string or None, return the 
        text of the expression otherwise
        return ''
        """
        if self.condition:
            return self.condition.text
        else:
            return self.condition

    security.declarePublic('getPermission')
    def getPermissions(self):
        """
        Return the permission if any required for a user to
        execute the action
        """
        return self.permissions

    security.declarePublic('getCategory')
    def getCategory(self):
        """
        Return the category for which the action is
        """
        if self.category:
            return self.category
        else:
            return 'object'

    security.declarePublic('getVisibility')
    def getVisibility(self):
        """
        Return boolean for whether the action
        is visible in the UI
        """
        return self.visible

    security.declarePublic('getPriority')
    def getPriority(self):
        """
        Return integer priority for sorting
        Not used....keep and implement or toss?
        """
        if self.priority:
            return self.priority
        else:
            return 10

InitializeClass(ActionInformation)

class oai:
    #Provided for backwards compatability
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

