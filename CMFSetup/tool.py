""" Classes:  SetupTool

$Id$
"""
import os
import time

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName

from interfaces import ISetupTool
from permissions import ManagePortal
from context import ImportContext
from context import TarballExportContext
from context import SnapshotExportContext
from registry import ImportStepRegistry
from registry import ExportStepRegistry

from utils import _wwwdir

class SetupTool( UniqueObject, Folder ):

    """ Profile-based site configuration manager.
    """
    __implements__ = ( ISetupTool, ) + Folder.__implements__

    id = 'portal_setup'
    meta_type = 'Portal Setup Tool'

    IMPORT_STEPS_XML = 'import_steps.xml'
    EXPORT_STEPS_XML = 'export_steps.xml'

    _product_name = None
    _profile_directory = None
    _root_directory = None

    security = ClassSecurityInfo()

    def __init__( self ):

        self._import_registry = ImportStepRegistry()
        self._export_registry = ExportStepRegistry()
        self._export_registry.registerStep( 'step_registries'
                                          , exportStepRegistries
                                          , 'Export import / export steps.'
                                          )

    #
    #   ISetupTool API
    #
    security.declareProtected( ManagePortal, 'getProfileProduct' )
    def getProfileProduct( self ):

        """ See ISetupTool.
        """
        return self._product_name

    security.declareProtected( ManagePortal, 'getProfileDirectory' )
    def getProfileDirectory( self, relative_to_product=False ):

        """ See ISetupTool.
        """
        return ( relative_to_product
             and self._profile_directory
              or self._getFullyQualifiedProfileDirectory()
               )

    security.declareProtected( ManagePortal, 'setProfileDirectory' )
    def setProfileDirectory( self, path, product_name=None, encoding=None ):

        """ See ISetupTool.
        """
        if product_name is not None:
            try:
                product = __import__( 'Products.%s' % product_name
                                    , globals(), {}, ['initialize' ] )
            except ImportError:
                raise ValueError, 'Not a valid product name: %s' % product_name

            root = self._root_directory = product.__path__[0]

            if not os.path.exists( os.path.join( root, path ) ):
                raise ValueError, 'Invalid path: %s' % path

        else:
            if not os.path.exists( path ):
                raise ValueError, 'Invalid path: %s' % path

            self._root_directory = None

        self._profile_directory = path
        self._product_name = product_name

        self._updateImportStepsRegistry( encoding )
        self._updateExportStepsRegistry( encoding )
    
    security.declareProtected( ManagePortal, 'getImportStepRegistry' )
    def getImportStepRegistry( self ):

        """ See ISetupTool.
        """
        return self._import_registry
    
    security.declareProtected( ManagePortal, 'getImportStepRegistry' )
    def getExportStepRegistry( self ):

        """ See ISetupTool.
        """
        return self._export_registry

    security.declareProtected( ManagePortal, 'executeStep' )
    def runImportStep( self, step_id, run_dependencies=True, purge_old=True ):

        """ See ISetupTool.
        """
        profile_path = self._getFullyQualifiedProfileDirectory()
        context = ImportContext( self, profile_path, purge_old )

        info = self._import_registry.getStepMetadata( step_id )

        if info is None:
            raise ValueError, 'No such import step: %s' % step_id

        dependencies = info.get( 'dependencies', () )

        messages = {}
        steps = []
        if run_dependencies:
            for dependency in dependencies:

                if dependency not in steps:
                    message = self._doRunImportStep( dependency, context )
                    messages[ dependency ] = message
                    steps.append( dependency )

        message = self._doRunImportStep( step_id, context )
        messages[ step_id ] = message
        steps.append( step_id )

        return { 'steps' : steps, 'messages' : messages }

    security.declareProtected( ManagePortal, 'runAllSetupSteps')
    def runAllImportSteps( self, purge_old=True ):

        """ See ISetupTool.
        """
        profile_path = self._getFullyQualifiedProfileDirectory()
        context = ImportContext( self, profile_path, purge_old )

        steps = self._import_registry.sortSteps()
        messages = {}

        for step in steps:
            message = self._doRunImportStep( step, context )
            messages[ step ] = message

        return { 'steps' : steps, 'messages' : messages }

    security.declareProtected( ManagePortal, 'runExportStep')
    def runExportStep( self, step_id ):

        """ See ISetupTool.
        """
        return self._doRunExportSteps( [ step_id ] )

    security.declareProtected(ManagePortal, 'runAllExportSteps')
    def runAllExportSteps( self ):

        """ See ISetupTool.
        """
        return self._doRunExportSteps( self._export_registry.listSteps() )

    security.declareProtected( ManagePortal, 'createSnapshot')
    def createSnapshot( self, snapshot_id ):

        """ See ISetupTool.
        """
        context = SnapshotExportContext( self, snapshot_id )
        messages = {}
        steps = self._export_registry.listSteps()

        for step_id in steps:

            handler = self._export_registry.getStep( step_id )

            if handler is None:
                raise ValueError( 'Invalid export step: %s' % step_id )

            messages[ step_id ] = handler( context )


        return { 'steps' : steps
               , 'messages' : messages
               , 'url' : context.getSnapshotURL()
               , 'snapshot' : context.getSnapshotFolder()
               }

    security.declareProtected(ManagePortal, 'compareConfigurations')
    def compareConfigurations( self   
                             , source1
                             , source2
                             , missing_as_empty=False
                             , ignore_whitespace=False
                             ):
        """ See ISetupTool.
        """
        raise NotImplementedError

    security.declareProtected( ManagePortal, 'markupComparison')
    def markupComparison(self, lines):

        """ See ISetupTool.
        """
        raise NotImplementedError

    #
    #   ZMI
    #
    manage_options = ( Folder.manage_options[ :1 ]
                     + ( { 'label' : 'Properties'
                         , 'action' : 'manage_tool'
                         }
                       , { 'label' : 'Import'
                         , 'action' : 'manage_importSteps'
                         }
                       , { 'label' : 'Export'
                         , 'action' : 'manage_exportSteps'
                         }
                       , { 'label' : 'Snapshots'
                         , 'action' : 'manage_snapshots'
                         }
                       )
                     + Folder.manage_options[ 3: ] # skip "View", "Properties"
                     )

    security.declareProtected( ManagePortal, 'manage_tool' )
    manage_tool = PageTemplateFile( 'sutProperties', _wwwdir )

    security.declareProtected( ManagePortal, 'manage_updateToolProperties' )
    def manage_updateToolProperties( self
                                   , profile_directory
                                   , profile_product
                                   , RESPONSE
                                   ):
        """ Update the tool's settings.
        """
        profile_directory = profile_directory.strip()
        profile_product = profile_product.strip()

        if profile_directory.startswith( '.' ):
            raise ValueError(
                    "Directories begining with '.' are not allowed." )

        if profile_product and profile_directory.startswith( '/' ):
            raise ValueError(
                    "Product may not be specified with absolute directories" )

        self.setProfileDirectory( profile_directory, profile_product )

        RESPONSE.redirect( '%s/manage_tool?manage_tabs_message=%s'
                         % ( self.absolute_url(), 'Properties+updated.' )
                         )

    security.declareProtected( ManagePortal, 'manage_importSteps' )
    manage_importSteps = PageTemplateFile( 'sutImportSteps', _wwwdir )

    security.declareProtected( ManagePortal, 'manage_importSelectedSteps' )
    def manage_importSelectedSteps( self
                                  , ids
                                  , run_dependencies
                                  , purge_old
                                  , RESPONSE
                                  ):
        """ Import the steps selected by the user.
        """
        if not ids:
            message = 'No+steps+selected.'

        else:
            steps_run = []
            for step_id in ids:
                result = self.runImportStep( step_id
                                           , run_dependencies
                                           , purge_old
                                           )
                steps_run.extend( result[ 'steps' ] )

            message = 'Steps+run:%s' % '+,'.join( steps_run )

        RESPONSE.redirect( '%s/manage_importSteps?manage_tabs_message=%s'
                         % ( self.absolute_url(), message )
                         )

    security.declareProtected( ManagePortal, 'manage_importSelectedSteps' )
    def manage_importAllSteps( self, purge_old, RESPONSE ):

        """ Import all steps.
        """
        result = self.runAllImportSteps( purge_old )
        message = 'Steps+run:%s' % '+,'.join( result[ 'steps' ] )

        RESPONSE.redirect( '%s/manage_importSteps?manage_tabs_message=%s'
                         % ( self.absolute_url(), message )
                         )

    security.declareProtected( ManagePortal, 'manage_exportSteps' )
    manage_exportSteps = PageTemplateFile( 'sutExportSteps', _wwwdir )

    security.declareProtected( ManagePortal, 'manage_exportSelectedSteps' )
    def manage_exportSelectedSteps( self, ids, RESPONSE ):

        """ Export the steps selected by the user.
        """
        if not ids:
            RESPONSE.redirect( '%s/manage_exportSteps?manage_tabs_message=%s'
                             % ( self.absolute_url(), 'No+steps+selected.' )
                             )

        result = self._doRunExportSteps( ids )
        RESPONSE.setHeader( 'Content-type', 'application/x-gzip')
        RESPONSE.setHeader( 'Content-disposition'
                          , 'attachment; filename=%s' % result[ 'filename' ]
                          )
        return result[ 'tarball' ]

    security.declareProtected( ManagePortal, 'manage_exportAllSteps' )
    def manage_exportAllSteps( self, RESPONSE ):

        """ Export all steps.
        """
        result = self.runAllExportSteps()
        RESPONSE.setHeader( 'Content-type', 'application/x-gzip')
        RESPONSE.setHeader( 'Content-disposition'
                          , 'attachment; filename=%s' % result[ 'filename' ]
                          )
        return result[ 'tarball' ]

    security.declareProtected( ManagePortal, 'manage_snapshots' )
    manage_snapshots = PageTemplateFile( 'sutSnapshots', _wwwdir )

    security.declareProtected( ManagePortal, 'listSnapshotInfo' )
    def listSnapshotInfo( self ):

        """ Return a list of mappings describing available snapshots.
        
        o Keys include:

          'id' -- snapshot ID

          'title' -- snapshot title or ID

          'url' -- URL of the snapshot folder

        o ZMI support.
        """
        result = []
        snapshots = self._getOb( 'snapshots', None )

        if snapshots:

            for id, folder in snapshots.objectItems( 'Folder' ):

                result.append( { 'id' : id
                               , 'title' : folder.title_or_id()
                               , 'url' : folder.absolute_url()
                               } )
        return result

    security.declareProtected( ManagePortal, 'manage_createSnapshot' )
    def manage_createSnapshot( self, RESPONSE, snapshot_id=None ):

        """ Create a snapshot with the given ID.

        o If no ID is passed, generate one.
        """
        if snapshot_id is None:
            timestamp = time.gmtime()
            snapshot_id = 'snapshot-%4d%02d%02d%02d%02d%02d' % timestamp[:6]

        self.createSnapshot( snapshot_id )

        RESPONSE.redirect( '%s/manage_snapshots?manage_tabs_message=%s'
                         % ( self.absolute_url(), 'Snapshot+created.' ) )


    #
    #   Helper methods
    #
    security.declarePrivate( '_getFullyQualifiedProfileDirectory' )
    def _getFullyQualifiedProfileDirectory( self ):

        """ Return the fully-qualified directory path of our profile.
        """
        if self._root_directory is not None:
            return os.path.join( self._root_directory
                               , self._profile_directory )

        return self._profile_directory

    security.declarePrivate( '_updateImportStepsRegistry' )
    def _updateImportStepsRegistry( self, encoding ):

        """ Update our import steps registry from our profile.
        """
        fq = self._getFullyQualifiedProfileDirectory()

        f = open( os.path.join( fq, self.IMPORT_STEPS_XML ), 'r' )
        xml = f.read()
        f.close()

        self._import_registry.parseXML( xml, encoding )

    security.declarePrivate( '_updateExportStepsRegistry' )
    def _updateExportStepsRegistry( self, encoding ):

        """ Update our export steps registry from our profile.
        """
        fq = self._getFullyQualifiedProfileDirectory()

        f = open( os.path.join( fq, self.EXPORT_STEPS_XML ), 'r' )
        xml = f.read()
        f.close()

        self._export_registry.parseXML( xml, encoding )

    security.declarePrivate( '_doRunImportStep' )
    def _doRunImportStep( self, step_id, context ):

        """ Run a single import step, using a pre-built context.
        """
        handler = self._import_registry.getStep( step_id )

        if handler is None:
            raise ValueError( 'Invalid import step: %s' % step_id )

        return handler( context )

    security.declarePrivate( '_doRunExportSteps')
    def _doRunExportSteps( self, steps ):

        """ See ISetupTool.
        """
        context = TarballExportContext( self )
        messages = {}

        for step_id in steps:

            handler = self._export_registry.getStep( step_id )

            if handler is None:
                raise ValueError( 'Invalid export step: %s' % step_id )

            messages[ step_id ] = handler( context )


        return { 'steps' : steps
               , 'messages' : messages
               , 'tarball' : context.getArchive()
               , 'filename' : context.getArchiveFilename()
               }

InitializeClass( SetupTool )


def exportStepRegistries( context ):

    """ Built-in handler for exporting import / export step registries.
    """
    site = context.getSite()
    tool = getToolByName( site, 'portal_setup' )

    import_steps_xml = tool.getImportStepRegistry().generateXML()
    context.writeDataFile( 'import_steps.xml', import_steps_xml, 'text/xml' )

    export_steps_xml = tool.getExportStepRegistry().generateXML()
    context.writeDataFile( 'export_steps.xml', export_steps_xml, 'text/xml' )

    return 'Step registries exported'
