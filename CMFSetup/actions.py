##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Classes:  ActionsProviderConfigurator

$Id$
"""

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.ActionProviderBase import IActionProvider
from Products.CMFCore.utils import getToolByName

from permissions import ManagePortal
from utils import _xmldir
from utils import ConfiguratorBase
from utils import CONVERTER, DEFAULT, KEY


#
#   Configurator entry points
#
_FILENAME = 'actions.xml'

def importActionProviders( context ):

    """ Import action providers and their actions from an XML file.

    o 'context' must implement IImportContext.

    o Register via Python:

      registry = site.portal_setup.getImportStepRegistry()
      registry.registerStep( 'importActionProviders'
                           , '20040518-01'
                           , Products.CMFSetup.actions.importActionProviders
                           , ()
                           , 'Action Provider import'
                           , 'Import  action providers registered with '
                             'the actions tool, and their actions.'
                           )

    o Register via XML:

      <setup-step id="importActionProviders"
                  version="20040524-01"
                  handler="Products.CMFSetup.actions.importActionProviders"
                  title="Action Provider import"
      >Import action providers registered with the actions tool,
       and their actions.</setup-step>

    """
    site = context.getSite()
    encoding = context.getEncoding()

    actions_tool = getToolByName( site, 'portal_actions' )

    if context.shouldPurge():

        for provider_id in actions_tool.listActionProviders():
            actions_tool.deleteActionProvider( provider_id )

    text = context.readDataFile( _FILENAME )

    if text is not None:

        apc = ActionProvidersConfigurator( site, encoding )
        tool_info = apc.parseXML( text )

        for p_info in tool_info[ 'providers' ]:

            if p_info[ 'id' ] not in actions_tool.listActionProviders():

                actions_tool.addActionProvider( p_info[ 'id' ] )

            provider = getToolByName( site, p_info[ 'id' ] )
            provider._actions = [ ActionInformation(**a_info)
                                  for a_info in p_info[ 'actions' ] ]

    return 'Action providers imported.'

def exportActionProviders( context ):

    """ Export action providers and their actions as an XML file

    o 'context' must implement IExportContext.

    o Register via Python:

      registry = site.portal_setup.getExportStepRegistry()
      registry.registerStep( 'exportActionProviders'
                           , Products.CMFSetup.actions.exportActionProviders
                           , 'Action Provider export'
                           , 'Export action providers registered with '
                             'the actions tool, and their actions.'
                           )

    o Register via XML:

      <export-script id="exportActionProviders"
                     version="20040518-01"
                     handler="Products.CMFSetup.actions.exportActionProviders"
                     title="Action Provider export"
      >Export action providers registered with the actions tool,
       and their actions.</export-script>

    """
    site = context.getSite()
    apc = ActionProvidersConfigurator( site ).__of__( site )
    text = apc.generateXML()

    context.writeDataFile( _FILENAME, text, 'text/xml' )

    return 'Action providers exported.'


class ActionProvidersConfigurator(ConfiguratorBase):
    """ Synthesize XML description of site's action providers.
    """
    security = ClassSecurityInfo()

    security.declareProtected( ManagePortal, 'listProviderInfo' )
    def listProviderInfo( self ):

        """ Return a sequence of mappings for each action provider.
        """
        actions_tool = getToolByName( self._site, 'portal_actions' )
        result = []

        for provider_id in actions_tool.listActionProviders():

            provider_info = { 'id' : provider_id, 'actions' : [] }
            result.append( provider_info )

            provider = getToolByName( self._site, provider_id )

            if not IActionProvider.isImplementedBy( provider ):
                continue

            actions = provider.listActions()

            if actions and isinstance(actions[0], dict):
                continue

            provider_info['actions'] = [ ai.getMapping() for ai in actions ]

        return result

    def _getExportTemplate(self):

        return PageTemplateFile('apcExport.xml', _xmldir)

    def _getImportMapping(self):

        return {
          'actions-tool':
             { 'action-provider': {KEY: 'providers'} },
          'action-provider':
             { 'id':              {},
               'action':          {KEY: 'actions', DEFAULT: ()} },
          'action':
             { 'action_id':       {KEY: 'id'},
               'title':           {},
               'description':     {CONVERTER: self._convertToUnique},
               'category':        {},
               'condition_expr':  {KEY: 'condition'},
               'permission':      {KEY: 'permissions', DEFAULT: ()},
               'category':        {},
               'visible':         {CONVERTER: self._convertToBoolean},
               'url_expr':        {KEY: 'action'} },
          'permission':
             { '#text':           {KEY: None} } }

InitializeClass(ActionProvidersConfigurator)
