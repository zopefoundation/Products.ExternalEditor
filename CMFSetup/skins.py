"""Skin path configuration management

Setup step and export script

$Id$
"""

from xml.sax import parse

from AccessControl import ClassSecurityInfo
from Acquisition import Implicit
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.DirectoryView import createDirectoryView

from permissions import ManagePortal
from utils import HandlerBase
from utils import _xmldir

class _SkinsParser( HandlerBase ):

    def __init__( self, site, encoding='latin-1' ):

        self._site = site
        self._skins_tool = getToolByName( site, 'portal_skins' )
        self._encoding = encoding
        self._skin_dirs = []
        self._skin_paths = []

    def startElement( self, name, attrs ):

        if name == 'skins-tool':
            pass

        elif name == 'skin-directory':

            self._skin_dirs.append( ( self._extract( attrs, 'id' )
                                    , self._extract( attrs, 'path' )
                                    ) )

        elif name == 'skin-path':

            path_name = self._extract( attrs,'id' )
            self._skin_paths.append( ( path_name, [] ) )

        elif name == 'layer':

            path_name, layers = self._skin_paths[ -1 ]
            layers.append( self._extract( attrs, 'name' ) )

        else:
            raise ValueError, 'Unknown element %s' % name

    def endDocument( self ):

        tool = self._skins_tool

        for id, path in self._skin_dirs:
            createDirectoryView( tool, path, id )

        for path_name, layers in self._skin_paths:
            tool.addSkinSelection( path_name, ', '.join( layers ) )

class SkinsToolConfigurator( Implicit ):

    security = ClassSecurityInfo()   
    security.setDefaultAccess('allow')
    
    def __init__( self, site ):

        self._site = site
        self._skins_tool = getToolByName( site, 'portal_skins' )

    security.declareProtected(ManagePortal, 'listSkinPaths' )
    def listSkinPaths( self ):

        """ Return a sequence of mappings for each skin path in the tool.

        o Keys include:

          'id' -- folder ID

          'path' -- sequence of layer IDs
        """
        return [ { 'id' : k, 'path' : v }
                  for k, v in self._skins_tool.getSkinPaths() ]

    security.declareProtected(ManagePortal, 'getDirPath' )
    def getDirPath( self, dir ):

        """Return the private _dirpath variable
        """
        return dir._dirpath

    _skinsConfig = PageTemplateFile( 'stcExport.xml'
                                   , _xmldir
                                   , __name__='skinsConfig'
                                   )

    security.declareProtected(ManagePortal, 'generateXML' )
    def generateXML(self):

        """ Pseudo API.
        """
        return self._skinsConfig()

    security.declareProtected( ManagePortal, 'parseXML' )
    def parseXML( self, text ):

        """ Pseudo API.
        """
        reader = getattr( text, 'read', None )

        if reader is not None:
            text = reader()

        parseString( text, _SkinsParser( self._site ) )

InitializeClass( SkinsToolConfigurator )


_FILENAME = 'skins.xml'

def importSkinsTool( context ):

    """ Import skins tool FSDirViews and skin paths from an XML file

    o 'context' must implement IImportContext.

    o Register via Python:

      registry = site.portal_setup.getImportStepRegistry()
      registry.registerStep( 'importSkinsTool'
                           , '20040518-01'
                           , Products.CMFSetup.skins.importSkinsTool
                           , ()
                           , 'Skins Tool import'
                           , 'Import skins tool FSDVs and skin paths.'
                           )

    o Register via XML:
 
      <setup-step id="importSkinsTool"
                  version="20040524-01"
                  handler="Products.CMFSetup.skins.importSkinsTool"
                  title="Skins Tool import"
      >Import skins tool FSDVs and skin paths.</setup-step>

    """
    site = context.getSite()
    skins_tool = getToolByName( site, 'portal_skins' )

    if context.shouldPurge():

        skins_tool._getSelections().clear()

        for id in skins_tool.objectIds('Filesystem Directory View'):
            skins_tool._delObject(id)

    text = context.readDataFile( _FILENAME )

    if text is not None:

        stc = SkinsToolConfigurator( site ).__of__( site )
        stc.parseXML( text )

    #
    #   Purge and rebuild the skin path, now that we have added our stuff.
    #
    site._v_skindata = None
    skins_tool.setupCurrentSkin( site.REQUEST )

    return 'Skins tool imported'


def exportSkinsTool( context ):

    """ Export skins tool FSDVs and skin paths as an XML file

    o 'context' must implement IExportContext.

    o Register via Python:

      registry = site.portal_setup.getExportStepRegistry()
      registry.registerStep( 'exportSkinsTool'
                           , Products.CMFSetup.skins.exportSkinsTool
                           , 'Skins Tool export'
                           , 'Export skins tool FSDVs and skin paths.'
                           )

    o Register via XML:
 
      <export-script id="exportSkinsTool"
                     version="20040518-01"
                     handler="Products.CMFSetup.skins.exportSkinsTool"
                     title="Skins Tool export"
      >Export skins tool FSDVs and skin paths.</export-script>

    """
    site = context.getSite()
    stc = SkinsToolConfigurator( site ).__of__( site )
    text = stc.generateXML()

    context.writeDataFile( _FILENAME, text, 'text/xml' )

    return 'Skins tool exported.'
