""" Classes:  ActionsProviderConfigurator

$Id$
"""
from xml.dom.minidom import parseString as domParseString

from AccessControl import ClassSecurityInfo
from Acquisition import Implicit
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.ActionProviderBase import IActionProvider
from Products.CMFCore.utils import getToolByName

from permissions import ManagePortal
from utils import _coalesceTextNodeChildren
from utils import _getNodeAttribute
from utils import _getNodeAttributeBoolean
from utils import _xmldir
from utils import HandlerBase

#
#   Configurator entry points
#
_FILENAME = 'actions.xml'

def importActionProviders( context ):

    """ Import action providers and their actions rom an XML file

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

        apc = ActionProvidersConfigurator( site ).__of__( site )
        info_list = apc.parseXML( text, encoding )

        for p_info in info_list:

            if p_info[ 'id' ] not in actions_tool.listActionProviders():

                actions_tool.addActionProvider( p_info[ 'id' ] )

            provider = getToolByName( site, p_info[ 'id' ] )
            provider._actions = [ ActionInformation(**a_info)
                                  for a_info in p_info['actions'] ]

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


class ActionProvidersConfigurator( Implicit ):

    """ Synthesize XML description of site's action providers.
    """
    security = ClassSecurityInfo()
    security.setDefaultAccess( 'allow' )

    def __init__( self, site ):
        self._site = site

    _providers = PageTemplateFile( 'apcExport.xml'
                                 , _xmldir
                                 , __name__='_providers'
                                 )

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

    security.declareProtected( ManagePortal, 'generateXML' )
    def generateXML( self ):

        """ Pseudo API.
        """
        return self._providers()

    security.declareProtected( ManagePortal, 'parseXML' )
    def parseXML( self, text, encoding=None ):

        """ Pseudo API.
        """
        reader = getattr( text, 'read', None )

        if reader is not None:
            text = reader()

        dom = domParseString(text)

        root = dom.getElementsByTagName('actions-tool')[0]
        return _extractActionProviderNodes(root, encoding)

InitializeClass( ActionProvidersConfigurator )


def _extractActionProviderNodes(parent, encoding=None):

    result = []

    for ap_node in parent.getElementsByTagName('action-provider'):

        id = _getNodeAttribute(ap_node, 'id', encoding)
        actions = _extractActionNodes(ap_node, encoding)

        result.append( { 'id': id, 'actions': actions } )

    return result

def _extractActionNodes(parent, encoding=None):

    result = []

    for a_node in parent.getElementsByTagName('action'):

        def _es(key):
            return _getNodeAttribute(a_node, key, encoding)

        action_id      = _es('action_id')
        title          = _es('title')
        category       = _es('category')
        condition_expr = _es('condition_expr')
        permissions    = _extractPermissionNodes(a_node, encoding)
        category       = _es('category')
        visible        = _getNodeAttributeBoolean(a_node, 'visible')
        url_expr       = _es('url_expr')

        result.append( { 'id': action_id,
                         'title': title,
#                         'description': description,
                         'category': category,
                         'condition': condition_expr,
                         'permissions': permissions,
                         'visible': visible,
                         'action': url_expr } )

    return result

def _extractPermissionNodes(parent, encoding=None):

    result = []

    for p_node in parent.getElementsByTagName('permission'):
        value = _coalesceTextNodeChildren(p_node, encoding)
        result.append(value)

    return tuple(result)
