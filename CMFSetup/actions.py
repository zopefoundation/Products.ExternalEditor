""" Classes:  ActionsProviderConfigurator

$Id$
"""
from xml.sax import parseString
from xml.sax.handler import ContentHandler

from AccessControl import ClassSecurityInfo
from Acquisition import Implicit
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.utils import getToolByName

from permissions import ManagePortal
from utils import _xmldir

# Dummy object for passing to listActions
class _FauxContent:
    def __init__( self, **kw ):
        self.__dict__.update( kw )

class _ActionProviderParser( ContentHandler ):

    def __init__( self, site, encoding='latin-1' ):

        self._site = site
        self._encoding = encoding
        self._provider_info = {}
        self._provider_ids = []

    def _extract( self, attrs, key ):

        return attrs[ key ].encode( self._encoding )

    def startElement( self, name, attrs ):

        if name == 'actions-tool':
            pass

        elif name == 'action-provider':

            id = self._extract( attrs, 'id' )

            if id not in self._provider_ids:
                self._provider_ids.append( id )

        elif name == 'action':

            provider_id = self._provider_ids[ -1 ]
            actions = self._provider_info.setdefault( provider_id, [] )

            info = { 'action_id' : self._extract( attrs, 'action_id' )
                   , 'category' : self._extract( attrs, 'category' )
                   , 'name' : self._extract( attrs, 'title' )
                   , 'action' : self._extract( attrs, 'action_expr' )
                   , 'condition' : self._extract( attrs, 'condition_expr' )
                   , 'permission' : self._extract( attrs, 'permission' )
                   , 'category' : self._extract( attrs, 'category' )
                   , 'visible' : self._extract( attrs, 'visible' )
                   }

            actions.append( info )

        else:
            raise ValueError, 'Unknown element %s' % name

    def endElement( self, name ):

        if name in ( 'actions-tool', 'action' ):
            pass

    def endDocument( self ):

        actions_tool = getToolByName( self._site, 'portal_actions' )

        for provider_id in self._provider_ids:

            if provider_id not in actions_tool.listActionProviders():

                actions_tool.addActionProvider( provider_id )

            provider = getToolByName( self._site, provider_id )
            provider._actions = ()

            for info in self._provider_info.get( provider_id, () ):

                provider.addAction( id=info[ 'action_id' ]
                                  , name=info[ 'name' ]
                                  , action=info[ 'action' ]
                                  , condition=info[ 'condition' ]
                                  , permission=info[ 'permission' ]
                                  , category=info[ 'category' ]
                                  , visible=info[ 'visible' ]
                                  )

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
        faux = _FauxContent( content=None, isAnonymous=1 )
        result = []

        for provider_id in actions_tool.listActionProviders():

            provider_info = { 'id' : provider_id, 'actions' : [] }
            result.append( provider_info )
            append = provider_info[ 'actions' ].append

            provider = getToolByName( self._site, provider_id )

            actions = provider.listActions( info=faux ) or []
            
            for action in actions:

                ainfo = {}
                ainfo[ 'id'] = action.getId()
                ainfo[ 'name'] = action.Title()

                p = action.getPermissions()

                if p:
                    ainfo[ 'permission'] = p[ 0 ]
                else:
                    ainfo[ 'permission'] = ''

                ainfo[ 'category'] = action.getCategory() or 'object'
                ainfo[ 'visible'] = action.getVisibility()
                ainfo[ 'action'] = action.getActionExpression()
                ainfo[ 'condition'] = action.getCondition()

                append( ainfo )

        return result

    security.declareProtected( ManagePortal, 'generateXML' )
    def generateXML( self ):

        """ Pseudo API.
        """
        return self._providers()

    security.declareProtected( ManagePortal, 'parseXML' )
    def parseXML( self, text ):

        """ Pseudo API.
        """
        reader = getattr( text, 'read', None )

        if reader is not None:
            text = reader()

        parseString( text, _ActionProviderParser( self._site ) )

InitializeClass( ActionProvidersConfigurator )


#
#   Configurator entry points
#
_FILENAME = 'actions.xml'

def importActionProviders( context ):

    """ Export roles / permission map as an XML file

    o 'context' must implement IImportContext.

    o Register via Python:

      registry = site.portal_setup.setup_steps
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

    if context.shouldPurge():

        actions_tool = getToolByName( site, 'portal_actions' )
        for provider_id in actions_tool.listActionProviders():
            actions_tool.deleteActionProvider( provider_id )

    text = context.readDataFile( _FILENAME )

    if text is not None:

        apc = ActionProvidersConfigurator( site ).__of__( site )
        apc.parseXML( text )

    return 'Action providers imported.'


def exportActionProviders( context ):

    """ Export action providers and their actions as an XML file

    o 'context' must implement IExportContext.

    o Register via Python:

      registry = site.portal_setup.export_steps
      registry.registerStep( 'exportActionProviders'
                           , Products.CMFSetup.rolemap.exportActionProviders
                           , 'Action Provider export'
                           , 'Export action providers registered with '
                             'the actions tool, and their actions.'
                           )

    o Register via XML:
 
      <export-script id="exportActionProviders"
                     version="20040518-01"
                     handler="Products.CMFSetup.rolemap.exportActionProviders"
                     title="Action Provider export"
      >Export action providers registered with the actions tool,
       and their actions.</export-script>

    """
    site = context.getSite()
    apc = ActionProvidersConfigurator( site ).__of__( site )
    text = apc.generateXML()

    context.writeDataFile( _FILENAME, text, 'text/xml' )

    return 'Action providers exported.'
