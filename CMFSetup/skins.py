""" Skin path configuration management

Setup step and export script

$Id$
"""
import os
import re
from xml.sax import parseString

from AccessControl import ClassSecurityInfo
from Acquisition import Implicit
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import minimalpath
from Products.CMFCore.DirectoryView import createDirectoryView
from Products.CMFCore.DirectoryView import DirectoryView

from permissions import ManagePortal
from utils import HandlerBase
from utils import _resolveDottedName
from utils import _xmldir

#
#   Entry points
#
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
    encoding = context.getEncoding()

    skins_tool = getToolByName( site, 'portal_skins' )

    if context.shouldPurge():

        skins_tool._getSelections().clear()

        for id in skins_tool.objectIds( DirectoryView.meta_type ):
            skins_tool._delObject(id)

    text = context.readDataFile( _FILENAME )

    if text is not None:

        stc = SkinsToolConfigurator( site ).__of__( site )

        ( default_skin
        , request_var
        , allow_arbitrary
        , persist_cookie
        , skin_dirs
        , skin_paths
        ) = stc.parseXML( text, encoding )

        tool = getToolByName( site, 'portal_skins' )

        tool.default_skin = str( default_skin )
        tool.request_varname = str( request_var )
        tool.allow_any =  allow_arbitrary and 1 or 0
        tool.cookie_persistence =  persist_cookie and 1 or 0

        for id, directory in skin_dirs:

            createDirectoryView( tool, directory, id )

        for path_name, layers in skin_paths:
            tool.addSkinSelection( path_name, ', '.join( layers ) )

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


class SkinsToolConfigurator( Implicit ):

    security = ClassSecurityInfo()   
    security.setDefaultAccess('allow')

    _COMMA_SPLITTER = re.compile( r',[ ]*' )
    
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
        return [ { 'id' : k
                 , 'path' : self._COMMA_SPLITTER.split( v )
                 } for k, v in self._skins_tool.getSkinPaths() ]

    security.declareProtected(ManagePortal, 'listFSDirectoryViews' )
    def listFSDirectoryViews( self ):

        """ Return a sequence of mappings for each FSDV.

        o Keys include:

          'id' -- FSDV ID

          'directory' -- filesystem path of the FSDV.
        """
        result = []
        fsdvs = self._skins_tool.objectItems( DirectoryView.meta_type )
        fsdvs.sort()

        for id, fsdv in fsdvs:

            dirpath = fsdv._dirpath

            if dirpath.startswith( '/' ):
                dirpath = minimalpath( fsdv._dirpath )

            result.append( { 'id' : id
                           , 'directory' : dirpath
                           } )

        return result

    security.declareProtected(ManagePortal, 'getDefaultSkin' )
    def getDefaultSkin( self ):

        """ Return the tool's default skin name.
        """
        return self._skins_tool.default_skin

    security.declareProtected(ManagePortal, 'getRequestVarName' )
    def getRequestVarName( self ):

        """ Return the tool's skin request variable name.
        """
        return self._skins_tool.request_varname

    security.declareProtected(ManagePortal, 'getAllowAny' )
    def getAllowAny( self ):

        """ Return the tool's "allow arbitrary skin paths" setting (a boolean).
        """
        return self._skins_tool.allow_any

    security.declareProtected(ManagePortal, 'getCookiePersistence' )
    def getCookiePersistence( self ):

        """ Return the tool's cookie persistence setting (a boolean).
        """
        return self._skins_tool.cookie_persistence

    security.declareProtected(ManagePortal, 'generateXML' )
    def generateXML(self):

        """ Pseudo API.
        """
        return self._skinsConfig()

    security.declareProtected( ManagePortal, 'parseXML' )
    def parseXML( self, text, encoding=None ):

        """ Pseudo API.
        """
        reader = getattr( text, 'read', None )

        if reader is not None:
            text = reader()

        parser = _SkinsParser( encoding )
        parseString( text, parser )

        return ( parser._default_skin
               , parser._request_var
               , parser._allow_arbitrary
               , parser._persist_cookie
               , parser._skin_dirs
               , parser._skin_paths
               )

    #
    #   Helper methods
    #
    security.declarePrivate( '_skinsConfig' )
    _skinsConfig = PageTemplateFile( 'stcExport.xml'
                                   , _xmldir
                                   , __name__='skinsConfig'
                                   )

InitializeClass( SkinsToolConfigurator )


class _SkinsParser( HandlerBase ):

    security = ClassSecurityInfo()
    security.declareObjectPrivate()
    security.setDefaultAccess( 'deny' )

    def __init__( self, encoding ):

        self._encoding = encoding
        self._skin_dirs = []
        self._skin_paths = []
        self._default_skin = None
        self._request_var = None
        self._allow_arbitrary = False
        self._persist_cookie = False

    def startElement( self, name, attrs ):

        if name == 'skins-tool':
            self._default_skin = self._extract( attrs, 'default_skin' )
            self._request_var = self._extract( attrs, 'request_varname' )
            self._allow_arbitrary = self._extractBoolean( attrs
                                                        , 'allow_any'
                                                        , False
                                                        )
            self._persist_cookie = self._extractBoolean( attrs
                                                       , 'cookie_persistence'
                                                       , False
                                                       )

        elif name == 'skin-directory':

            self._skin_dirs.append( ( self._extract( attrs, 'id' )
                                    , self._extract( attrs, 'directory' )
                                    ) )

        elif name == 'skin-path':

            path_name = self._extract( attrs,'id' )
            self._skin_paths.append( ( path_name, [] ) )

        elif name == 'layer':

            path_name, layers = self._skin_paths[ -1 ]
            layers.append( self._extract( attrs, 'name' ) )

        else:
            raise ValueError, 'Unknown element %s' % name

InitializeClass( _SkinsParser )
