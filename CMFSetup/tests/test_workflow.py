""" Unit tests for export / import of DCWorkflows and bindings.

$Id$
"""
import unittest

from OFS.Folder import Folder

from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition

from common import BaseRegistryTests

class DummyWorkflowTool( Folder ):

    def getWorkflowIds( self ):

        return self.objectIds()

    def getWorkflowById( self, workflow_id ):

        return self._getOb( workflow_id )

class DummyWorkflow( Folder ):

    meta_type = 'Dummy Workflow'

class _GuardChecker:

    def _genGuardProps( self, permissions, roles, groups, expr ):

        return { 'guard_permissions'   : '; '.join( permissions )
               , 'guard_roles'         : '; '.join( roles )
               , 'guard_groups'        : '; '.join( groups )
               , 'guard_expr'          : expr
               }

    def _assertGuard( self, info, permissions, roles, groups, expr ):

        self.assertEqual( info[ 'guard_permissions' ]
                        , '; '.join( permissions ) )

        self.assertEqual( info[ 'guard_roles' ]
                        , '; '.join( roles ) )

        self.assertEqual( info[ 'guard_groups' ]
                        , '; '.join( groups ) )

        self.assertEqual( info[ 'guard_expr' ], expr )

class _WorkflowSetup( BaseRegistryTests ):

    def _initSite( self ):

        self.root.site = Folder( id='site' )
        site = self.root.site
        self.root.site.portal_workflow = DummyWorkflowTool()

        return site

class WorkflowToolConfiguratorTests( _WorkflowSetup
                                   , _GuardChecker
                                   ):

    def _getTargetClass( self ):

        from Products.CMFSetup.workflow import WorkflowToolConfigurator
        return WorkflowToolConfigurator

    def test_getWorkflowInfo_non_dcworkflow( self ):

        WF_ID = 'dummy'
        WF_TITLE = 'Dummy'

        site = self._initSite()
        configurator = self._makeOne( site ).__of__( site )
        wf_tool = site.portal_workflow

        dummy = DummyWorkflow( WF_TITLE )
        wf_tool._setObject( WF_ID, dummy )

        info = configurator.getWorkflowInfo( WF_ID )
        self.assertEqual( info[ 'id' ], WF_ID )
        self.assertEqual( info[ 'meta_type' ], DummyWorkflow.meta_type )
        self.assertEqual( info[ 'title' ], WF_TITLE )

    def test_getWorkflowInfo_dcworkflow_defaults( self ):

        WF_ID = 'dcworkflow'

        site = self._initSite()
        configurator = self._makeOne( site ).__of__( site )
        wf_tool = site.portal_workflow

        dcworkflow = DCWorkflowDefinition( WF_ID )
        wf_tool._setObject( WF_ID, dcworkflow )

        info = configurator.getWorkflowInfo( WF_ID )
        self.assertEqual( info[ 'id' ], WF_ID )
        self.assertEqual( info[ 'meta_type' ], DCWorkflowDefinition.meta_type )
        self.assertEqual( info[ 'title' ], dcworkflow.title )

        self.assertEqual( info[ 'state_variable' ], dcworkflow.state_var )

        permission_info = info[ 'permissions' ]
        self.assertEqual( len( permission_info ), 0 )

    def test_getWorkflowInfo_dcworkflow_permissions( self ):

        WF_ID = 'dcworkflow'
        WF_PERMISSIONS = ( 'Frob content', 'Bruggle content' )

        site = self._initSite()
        configurator = self._makeOne( site ).__of__( site )
        wf_tool = site.portal_workflow

        dcworkflow = DCWorkflowDefinition( WF_ID )
        dcworkflow.permissions = WF_PERMISSIONS
        wf_tool._setObject( WF_ID, dcworkflow )

        info = configurator.getWorkflowInfo( WF_ID )
        permissions = info[ 'permissions' ]
        self.assertEqual( len( permissions ), len( WF_PERMISSIONS ) )
        for permission in WF_PERMISSIONS:
            self.failUnless( permission in permissions )

    def test_getWorkflowInfo_dcworkflow_variables( self ):

        WF_ID = 'dcworkflow'

        site = self._initSite()
        configurator = self._makeOne( site ).__of__( site )
        wf_tool = site.portal_workflow

        dcworkflow = DCWorkflowDefinition( WF_ID )

        for id, args in _WF_VARIABLES.items():

            dcworkflow.variables.addVariable( id )
            variable = dcworkflow.variables._getOb( id )

            ( descr, def_val, def_exp, for_cat, for_stat, upd_alw
            ) = args[ :-4 ]

            variable.setProperties( descr, def_val, def_exp
                                  , for_cat, for_stat, upd_alw
                                  , self._genGuardProps( *args[ -4: ] )
                                  )

        wf_tool._setObject( WF_ID, dcworkflow )

        info = configurator.getWorkflowInfo( WF_ID )
        variable_info = info[ 'variable_info' ]
        self.assertEqual( len( variable_info ), len( _WF_VARIABLES ) )

        ids = [ x[ 'id' ] for x in variable_info ]
        for k in _WF_VARIABLES.keys():
            self.failUnless( k in ids )

        for info in variable_info:

            expected = _WF_VARIABLES[ info[ 'id' ] ]

            self.assertEqual( info[ 'description' ], expected[ 0 ] )
            self.assertEqual( info[ 'default_value' ], expected[ 1 ] )
            self.assertEqual( info[ 'default_expr' ], expected[ 2 ] )
            self.assertEqual( info[ 'for_catalog' ], expected[ 3 ] )
            self.assertEqual( info[ 'for_status' ], expected[ 4 ] )
            self.assertEqual( info[ 'update_always' ], expected[ 5 ] )

            self._assertGuard( info, *expected[ -4: ] )

    def test_getWorkflowInfo_dcworkflow_states( self ):

        WF_ID = 'dcworkflow'
        WF_INITIAL_STATE = 'closed'

        site = self._initSite()
        configurator = self._makeOne( site ).__of__( site )
        wf_tool = site.portal_workflow

        dcworkflow = DCWorkflowDefinition( WF_ID )
        dcworkflow.initial_state = WF_INITIAL_STATE
        
        for k, v in _WF_STATES.items():

            dcworkflow.states.addState( k )
            state = dcworkflow.states._getOb( k )

            state.setProperties( title=v[ 0 ]
                               , description=v[ 1 ]
                               , transitions=v[ 2 ]
                               )
            if not v[ 3 ]:
                state.permission_roles = {}

            for permission, roles in v[ 3 ].items():
                state.setPermission( permission
                                   , not isinstance( roles, tuple )
                                   , roles
                                   )
            faux_request = {}

            for group_id, roles in v[ 4 ]:
                for role in roles:
                    faux_request[ '%s|%s' % ( group_id, role ) ] = True

            state.setGroups( REQUEST=faux_request )

            for k, v in v[ 5 ].items():
                state.addVariable( k, v )

        wf_tool._setObject( WF_ID, dcworkflow )

        info = configurator.getWorkflowInfo( WF_ID )
        self.assertEqual( info[ 'state_variable' ], dcworkflow.state_var )
        self.assertEqual( info[ 'initial_state' ], dcworkflow.initial_state )

        state_info = info[ 'state_info' ]
        self.assertEqual( len( state_info ), len( _WF_STATES ) )

        ids = [ x[ 'id' ] for x in state_info ]
        for k in _WF_STATES.keys():
            self.failUnless( k in ids )

        for info in state_info:

            expected = _WF_STATES[ info[ 'id' ] ]

            self.assertEqual( info[ 'title' ], expected[ 0 ] )
            self.assertEqual( info[ 'description' ], expected[ 1 ] )
            self.assertEqual( info[ 'transitions' ], expected[ 2 ] )

            permissions = info[ 'permissions' ]

            self.assertEqual( len( permissions ), len( expected[ 3 ] ) )

    def test_listWorkflowInfo_empty( self ):

        site = self._initSite()
        configurator = self._makeOne( site ).__of__( site )

        self.assertEqual( len( configurator.listWorkflowInfo() ), 0 )



_WF_VARIABLES = \
{ 'foo' : ( 'Foo stuff'
          , ''
          , "python:'foo'"
          , True
          , False
          , True
          , ( 'Manage foo', 'Add qux' )
          , ()
          , ()
          , ""
          )
, 'bar' : ( 'Bar stuff'
          , 'bar'
          , ""
          , True
          , False
          , True
          , ()
          , ( 'Barkeeper', 'Prisoner' )
          , ()
          , ""
          )
}

_WF_STATES = \
{ 'closed' : ( 'Closed'
             , 'Closed for modifications'
             , ( 'open', 'kill' )
             , { 'Modify content' : () }
             , ()
             , { 'is_opened' : False, 'is_closed' : True }
             )
, 'open'   : ( 'Open'
             , 'Open for modifications'
             , ( 'close', 'kill' )
             , { 'Modify content' : [ 'Owner', 'Manager' ] }
             , [ ( 'Content_owners', ( 'Owner', ) ) ]
             , { 'is_opened' : True, 'is_closed' : True }
             )
, 'killed' : ( 'Killed'
             , 'Permanently unavailable'
             , ()
             , {}
             , ()
             , {}
             )
}


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite( WorkflowToolConfiguratorTests ),
        #unittest.makeSuite( Test_exportWorkflow ),
        #unittest.makeSuite( Test_importWorkflow ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
