""" Unit tests for export / import of DCWorkflows and bindings.

$Id$
"""
import unittest

from OFS.Folder import Folder

from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.DCWorkflow.Transitions import TRIGGER_USER_ACTION
from Products.DCWorkflow.Transitions import TRIGGER_AUTOMATIC

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

    def _initDCWorkflow( self, workflow_id ):

        wf_tool = self.root.site.portal_workflow
        wf_tool._setObject( workflow_id, DCWorkflowDefinition( workflow_id ) )

        return wf_tool._getOb( workflow_id )

    def _initVariables( self, dcworkflow ):

        for id, args in _WF_VARIABLES.items():

            dcworkflow.variables.addVariable( id )
            variable = dcworkflow.variables._getOb( id )

            ( descr, def_val, def_exp, for_cat, for_stat, upd_alw
            ) = args[ :-4 ]

            variable.setProperties( description=args[0]
                                  , default_value=args[1]
                                  , default_expr=args[2]
                                  , for_catalog=args[3]
                                  , for_status=args[4]
                                  , update_always=args[5]
                                  , props=self._genGuardProps( *args[ -4: ] )
                                  )

    def _initStates( self, dcworkflow ):
        
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

    def _initTransitions( self, dcworkflow ):
        
        for k, v in _WF_TRANSITIONS.items():

            dcworkflow.transitions.addTransition( k )
            transition = dcworkflow.transitions._getOb( k )

            transition.setProperties( title=v[ 0 ]
                                    , description=v[ 1 ]
                                    , new_state_id=v[ 2 ]
                                    , trigger_type=v[ 3 ]
                                    , script_name=v[ 4 ]
                                    , after_script_name=v[ 5 ]
                                    , actbox_name=v[ 6 ]
                                    , actbox_url=v[ 7 ]
                                    , actbox_category=v[ 8 ]
                                    , props=self._genGuardProps( *v[ -4: ] )
                                    )

            for k, v in v[ 9 ].items():
                transition.addVariable( k, v )

    def _initWorklists( self, dcworkflow ):

        for k, v in _WF_WORKLISTS.items():

            dcworkflow.worklists.addWorklist( k )
            worklist = dcworkflow.worklists._getOb( k )

            worklist.title = v[ 0 ]

            props=self._genGuardProps( *v[ -4: ] )

            for var_id, matches in v[ 2 ].items():
                props[ 'var_match_%s' % var_id ] = ';'.join( matches )

            worklist.setProperties( description=v[ 1 ]
                                  , actbox_name=v[ 3 ]
                                  , actbox_url=v[ 4 ]
                                  , actbox_category=v[ 5 ]
                                  , props=props
                                  )

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
        wf_tool = site.portal_workflow
        dummy = DummyWorkflow( WF_TITLE )
        wf_tool._setObject( WF_ID, dummy )

        dummy.title = WF_TITLE

        configurator = self._makeOne( site ).__of__( site )
        info = configurator.getWorkflowInfo( WF_ID )

        self.assertEqual( info[ 'id' ], WF_ID )
        self.assertEqual( info[ 'meta_type' ], DummyWorkflow.meta_type )
        self.assertEqual( info[ 'title' ], WF_TITLE )

    def test_getWorkflowInfo_dcworkflow_defaults( self ):

        WF_ID = 'dcworkflow_defaults'

        site = self._initSite()
        dcworkflow = self._initDCWorkflow( WF_ID )

        configurator = self._makeOne( site ).__of__( site )
        info = configurator.getWorkflowInfo( WF_ID )

        self.assertEqual( info[ 'id' ], WF_ID )
        self.assertEqual( info[ 'meta_type' ], DCWorkflowDefinition.meta_type )
        self.assertEqual( info[ 'title' ], dcworkflow.title )

        self.assertEqual( info[ 'state_variable' ], dcworkflow.state_var )

        self.assertEqual( len( info[ 'permissions' ] ), 0 )
        self.assertEqual( len( info[ 'variable_info' ] ), 0 )
        self.assertEqual( len( info[ 'state_info' ] ), 0 )
        self.assertEqual( len( info[ 'transition_info' ] ), 0 )

    def test_getWorkflowInfo_dcworkflow_permissions( self ):

        WF_ID = 'dcworkflow_permissions'

        site = self._initSite()
        dcworkflow = self._initDCWorkflow( WF_ID )
        dcworkflow.permissions = _WF_PERMISSIONS

        configurator = self._makeOne( site ).__of__( site )
        info = configurator.getWorkflowInfo( WF_ID )

        permissions = info[ 'permissions' ]
        self.assertEqual( len( permissions ), len( _WF_PERMISSIONS ) )

        for permission in _WF_PERMISSIONS:
            self.failUnless( permission in permissions )

    def test_getWorkflowInfo_dcworkflow_variables( self ):

        WF_ID = 'dcworkflow_variables'

        site = self._initSite()
        dcworkflow = self._initDCWorkflow( WF_ID )
        self._initVariables( dcworkflow )

        configurator = self._makeOne( site ).__of__( site )
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

        WF_ID = 'dcworkflow_states'
        WF_INITIAL_STATE = 'closed'

        site = self._initSite()
        dcworkflow = self._initDCWorkflow( WF_ID )
        dcworkflow.initial_state = WF_INITIAL_STATE
        self._initStates( dcworkflow )

        configurator = self._makeOne( site ).__of__( site )
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

            for ep_id, ep_roles in expected[ 3 ].items():

                fp = [ x for x in permissions if x[ 'name' ] == ep_id ][ 0 ]

                self.assertEqual( fp[ 'acquired' ]
                                , not isinstance( ep_roles, tuple ) )

                self.assertEqual( len( fp[ 'roles' ] ), len( ep_roles ) )

                for ep_role in ep_roles:
                    self.failUnless( ep_role in fp[ 'roles' ] )

    def test_getWorkflowInfo_dcworkflow_transitions( self ):

        from Products.CMFSetup.workflow import TRIGGER_TYPES

        WF_ID = 'dcworkflow_transitions'

        site = self._initSite()
        dcworkflow = self._initDCWorkflow( WF_ID )
        self._initTransitions( dcworkflow )

        configurator = self._makeOne( site ).__of__( site )
        info = configurator.getWorkflowInfo( WF_ID )

        transition_info = info[ 'transition_info' ]
        self.assertEqual( len( transition_info ), len( _WF_TRANSITIONS ) )

        ids = [ x[ 'id' ] for x in transition_info ]

        for k in _WF_TRANSITIONS.keys():
            self.failUnless( k in ids )

        for info in transition_info:

            expected = _WF_TRANSITIONS[ info[ 'id' ] ]

            self.assertEqual( info[ 'title' ], expected[ 0 ] )
            self.assertEqual( info[ 'description' ], expected[ 1 ] )
            self.assertEqual( info[ 'new_state_id' ], expected[ 2 ] )
            self.assertEqual( info[ 'trigger_type' ]
                            , TRIGGER_TYPES[ expected[ 3 ] ] )
            self.assertEqual( info[ 'script_name' ], expected[ 4 ] )
            self.assertEqual( info[ 'after_script_name' ], expected[ 5 ] )
            self.assertEqual( info[ 'actbox_name' ], expected[ 6 ] )
            self.assertEqual( info[ 'actbox_url' ], expected[ 7 ] )
            self.assertEqual( info[ 'actbox_category' ], expected[ 8 ] )

            variables = info[ 'variables' ]
            self.assertEqual( len( variables ), len( expected[ 9 ] ) )

            for var_id, expr in variables:
                self.assertEqual( expr, expected[ 9 ][ var_id ] )

            self._assertGuard( info, *expected[ -4: ] )

    def test_getWorkflowInfo_dcworkflow_worklists( self ):

        WF_ID = 'dcworkflow_worklists'

        site = self._initSite()
        dcworkflow = self._initDCWorkflow( WF_ID )
        self._initWorklists( dcworkflow )

        configurator = self._makeOne( site ).__of__( site )
        info = configurator.getWorkflowInfo( WF_ID )

        worklist_info = info[ 'worklist_info' ]
        self.assertEqual( len( worklist_info ), len( _WF_WORKLISTS ) )

        ids = [ x[ 'id' ] for x in worklist_info ]

        for k in _WF_WORKLISTS.keys():
            self.failUnless( k in ids )

        for info in worklist_info:

            expected = _WF_WORKLISTS[ info[ 'id' ] ]

            self.assertEqual( info[ 'title' ], expected[ 0 ] )
            self.assertEqual( info[ 'description' ], expected[ 1 ] )
            self.assertEqual( info[ 'actbox_name' ], expected[ 3 ] )
            self.assertEqual( info[ 'actbox_url' ], expected[ 4 ] )
            self.assertEqual( info[ 'actbox_category' ], expected[ 5 ] )

            var_match = info[ 'var_match' ]
            self.assertEqual( len( var_match ), len( expected[ 2 ] ) )

            for var_id, values_txt in var_match:

                values = [ x.strip() for x in values_txt.split( ';' ) ]
                e_values = expected[ 2 ][ var_id ]
                self.assertEqual( len( values ), len( e_values ) )

                for e_value in e_values:
                    self.failUnless( e_value in values )

            self._assertGuard( info, *expected[ -4: ] )

    def test_listWorkflowInfo_empty( self ):

        site = self._initSite()

        configurator = self._makeOne( site ).__of__( site )

        self.assertEqual( len( configurator.listWorkflowInfo() ), 0 )


_WF_PERMISSIONS = \
( 'Open content for modifications'
, 'Modify content'
, 'Query history'
, 'Restore expired content'
)

_WF_VARIABLES = \
{ 'when_opened':  ( 'Opened when'
                  , ''
                  , "python:None"
                  , True
                  , False
                  , True
                  , ( 'Query history', 'Open content for modifications' )
                  , ()
                  , ()
                  , ""
                  )
, 'when_expired': ( 'Expired when'
                  , ''
                  , "nothing"
                  , True
                  , False
                  , True
                  , ( 'Query history', 'Open content for modifications' )
                  , ()
                  , ()
                  , ""
                  )
, 'killed_by':    ( 'Killed by'
                  , 'n/a'
                  , ""
                  , True
                  , False
                  , True
                  , ()
                  , ( 'Hangman', 'Sherrif' )
                  , ()
                  , ""
                  )
}

_WF_STATES = \
{ 'closed':  ( 'Closed'
             , 'Closed for modifications'
             , ( 'open', 'kill', 'expire' )
             , { 'Modify content':  () }
             , ()
             , { 'is_opened':  False, 'is_closed':  True }
             )
, 'opened':  ( 'Opened'
             , 'Open for modifications'
             , ( 'close', 'kill', 'expire' )
             , { 'Modify content':  [ 'Owner', 'Manager' ] }
             , [ ( 'Content_owners', ( 'Owner', ) ) ]
             , { 'is_opened':  True, 'is_closed':  True }
             )
, 'killed':  ( 'Killed'
             , 'Permanently unavailable'
             , ()
             , {}
             , ()
             , {}
             )
, 'expired': ( 'Expired'
             , 'Expiration date has passed'
             , ( 'open', )
             , { 'Modify content':  [ 'Owner', 'Manager' ] }
             , ()
             , { 'is_opened':  False, 'is_closed':  False }
             )
}

_WF_TRANSITIONS = \
{ 'open':    ( 'Open'
             , 'Open the object for modifications'
             , 'opened'
             , TRIGGER_USER_ACTION
             , 'before_open'
             , ''
             , 'Open'
             , 'string:${object_url}/open_for_modifications'
             , 'workflow'
             , { 'when_opened' : 'object/ZopeTime' }
             , ( 'Open content for modifications', )
             , ()
             , ()
             , ""
             )
, 'close':   ( 'Close'
             , 'Close the object for modifications'
             , 'closed'
             , TRIGGER_USER_ACTION
             , ''
             , 'after_close'
             , 'Close'
             , 'string:${object_url}/close_for_modifications'
             , 'workflow'
             , {}
             , ()
             , ( 'Owner', 'Manager' )
             , ()
             , ""
             )
, 'kill':    ( 'Kill'
             , 'Make the object permanently unavailable.'
             , 'killed'
             , TRIGGER_USER_ACTION
             , ''
             , 'after_kill'
             , 'Kill'
             , 'string:${object_url}/kill_object'
             , 'workflow'
             , { 'killed_by' : 'string:${user/getId}' }
             , ()
             , ()
             , ( 'Content assassins', )
             , ""
             )
, 'expire':  ( 'Expire'
             , 'Retire objects whose expiration is past.'
             , 'expired'
             , TRIGGER_AUTOMATIC
             , ''
             , ''
             , ''
             , ''
             , ''
             , { 'when_expired' : 'object/ZopeTime' }
             , ()
             , ()
             , ()
             , "python: object.expiration() <= object.ZopeTime()"
             )
}

_WF_WORKLISTS = \
{ 'expired_list':   ( 'Expired'
                    , 'Worklist for expired content'
                    , { 'state' : ( 'expired', ) }
                    , 'Expired items'
                    , 'string:${portal_url}/expired_items'
                    , 'workflow'
                    , ( 'Restore expired content', )
                    , ()
                    , ()
                    , ""
                    )
, 'alive_list':     ( 'Alive'
                    , 'Worklist for content not yet expired / killed'
                    , { 'state' : ( 'open',  'closed' ) }
                    , 'Expired items'
                    , 'string:${portal_url}/expired_items'
                    , 'workflow'
                    , ( 'Restore expired content', )
                    , ()
                    , ()
                    , ""
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
