##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
""" Implement a shared base for tools which provide actions.

$Id$
"""

from Globals import DTMLFile, InitializeClass
from AccessControl import ClassSecurityInfo

from ActionInformation import ActionInformation
from CMFCorePermissions import ManagePortal
from Expression import Expression
from utils import _dtmldir

from interfaces.portal_actions import ActionProvider as IActionProvider


class ActionProviderBase:
    """ Provide ActionTabs and management methods for ActionProviders
    """

    __implements__ = IActionProvider

    security = ClassSecurityInfo()

    _actions = ()

    _actions_form = DTMLFile( 'editToolsActions', _dtmldir )

    manage_options = ( { 'label' : 'Actions'
                       , 'action' : 'manage_editActionsForm'
                       }
                     , 
                     )

    #
    #   ActionProvider interface
    #
    security.declarePrivate( 'listActions' )
    def listActions( self, info=None ):
        """ Return all the actions defined by a provider.
        """
        return self._actions or ()

    #
    #   ZMI methods
    #
    security.declareProtected( ManagePortal, 'manage_editActionsForm' )
    def manage_editActionsForm( self, REQUEST, manage_tabs_message=None ):

        """ Show the 'Actions' management tab.

        Bug note: Note that this method, when called by Management.py's
        manage_workspace (when it is the first action of an object),
        will be called with REQUEST equal to 'self' and
        manage_tabs_message equal to the REQUEST.  This causes the
        request to be printed by manage_tabs, because it considers
        'manage_tabs_message' to be true.  The fix would be to remove
        this method and put it all into DTML (probably easiest) or to
        make manage_workspace sniff at the method it obtains to make sure
        it's a DTMLFile before passing along self and REQUEST. I don't
        care too much either way, and I'm too lazy to fix it at the moment.
        - chrism
        
        """
        actions = []

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
            a1['action'] = a.getActionExpression()
            a1['condition'] = a.getCondition()
            actions.append(a1)

        # possible_permissions is in AccessControl.Role.RoleManager.
        pp = self.possible_permissions()
        return self._actions_form( self
                                 , REQUEST
                                 , actions=actions
                                 , possible_permissions=pp
                                 , management_view='Actions'
                                 , manage_tabs_message=manage_tabs_message
                                 )

    security.declareProtected( ManagePortal, 'addAction' )
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
        """ Add an action to our list.
        """
        if not name:
            raise ValueError('A name is required.')

        a_expr = action and Expression(text=str(action)) or ''
        c_expr = condition and Expression(text=str(condition)) or ''

        if type( permission ) != type( () ):
            permission = permission and (str(permission),) or ()

        new_actions = self._cloneActions()

        new_action = ActionInformation( id=str(id)
                                      , title=str(name)
                                      , action=a_expr
                                      , condition=c_expr
                                      , permissions=permission
                                      , category=str(category)
                                      , visible=int(visible)
                                      )

        new_actions.append( new_action )
        self._actions = tuple( new_actions )

        if REQUEST is not None:
            return self.manage_editActionsForm(
                REQUEST, manage_tabs_message='Added.')

    security.declareProtected( ManagePortal, 'changeActions' )
    def changeActions( self, properties=None, REQUEST=None ):

        """ Update our list of actions.
        """
        if properties is None:
            properties = REQUEST

        actions = []

        for index in range( len( self._actions ) ):
            actions.append( self._extractAction( properties, index ) )

        self._actions = tuple( actions )

        if REQUEST is not None:
            return self.manage_editActionsForm(REQUEST, manage_tabs_message=
                                               'Actions changed.')

    security.declareProtected( ManagePortal, 'deleteActions' )
    def deleteActions( self, selections=(), REQUEST=None ):

        """ Delete actions indicated by indexes in 'selections'.
        """
        sels = list( map( int, selections ) )  # Convert to a list of integers.

        old_actions = self._cloneActions()
        new_actions = []

        for index in range( len( old_actions ) ):
            if index not in sels:
                new_actions.append( old_actions[ index ] )

        self._actions = tuple( new_actions )

        if REQUEST is not None:
            return self.manage_editActionsForm(
                REQUEST, manage_tabs_message=(
                'Deleted %d action(s).' % len(sels)))

    security.declareProtected( ManagePortal, 'moveUpActions' )
    def moveUpActions( self, selections=(), REQUEST=None ):

        """ Move the specified actions up one slot in our list.
        """
        sels = list( map( int, selections ) )  # Convert to a list of integers.
        sels.sort()

        new_actions = self._cloneActions()

        for idx in sels:
            idx2 = idx - 1
            if idx2 < 0:
                # Wrap to the bottom.
                idx2 = len(new_actions) - 1
            # Swap.
            a = new_actions[idx2]
            new_actions[idx2] = new_actions[idx]
            new_actions[idx] = a

        self._actions = tuple( new_actions )

        if REQUEST is not None:
            return self.manage_editActionsForm(
                REQUEST, manage_tabs_message=(
                'Moved up %d action(s).' % len(sels)))

    security.declareProtected( ManagePortal, 'moveDownActions' )
    def moveDownActions( self, selections=(), REQUEST=None ):

        """ Move the specified actions down one slot in our list.
        """
        sels = list( map( int, selections ) )  # Convert to a list of integers.
        sels.sort()
        sels.reverse()

        new_actions = self._cloneActions()

        for idx in sels:
            idx2 = idx + 1
            if idx2 >= len(new_actions):
                # Wrap to the top.
                idx2 = 0
            # Swap.
            a = new_actions[idx2]
            new_actions[idx2] = new_actions[idx]
            new_actions[idx] = a

        self._actions = tuple( new_actions )

        if REQUEST is not None:
            return self.manage_editActionsForm(
                REQUEST, manage_tabs_message=(
                'Moved down %d action(s).' % len(sels)))

    #
    #   Helper methods
    #
    security.declarePrivate( '_cloneActions' )
    def _cloneActions( self ):

        """ Return a list of actions, cloned from our current list.
        """
        return map( lambda x: x.clone(), list( self._actions ) )
 
    security.declarePrivate( '_extractAction' )
    def _extractAction( self, properties, index ):

        """ Extract an ActionInformation from the funky form properties.
        """
        id          = str( properties.get( 'id_%d'          % index, '' ) )
        name        = str( properties.get( 'name_%d'        % index, '' ) )
        action      = str( properties.get( 'action_%d'      % index, '' ) )
        condition   = str( properties.get( 'condition_%d'   % index, '' ) )
        category    = str( properties.get( 'category_%d'    % index, '' ))
        visible     =      properties.get( 'visible_%d'     % index, 0  )
        permissions =      properties.get( 'permission_%d'  % index, () )

        if not name:
            raise ValueError('A name is required.')

        if action is not '':
            action = Expression( text=action )

        if condition is not '':
            condition = Expression( text=condition )

        if category == '':
            category = 'object'

        if type( visible ) is not type( 0 ):
            try:
                visible = int( visible )
            except:
                visible = 0

        if type( permissions ) is type( '' ):
            permissions = ( permissions, )

        return ActionInformation( id=id
                                , title=name
                                , action=action
                                , condition=condition
                                , permissions=permissions
                                , category=category
                                , visible=visible
                                )

InitializeClass(ActionProviderBase)
