""" Classes:  SetupTool

$Id$
"""
import os

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from OFS.Folder import Folder

from Products.CMFCore.utils import UniqueObject

from interfaces import ISetupTool
from permissions import ManagePortal
from context import ImportContext
from context import ExportContext
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

        if run_dependencies:
            already = {}
            for dependency in dependencies:

                if already.get( dependency ) is None:
                    self._doRunImportStep( dependency, context )
                    already[ dependency ] = 1

        return self._doRunImportStep( step_id, context )

    security.declareProtected( ManagePortal, 'runAllSetupSteps')
    def runAllImportSteps( self, purge_old=True ):

        """ See ISetupTool.
        """

    security.declareProtected( ManagePortal, 'runExportStep')
    def runExportStep( self, step_id ):

        """ See ISetupTool.
        """

    security.declareProtected(ManagePortal, 'runAllExportSteps')
    def runAllExportSteps( self ):

        """ See ISetupTool.
        """

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

        return handler( context )

InitializeClass( SetupTool )
