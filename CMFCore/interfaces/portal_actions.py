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

"""Actions tool interface description.
$Id$
"""
__version__='$Revision$'[11:-2]

from Interface import Base, Attribute

class portal_actions(Base):
    '''Gathers a list of links which the user is allowed to view according to
    the current context.
    '''
    id = Attribute('id', 'Must be set to "portal_actions"')

    # listActionProviders__roles__ = ( 'Manager', )
    def listActionProviders():
        """ Lists all action provider names registered with the 
        actions tool.
        """

    # addActionProvider__roles__ = ( 'Manager', )
    def addActionProvider( provider_name ):
        """ Add a new action provider to the providers known by the actions
        tool. A provider must implement listActions.
        The provider is only added is the actions tool can find the 
        object corresponding to the provider_name
        """

    # deleteActionProvider__roles__ = ( 'Manager', )
    def deleteActionProvider( provider_name ):
        """ Deletes an action provider name from the providers known to
        the actions tool. The deletion only takes place if provider_name
        is actually found among the known action providers.
        """

    # listFilteredActionsFor__roles__ = None
    def listFilteredActionsFor(object):
        '''Gets all actions available to the user and returns a mapping
        containing a list of user actions, folder actions, object actions,
        and global actions.  Each action has the following keys:
           name: An identifying action name
           url: The URL to visit to access the action
           permissions: A list. The user must have at least of the listed
             permissions to access the action.  If the list is empty,
             the user is allowed.  (Note that listFilteredActions() filters
             out actions according to this field.)
           category: One of "user", "folder", "object", or "globals".
        '''

    # listFilteredActions__roles__ = None
    def listFilteredActions():
        '''Gets all actions available to the user in no particular context.
        '''


class ActionProvider(Base):
    '''The interface expected of an object that can provide actions.
    '''

    # listActions__roles__ = ()  # No permission.
    def listActions(info):
        '''Returns a list of mappings describing actions.  Each action
        should contain the keys "name", "url", "permissions", and
        "category", conforming to the specs outlined in
        portal_actions.listFilteredActionsFor().  The info argument
        contains at least the following attributes, some of which
        may be set to "None":

          isAnonymous
          portal
          portal_url
          folder
          folder_url
          content
          content_url
        '''

