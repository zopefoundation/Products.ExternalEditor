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

from OFS.SimpleItem import SimpleItem
from Globals import DTMLFile
from CMFCorePermissions import ManagePortal
from utils import _dtmldir, cookString
from AccessControl import ClassSecurityInfo
from ActionInformation import ActionInformation
from Expression import Expression


"""Basic action list tool.

$Id$
"""
__version__='$Revision$'[11:-2]

class ActionProviderBase:
    """
    Provide ActionTabs and management methods for ActionProviders
    """
    _actions = []
    security = ClassSecurityInfo()
    _actions_form = DTMLFile( 'editToolsActions', _dtmldir )

    manage_options = ({ 'label' : 'Actions', 'action' : 'manage_editActionsForm' }
                    , 
                     )

    security.declarePrivate('listActions')
    def listActions(self):
        """
        Return all the actions defined by a tool
        """
        if self._actions:
            return self._actions
        else:
            return None

    security.declareProtected(ManagePortal, 'manage_editActionsForm')
    def manage_editActionsForm(self, REQUEST, manage_tabs_message=None):
        """
        Shows the 'Actions' management tab.
        """
        actions = []
        if self.listActions() is not None:
            for a in self.listActions():
                a1 = {}
                a1['id'] = a.getId()
                a1['name'] = a.Title()
                p = a.getPermissions()
                if p:
                    a1['permission'] = p[0]
                else:
                    a1['permission'] = ''
                a1['category'] = a.getCategory() or 'object'
                a1['visible'] = a.getVisibility()
                if a._action:
                    a1['action'] = a.getActionExpression()
                else:
                    a1['action'] = ''
                if a.condition:
                    a1['condition'] = a.getCondition()
                else:
                    a1['condition'] = ''
                actions.append(a1)
                # possible_permissions is in AccessControl.Role.RoleManager.
        pp = self.possible_permissions()
        return self._actions_form(self, REQUEST,
                                  actions=actions,
                                  possible_permissions=pp,
                                  management_view='Actions',
                                  manage_tabs_message=manage_tabs_message)

    security.declareProtected(ManagePortal, 'addAction')
    def addAction( self
                 , id
                 , name
                 , action
                 , condition
                 , permission
                 , category
                 , visible=1
                 , REQUEST=None
                 ):
        """
        Adds an action to the list.
        """
        al = self._actions[:]
        if not name:
            raise ValueError('A name is required.')
        if action:
            a_expr = Expression(text=str(action))
        else:
            a_expr = ''
        if condition:
            c_expr = Expression(text=str(condition))
        else:
            c_expr = ''
        al.append(ActionInformation(id=str(id)
                                         , title=str(name)
                                         , action=a_expr
                                         , condition=c_expr
                                         , permissions=(str(permission),)
                                         , category=str(category)
                                         , visible=int(visible)
                                          ))
        self._actions = al
        if REQUEST is not None:
            return self.manage_editActionsForm(
                REQUEST, manage_tabs_message='Added.')
    
    security.declareProtected(ManagePortal, 'changeActions')
    def changeActions(self, properties=None, REQUEST=None):
        """
        Changes the _actions.
        """
        if properties is None:
            properties = REQUEST
        actions = self._actions[:]
        for idx in range(len(actions)):
            s_idx = str(idx)
            action = {
                'id': str(properties.get('id_' + s_idx, '')),
                'name': str(properties.get('name_' + s_idx, '')),
                'action': str(properties.get('action_' + s_idx, '')),
                'condition': str(properties.get('condition_' + s_idx, '')),
                'permissions':
                (properties.get('permission_' + s_idx, ()),),
                'category': str(properties.get('category_' + s_idx, 'object')),
                'visible': properties.get('visible_' + s_idx, 0),
                }
            if not action['name']:
                raise ValueError('A name is required.')
            a = actions[idx]
            a.id = action['id']
            a.title = action['name']
            if action['action'] is not '':
                a._action = Expression(text=action['action'])
            else:
                a._action = ''
            if action['condition'] is not '':
                a.condition = Expression(text=action['condition'])
            else:
                a.condition = ''
            a.permissions = action['permissions']
            a.category = action['category']
            a.visible = action['visible']
        self._actions = actions
        if REQUEST is not None:
            return self.manage_editActionsForm(REQUEST, manage_tabs_message=
                                               'Actions changed.')

    security.declareProtected(ManagePortal, 'deleteActions')
    def deleteActions(self, selections=(), REQUEST=None):
        """
        Deletes actions.
        """
        actions = self._actions[:]
        sels = list(map(int, selections))  # Convert to a list of integers.
        sels.sort()
        sels.reverse()
        for idx in sels:
            del actions[idx]
        self._actions = actions
        if REQUEST is not None:
            return self.manage_editActionsForm(
                REQUEST, manage_tabs_message=(
                'Deleted %d action(s).' % len(sels)))

    security.declareProtected(ManagePortal, 'moveUpActions')
    def moveUpActions(self, selections=(), REQUEST=None):
        """
        Moves the specified actions up one slot.
        """
        actions = list(self._actions)
        sels = list(map(int, selections))  # Convert to a list of integers.
        sels.sort()
        for idx in sels:
            idx2 = idx - 1
            if idx2 < 0:
                # Wrap to the bottom.
                idx2 = len(actions) - 1
            # Swap.
            a = actions[idx2]
            actions[idx2] = actions[idx]
            actions[idx] = a
        self._actions = actions
        if REQUEST is not None:
            return self.manage_editActionsForm(
                REQUEST, manage_tabs_message=(
                'Moved up %d action(s).' % len(sels)))

    security.declareProtected(ManagePortal, 'moveDownActions')
    def moveDownActions(self, selections=(), REQUEST=None):
        """
        Moves the specified actions down one slot.
        """
        actions = list(self._actions)
        sels = list(map(int, selections))  # Convert to a list of integers.
        sels.sort()
        sels.reverse()
        for idx in sels:
            idx2 = idx + 1
            if idx2 >= len(actions):
                # Wrap to the top.
                idx2 = 0
            # Swap.
            a = actions[idx2]
            actions[idx2] = actions[idx]
            actions[idx] = a
        self._actions = actions
        if REQUEST is not None:
            return self.manage_editActionsForm(
                REQUEST, manage_tabs_message=(
                'Moved down %d action(s).' % len(sels)))
