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
""" Actions tool interface.

$Id$
"""

from Interface import Attribute
try:
    from Interface import Interface
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import Base as Interface


class portal_actions(Interface):
    """ Gathers a list of links which the user is allowed to view according to
    the current context.
    """
    id = Attribute('id', 'Must be set to "portal_actions"')

    def listActionProviders():
        """ List the ids of all Action Providers queried by this tool.

        Permission -- Manage portal

        Returns -- Tuple of Action Provider ids
        """

    def addActionProvider(provider_name):
        """ Add an Action Provider id to the providers queried by this tool.

        A provider must implement the ActionProvider Interface.
        OldstyleActionProviders are currently also supported.

        The provider is only added if the actions tool can find the object
        corresponding to the provider_name.

        Permission -- Manage portal
        """

    def deleteActionProvider(provider_name):
        """ Delete an Action Provider id from providers queried by this tool.

        The deletion only takes place if provider_name is actually found among
        the known action providers.

        Permission -- Manage portal
        """

    def listFilteredActionsFor(object=None):
        """ List all actions available to the user.

        Each action has the following keys:

        - name: An identifying action name

        - url: The URL to visit to access the action

        - permissions: A list. The user must have at least one of the listed
          permissions to access the action. If the list is empty, the user is
          allowed. (Note that listFilteredActionsFor() filters out actions
          according to this field.)

        - category: One of "user", "folder", "object", "global" or "workflow"

        Permission -- Always available

        Returns -- Dictionary of category / action list pairs.
        """

    def listFilteredActions(object=None):
        """ Deprecated alias of listFilteredActionsFor.
        """


class ActionProvider(Interface):
    """ The interface expected of an object that can provide actions.
    """

    def listActions(info=None):
        """ List all the actions defined by a provider.

        The info argument is currently used by 'CMF Types Tool'. It contains
        at least a 'content' attribute.

        Returns -- Tuple of ActionInformation objects
        """


class OldstyleActionProvider(Interface):
    """ Deprecated interface expected of an object that can provide actions.

    Still used by 'Oldstyle CMF Discussion Tool' and 'CMF Workflow Tool'.
    """

    def listActions(info):
        """ List all the actions defined by a provider.

        Each action should contain the keys "name", "url", "permissions" and
        "category", conforming to the specs outlined in
        portal_actions.listFilteredActionsFor(). The info argument contains
        at least the following attributes, some of which may be set to "None":

        - isAnonymous

        - portal

        - portal_url

        - folder

        - folder_url

        - content

        - content_url

        Returns -- Tuple of mappings describing actions
        """
