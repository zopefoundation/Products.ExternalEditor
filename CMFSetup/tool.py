""" Classes:  SetupTool

$Id$
"""

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from OFS.Folder import Folder

from Products.CMFCore.utils import UniqueObject

from interfaces import ISetupTool
from permissions import ManagePortal


class SetupTool( UniqueObject, Folder ):

    """ Profile-based site configuration manager.
    """
    __implements__ = ( ISetupTool, ) + Folder.__implements__

    id = 'portal_setup'
    meta_type = 'Portal Setup Tool'

    security = ClassSecurityInfo()
    
    security.declareProtected( ManagePortal, 'executeStep' )
    def runSetupStep( self, step_id, run_dependencies=True, purge_old=True ):

        """ See ISetupTool.
        """

    security.declareProtected( ManagePortal, 'runAllSetupSteps')
    def runAllSetupSteps( self, purge_old=True ):

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

InitializeClass( SetupTool )
