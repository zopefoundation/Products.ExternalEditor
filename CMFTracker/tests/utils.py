import Zope
import unittest

from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.CatalogTool import CatalogTool
from Products.CMFCore.TypesTool import TypesTool
from Products.CMFCore.WorkflowTool import WorkflowTool
from Products.CMFDefault.DefaultWorkflow import DefaultWorkflowDefinition
from Products.CMFDefault.MetadataTool import MetadataTool
from Products.CMFDefault.Portal import manage_addCMFSite

class BaseTrackerTestCase( unittest.TestCase ):
    """
        Common base class for CMFTracker test cases.
    """
    def setUp( self ):

        get_transaction().begin()

        # Set up a scratch CMFSite
        app = Zope.app()
        manage_addCMFSite( app, 'testing' )
        self.root = app.testing

        # TODO:  Configure type info for Issue, Tracker

        # TODO:  Create TrackerWorkflow and bind to Issue.

        # TODO:  Create Tracker/Issue-specific element specs.

    def tearDown( self ):

        del self.root
        get_transaction().abort()
