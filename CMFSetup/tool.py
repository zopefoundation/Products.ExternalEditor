""" Classes:  SetupTool

$Id$
"""
import os

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from OFS.Folder import Folder

from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName

from interfaces import ISetupTool
from permissions import ManagePortal
from context import ImportContext
from context import TarballExportContext
from registry import ImportStepRegistry
from registry import ExportStepRegistry


class SetupTool( UniqueObject, Folder ):

    """ Profile-based site configuration manager.
    """
    __implements__ = ( ISetupTool, ) + Folder.__implements__

    id = 'portal_setup'
    meta_type = 'Portal Setup Tool'

    IMPORT_STEPS_XML = 'import-steps.xml'
    EXPORT_STEPS_XML = 'export-steps.xml'

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

    security.declareProtected( ManagePortal, 'getProfileProduct' )
    def getProfileProduct( self ):

        """ See ISetupTool.
        """
        return self._product_name

    security.declareProtected( ManagePortal, 'getProfileDirectory' )
    def getProfileDirectory( self, relative_to_product=False ):

        """ See ISetupTool.
        """
        if relative_to_product:
            if not self._product_name:
                raise ValueError(
                        'Profile directory is not relative to any product.' )
        else:
            if self._product_name:
                return self._getFullyQualifiedProfileDirectory()

        return self._profile_directory

    security.declareProtected( ManagePortal, 'setProfileDirectory' )
    def setProfileDirectory( self, path, product_name=None ):

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

        self._updateImportStepsRegistry()
        self._updateExportStepsRegistry()
    
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
        context = TarballExportContext( self )
        handler = self._export_registry.getStep( step_id )

        if handler is None:
            raise ValueError( 'Invalid export step: %s' % step_id )

        message = handler( context )

        return { 'steps' : [ step_id ]
               , 'messages' : { step_id : message }
               , 'tarball' : context.getArchive()
               }

    security.declareProtected(ManagePortal, 'runAllExportSteps')
    def runAllExportSteps( self ):

        """ See ISetupTool.
        """
        context = TarballExportContext( self )

        steps = self._export_registry.listSteps()
        messages = {}
        for step_id in steps:

            handler = self._export_registry.getStep( step_id )
            messages[ step_id ] = handler( context )


        return { 'steps' : steps
               , 'messages' : messages
               , 'tarball' : context.getArchive()
               }

    security.declareProtected( ManagePortal, 'createSnapshot')
    def createSnapshot( self, snapshot_id ):

        """ See ISetupTool.
        """

    security.declareProtected(ManagePortal, 'compareConfigurations')
    def compareConfigurations( self   
                             , source1
                             , source2
                             , missing_as_empty=False
                             , ignore_whitespace=False
                             ):
        """ See ISetupTool.
        """

    security.declareProtected( ManagePortal, 'markupComparison')
    def markupComparison(self, lines):

        """ See ISetupTool.
        """

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
    def _updateImportStepsRegistry( self ):

        """ Update our import steps registry from our profile.
        """
        fq = self._getFullyQualifiedProfileDirectory()

        f = open( os.path.join( fq, self.IMPORT_STEPS_XML ), 'r' )
        xml = f.read()
        f.close()

        self._import_registry.importFromXML( xml )

    security.declarePrivate( '_updateExportStepsRegistry' )
    def _updateExportStepsRegistry( self ):

        """ Update our export steps registry from our profile.
        """
        fq = self._getFullyQualifiedProfileDirectory()

        f = open( os.path.join( fq, self.EXPORT_STEPS_XML ), 'r' )
        xml = f.read()
        f.close()

        self._export_registry.importFromXML( xml )

    security.declarePrivate( '_doRunImportStep' )
    def _doRunImportStep( self, step_id, context ):

        """ Run a single import step, using a pre-built context.
        """
        handler = self._import_registry.getStep( step_id )

        if handler is None:
            raise ValueError( 'Invalid import step: %s' % step_id )

        return handler( context )

InitializeClass( SetupTool )


def exportStepRegistries( context ):

    """ Built-in handler for exporting import / export step registries.
    """
    site = context.getSite()
    tool = getToolByName( site, 'portal_setup' )

    import_steps_xml = tool.getImportStepRegistry().exportAsXML()
    context.writeDataFile( 'import_steps.xml', import_steps_xml, 'text/xml' )

    export_steps_xml = tool.getExportStepRegistry().exportAsXML()
    context.writeDataFile( 'export_steps.xml', export_steps_xml, 'text/xml' )

    return 'Step registries exported'
