##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Unit tests for export / import of DCWorkflows and bindings.

$Id$
"""

import unittest
import Testing
import Zope
Zope.startup()

from OFS.Folder import Folder
from Products.PythonScripts.PythonScript import PythonScript

from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.DCWorkflow.Transitions import TRIGGER_USER_ACTION
from Products.DCWorkflow.Transitions import TRIGGER_AUTOMATIC

from common import BaseRegistryTests
from common import DummyExportContext
from common import DummyImportContext


class DummyWorkflowTool( Folder ):

    def __init__( self, id='portal_workflow' ):
        Folder.__init__( self, id )
        self._default_chain = ()
        self._chains_by_type = {}

    def getWorkflowIds( self ):

        return self.objectIds()

    def getWorkflowById( self, workflow_id ):

        return self._getOb( workflow_id )

    def setDefaultChain( self, chain ):

        chain = chain.replace( ',', ' ' )
        self._default_chain = tuple( chain.split() )

    def setChainForPortalTypes( self, pt_names, chain ):

        chain = chain.replace( ',', ' ' )
        chain = tuple( chain.split() )

        if self._chains_by_type is None:
            self._chains_by_type = {}

        for pt_name in pt_names:
            self._chains_by_type[ pt_name ] = chain

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

        self.assertEqual( len( info[ 'guard_permissions' ] )
                        , len( permissions ) )

        for expected in permissions:
            self.failUnless( expected in info[ 'guard_permissions' ] )

        self.assertEqual( len( info[ 'guard_roles' ] )
                        , len( roles ) )

        for expected in roles:
            self.failUnless( expected in info[ 'guard_roles' ] )

        self.assertEqual( len( info[ 'guard_groups' ] )
                        , len( groups ) )

        for expected in groups:
            self.failUnless( expected in info[ 'guard_groups' ] )

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

        dcworkflow.groups = _WF_GROUPS

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

    def _initScripts( self, dcworkflow ):

        for k, v in _WF_SCRIPTS.items():

            if v[ 0 ] == PythonScript.meta_type:
                script = PythonScript( k )
                script.write( v[ 1 ] )

            else:
                raise ValueError, 'Unknown script type: %s' % v[ 0 ]

            dcworkflow.scripts._setObject( k, script )

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

            groups = info[ 'groups' ]
            self.assertEqual( len( groups ), len( expected[ 4 ] ) )

            for i in range( len( groups ) ):
                self.assertEqual( groups[ i ], expected[ 4 ][ i ] )

            variables = info[ 'variables' ]
            self.assertEqual( len( variables ), len( expected[ 5 ] ) )

            for v_info in variables:

                name, type, value = ( v_info[ 'name' ]
                                    , v_info[ 'type' ], v_info[ 'value' ] )

                self.assertEqual( value, expected[ 5 ][ name ] )

                if isinstance( value, bool ):
                    self.assertEqual( type, 'bool' )
                elif isinstance( value, int ):
                    self.assertEqual( type, 'int' )
                elif isinstance( value, float ):
                    self.assertEqual( type, 'float' )
                elif isinstance( value, basestring ):
                    self.assertEqual( type, 'string' )

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

            for v_info in variables:
                self.assertEqual( v_info[ 'expr' ]
                                , expected[ 9 ][ v_info[ 'name' ] ] )

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

    def test_getWorkflowInfo_dcworkflow_scripts( self ):

        WF_ID = 'dcworkflow_scripts'

        site = self._initSite()
        dcworkflow = self._initDCWorkflow( WF_ID )
        self._initScripts( dcworkflow )

        configurator = self._makeOne( site ).__of__( site )
        info = configurator.getWorkflowInfo( WF_ID )

        script_info = info[ 'script_info' ]
        self.assertEqual( len( script_info ), len( _WF_SCRIPTS ) )

        ids = [ x[ 'id' ] for x in script_info ]

        for k in _WF_SCRIPTS.keys():
            self.failUnless( k in ids )

        for info in script_info:

            expected = _WF_SCRIPTS[ info[ 'id' ] ]

            self.assertEqual( info[ 'meta_type' ], expected[ 0 ] )
            self.assertEqual( info[ 'body' ], expected[ 1 ] )
            self.assertEqual( info[ 'filename' ]
                            , expected[ 2 ] % WF_ID )


    def test_listWorkflowInfo_empty( self ):

        site = self._initSite()

        configurator = self._makeOne( site ).__of__( site )

        self.assertEqual( len( configurator.listWorkflowInfo() ), 0 )

    def test_listWorkflowInfo_mixed( self ):

        from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition

        site = self._initSite()

        WF_ID_NON = 'non_dcworkflow'
        WF_TITLE_NON = 'Non-DCWorkflow'
        WF_ID_DC = 'dcworkflow'
        WF_TITLE_DC = 'DCWorkflow'

        site = self._initSite()

        wf_tool = site.portal_workflow
        nondcworkflow = DummyWorkflow( WF_TITLE_NON )
        nondcworkflow.title = WF_TITLE_NON
        wf_tool._setObject( WF_ID_NON, nondcworkflow )

        dcworkflow = self._initDCWorkflow( WF_ID_DC )
        dcworkflow.title = WF_TITLE_DC

        configurator = self._makeOne( site ).__of__( site )

        info_list = configurator.listWorkflowInfo()

        self.assertEqual( len( info_list ), 2 )

        non_info = [ x for x in info_list if x[ 'id' ] == WF_ID_NON ][0]
        self.assertEqual( non_info[ 'title' ], WF_TITLE_NON )
        self.assertEqual( non_info[ 'meta_type' ], DummyWorkflow.meta_type )

        dc_info = [ x for x in info_list if x[ 'id' ] == WF_ID_DC ][0]
        self.assertEqual( dc_info[ 'title' ], WF_TITLE_DC )
        self.assertEqual( dc_info[ 'meta_type' ]
                        , DCWorkflowDefinition.meta_type )
        self.assertEqual( dc_info[ 'filename' ]
                        , 'workflows/%s/definition.xml' % WF_ID_DC )

    def test_listWorkflowChains_no_default( self ):

        site = self._initSite()
        configurator = self._makeOne( site ).__of__( site )

        chains = configurator.listWorkflowChains()

        default_chain = [ x[1] for x in chains if x[0] is None ][0]
        self.assertEqual( len( default_chain ), 0 )

    def test_listWorkflowChains_with_default( self ):

        site = self._initSite()
        site.portal_workflow._default_chain = ( 'foo', 'bar' )
        configurator = self._makeOne( site ).__of__( site )

        chains = configurator.listWorkflowChains()

        self.assertEqual( chains[ 0 ][ 0 ], None )
        default_chain = chains[ 0 ][ 1 ]
        self.assertEqual( len( default_chain ), 2 )
        self.assertEqual( default_chain[ 0 ], 'foo' )
        self.assertEqual( default_chain[ 1 ], 'bar' )

    def test_listWorkflowChains_no_overrides( self ):

        site = self._initSite()
        configurator = self._makeOne( site ).__of__( site )

        chains = configurator.listWorkflowChains()

        self.assertEqual( len( chains ), 1 )

    def test_listWorkflowChains_with_overrides( self ):

        site = self._initSite()
        site.portal_workflow._chains_by_type[ 'qux' ] = ( 'foo', 'bar' )
        configurator = self._makeOne( site ).__of__( site )

        chains = configurator.listWorkflowChains()

        self.assertEqual( len( chains ), 2 )

        self.assertEqual( chains[ 0 ][ 0 ], None )
        default_chain = chains[ 0 ][ 1 ]
        self.assertEqual( len( default_chain ), 0 )

        self.assertEqual( chains[ 1 ][ 0 ], 'qux' )
        qux_chain = chains[ 1 ][ 1 ]
        self.assertEqual( len( qux_chain ), 2 )
        self.assertEqual( qux_chain[ 0 ], 'foo' )
        self.assertEqual( qux_chain[ 1 ], 'bar' )

    def test_listWorkflowChains_default_chain_plus_overrides( self ):

        site = self._initSite()
        site.portal_workflow._default_chain = ( 'foo', 'bar' )
        site.portal_workflow._chains_by_type[ 'qux' ] = ( 'baz', )
        configurator = self._makeOne( site ).__of__( site )

        chains = configurator.listWorkflowChains()

        self.assertEqual( chains[ 0 ][ 0 ], None )
        default_chain = chains[ 0 ][ 1 ]
        self.assertEqual( len( default_chain ), 2 )
        self.assertEqual( default_chain[ 0 ], 'foo' )
        self.assertEqual( default_chain[ 1 ], 'bar' )

        self.assertEqual( chains[ 1 ][ 0 ], 'qux' )
        qux_chain = chains[ 1 ][ 1 ]
        self.assertEqual( len( qux_chain ), 1 )
        self.assertEqual( qux_chain[ 0 ], 'baz' )

    def test_generateToolXML_empty( self ):

        site = self._initSite()
        configurator = self._makeOne( site ).__of__( site )
        self._compareDOM( configurator.generateToolXML(), _EMPTY_TOOL_EXPORT )

    def test_generateToolXML_default_chain_plus_overrides( self ):

        site = self._initSite()
        site.portal_workflow._default_chain = ( 'foo', 'bar' )
        site.portal_workflow._chains_by_type[ 'qux' ] = ( 'baz', )

        configurator = self._makeOne( site ).__of__( site )

        self._compareDOM( configurator.generateToolXML()
                        , _OVERRIDE_TOOL_EXPORT )

    def test_generateToolXML_mixed( self ):

        WF_ID_NON = 'non_dcworkflow'
        WF_TITLE_NON = 'Non-DCWorkflow'
        WF_ID_DC = 'dcworkflow'
        WF_TITLE_DC = 'DCWorkflow'

        site = self._initSite()

        wf_tool = site.portal_workflow
        nondcworkflow = DummyWorkflow( WF_TITLE_NON )
        nondcworkflow.title = WF_TITLE_NON
        wf_tool._setObject( WF_ID_NON, nondcworkflow )

        dcworkflow = self._initDCWorkflow( WF_ID_DC )
        dcworkflow.title = WF_TITLE_DC

        configurator = self._makeOne( site ).__of__( site )

        self._compareDOM( configurator.generateToolXML(), _NORMAL_TOOL_EXPORT )

    def test_generateWorkflowXML_empty( self ):

        WF_ID = 'empty'
        WF_TITLE = 'Empty DCWorkflow'
        WF_INITIAL_STATE = 'initial'

        site = self._initSite()
        dcworkflow = self._initDCWorkflow( WF_ID )
        dcworkflow.title = WF_TITLE
        dcworkflow.initial_state = WF_INITIAL_STATE

        configurator = self._makeOne( site ).__of__( site )

        self._compareDOM( configurator.generateWorkflowXML( WF_ID )
                        , _EMPTY_WORKFLOW_EXPORT % ( WF_ID
                                                   , WF_TITLE
                                                   , WF_INITIAL_STATE
                                                   ) )

    def test_generateWorkflowXML_nondc( self ):

        WF_ID_NON = 'non_dcworkflow'
        WF_TITLE_NON = 'Non-DCWorkflow'

        site = self._initSite()

        wf_tool = site.portal_workflow
        nondcworkflow = DummyWorkflow( WF_TITLE_NON )
        nondcworkflow.title = WF_TITLE_NON
        wf_tool._setObject( WF_ID_NON, nondcworkflow )

        configurator = self._makeOne( site ).__of__( site )

        self.assertEqual( configurator.generateWorkflowXML( WF_ID_NON ), None )

    def test_generateWorkflowXML_normal( self ):

        WF_ID = 'normal'
        WF_TITLE = 'Normal DCWorkflow'
        WF_INITIAL_STATE = 'closed'

        site = self._initSite()
        dcworkflow = self._initDCWorkflow( WF_ID )
        dcworkflow.title = WF_TITLE
        dcworkflow.initial_state = WF_INITIAL_STATE
        dcworkflow.permissions = _WF_PERMISSIONS
        self._initVariables( dcworkflow )
        self._initStates( dcworkflow )
        self._initTransitions( dcworkflow )
        self._initWorklists( dcworkflow )
        self._initScripts( dcworkflow )

        configurator = self._makeOne( site ).__of__( site )

        self._compareDOM( configurator.generateWorkflowXML( WF_ID )
                        , _NORMAL_WORKFLOW_EXPORT
                          % { 'workflow_id' : WF_ID
                            , 'title' : WF_TITLE
                            , 'initial_state' : WF_INITIAL_STATE
                            , 'workflow_filename' : WF_ID.replace(' ', '_')
                            } )

    def test_generateWorkflowXML_multiple( self ):

        WF_ID_1 = 'dc1'
        WF_TITLE_1 = 'Normal DCWorkflow #1'
        WF_ID_2 = 'dc2'
        WF_TITLE_2 = 'Normal DCWorkflow #2'
        WF_INITIAL_STATE = 'closed'

        site = self._initSite()

        dcworkflow_1 = self._initDCWorkflow( WF_ID_1 )
        dcworkflow_1.title = WF_TITLE_1
        dcworkflow_1.initial_state = WF_INITIAL_STATE
        dcworkflow_1.permissions = _WF_PERMISSIONS
        self._initVariables( dcworkflow_1 )
        self._initStates( dcworkflow_1 )
        self._initTransitions( dcworkflow_1 )
        self._initWorklists( dcworkflow_1 )
        self._initScripts( dcworkflow_1 )

        dcworkflow_2 = self._initDCWorkflow( WF_ID_2 )
        dcworkflow_2.title = WF_TITLE_2
        dcworkflow_2.initial_state = WF_INITIAL_STATE
        dcworkflow_2.permissions = _WF_PERMISSIONS
        self._initVariables( dcworkflow_2 )
        self._initStates( dcworkflow_2 )
        self._initTransitions( dcworkflow_2 )
        self._initWorklists( dcworkflow_2 )
        self._initScripts( dcworkflow_2 )

        configurator = self._makeOne( site ).__of__( site )

        self._compareDOM( configurator.generateWorkflowXML( WF_ID_1 )
                        , _NORMAL_WORKFLOW_EXPORT
                          % { 'workflow_id' : WF_ID_1
                            , 'title' : WF_TITLE_1
                            , 'initial_state' : WF_INITIAL_STATE
                            , 'workflow_filename' : WF_ID_1.replace(' ', '_')
                            } )

        self._compareDOM( configurator.generateWorkflowXML( WF_ID_2 )
                        , _NORMAL_WORKFLOW_EXPORT
                          % { 'workflow_id' : WF_ID_2
                            , 'title' : WF_TITLE_2
                            , 'initial_state' : WF_INITIAL_STATE
                            , 'workflow_filename' : WF_ID_2.replace(' ', '_')
                            } )

    def test_parseToolXML_empty( self ):

        site = self._initSite()
        configurator = self._makeOne( site ).__of__( site )

        workflows, bindings = configurator.parseToolXML( _EMPTY_TOOL_EXPORT )

        self.assertEqual( len( workflows ), 0 )
        self.assertEqual( len( bindings ), 1 )

    def test_parseToolXML_default_chain_plus_overrides( self ):

        site = self._initSite()
        configurator = self._makeOne( site ).__of__( site )

        workflows, bindings = configurator.parseToolXML( _OVERRIDE_TOOL_EXPORT )

        self.assertEqual( len( workflows ), 0 )
        self.assertEqual( len( bindings ), 2 )

        default = bindings[ None ]
        self.assertEqual( len( default ), 2 )
        self.assertEqual( default[ 0 ], 'foo' )
        self.assertEqual( default[ 1 ], 'bar' )

        override = bindings[ 'qux' ]
        self.assertEqual( len( override ), 1 )
        self.assertEqual( override[ 0 ], 'baz' )

    def test_parseToolXML_normal( self ):

        site = self._initSite()
        configurator = self._makeOne( site ).__of__( site )

        workflows, bindings = configurator.parseToolXML( _NORMAL_TOOL_EXPORT )

        self.assertEqual( len( workflows ), 2 )

        wfid, meta_type, filename = workflows[ 0 ]
        self.assertEqual( wfid, 'non_dcworkflow' )
        self.assertEqual( meta_type, DummyWorkflow.meta_type )
        self.assertEqual( filename, None )

        wfid, meta_type, filename = workflows[ 1 ]
        self.assertEqual( wfid, 'dcworkflow' )
        self.assertEqual( meta_type, DCWorkflowDefinition.meta_type )
        self.assertEqual( filename, 'workflows/dcworkflow/definition.xml' )

        self.assertEqual( len( bindings ), 1 )

    def test_parseWorkflowXML_empty( self ):

        WF_ID = 'empty'
        WF_TITLE = 'Empty DCWorkflow'
        WF_INITIAL_STATE = 'initial'

        site = self._initSite()

        configurator = self._makeOne( site ).__of__( site )

        ( workflow_id
        , title
        , state_variable
        , initial_state
        , states
        , transitions
        , variables
        , worklists
        , permissions
        , scripts
        ) = configurator.parseWorkflowXML( _EMPTY_WORKFLOW_EXPORT
                                         % ( WF_ID
                                           , WF_TITLE
                                           , WF_INITIAL_STATE
                                           ) )

        self.assertEqual( len( states ), 0 )
        self.assertEqual( len( transitions ), 0 )
        self.assertEqual( len( variables ), 0 )
        self.assertEqual( len( worklists ), 0 )
        self.assertEqual( len( permissions ), 0 )
        self.assertEqual( len( scripts ), 0 )

    def test_parseWorkflowXML_normal_attribs( self ):

        WF_ID = 'normal'
        WF_TITLE = 'Normal DCWorkflow'
        WF_INITIAL_STATE = 'closed'

        site = self._initSite()

        configurator = self._makeOne( site ).__of__( site )

        ( workflow_id
        , title
        , state_variable
        , initial_state
        , states
        , transitions
        , variables
        , worklists
        , permissions
        , scripts
        ) = configurator.parseWorkflowXML(
                          _NORMAL_WORKFLOW_EXPORT
                          % { 'workflow_id' : WF_ID
                            , 'title' : WF_TITLE
                            , 'initial_state' : WF_INITIAL_STATE
                            , 'workflow_filename' : WF_ID.replace(' ', '_')
                            } )

        self.assertEqual( workflow_id, WF_ID )
        self.assertEqual( title, WF_TITLE )
        self.assertEqual( state_variable, 'state' )
        self.assertEqual( initial_state, WF_INITIAL_STATE )

    def test_parseWorkflowXML_normal_states( self ):

        WF_ID = 'normal'
        WF_TITLE = 'Normal DCWorkflow'
        WF_INITIAL_STATE = 'closed'

        site = self._initSite()

        configurator = self._makeOne( site ).__of__( site )

        ( workflow_id
        , title
        , state_variable
        , initial_state
        , states
        , transitions
        , variables
        , worklists
        , permissions
        , scripts
        ) = configurator.parseWorkflowXML(
                          _NORMAL_WORKFLOW_EXPORT
                          % { 'workflow_id' : WF_ID
                            , 'title' : WF_TITLE
                            , 'initial_state' : WF_INITIAL_STATE
                            , 'workflow_filename' : WF_ID.replace(' ', '_')
                            } )

        self.assertEqual( len( states ), len( _WF_STATES ) )

        for state in states:

            state_id = state[ 'state_id' ]
            self.failUnless( state_id in _WF_STATES )

            expected = _WF_STATES[ state_id ]

            self.assertEqual( state[ 'title' ], expected[ 0 ] )

            description = ''.join( state[ 'description' ] )
            self.failUnless( expected[ 1 ] in description )

            self.assertEqual( tuple( state[ 'transitions' ] ), expected[ 2 ] )
            self.assertEqual( state[ 'permissions' ], expected[ 3 ] )
            self.assertEqual( tuple( state[ 'groups' ] )
                            , tuple( expected[ 4 ] ) )

            for k, v_info in state[ 'variables' ].items():

                exp_value = expected[ 5 ][ k ]
                self.assertEqual( v_info[ 'value' ], str( exp_value ) )

                if isinstance( exp_value, bool ):
                    self.assertEqual( v_info[ 'type' ], 'bool' )
                elif isinstance( exp_value, int ):
                    self.assertEqual( v_info[ 'type' ], 'int' )
                elif isinstance( exp_value, float ):
                    self.assertEqual( v_info[ 'type' ], 'float' )
                elif isinstance( exp_value, basestring ):
                    self.assertEqual( v_info[ 'type' ], 'string' )

    def test_parseWorkflowXML_normal_transitions( self ):

        from Products.CMFSetup.workflow import TRIGGER_TYPES

        WF_ID = 'normal'
        WF_TITLE = 'Normal DCWorkflow'
        WF_INITIAL_STATE = 'closed'

        site = self._initSite()

        configurator = self._makeOne( site ).__of__( site )

        ( workflow_id
        , title
        , state_variable
        , initial_state
        , states
        , transitions
        , variables
        , worklists
        , permissions
        , scripts
        ) = configurator.parseWorkflowXML(
                          _NORMAL_WORKFLOW_EXPORT
                          % { 'workflow_id' : WF_ID
                            , 'title' : WF_TITLE
                            , 'initial_state' : WF_INITIAL_STATE
                            , 'workflow_filename' : WF_ID.replace(' ', '_')
                            } )

        self.assertEqual( len( transitions ), len( _WF_TRANSITIONS ) )

        for transition in transitions:

            transition_id = transition[ 'transition_id' ]
            self.failUnless( transition_id in _WF_TRANSITIONS )

            expected = _WF_TRANSITIONS[ transition_id ]

            self.assertEqual( transition[ 'title' ], expected[ 0 ] )

            description = ''.join( transition[ 'description' ] )
            self.failUnless( expected[ 1 ] in description )

            self.assertEqual( transition[ 'new_state' ], expected[ 2 ] )
            self.assertEqual( transition[ 'trigger' ]
                            , TRIGGER_TYPES[ expected[ 3 ] ] )
            self.assertEqual( transition[ 'before_script' ], expected[ 4 ] )
            self.assertEqual( transition[ 'after_script' ]
                            , expected[ 5 ] )

            action = transition[ 'action' ]
            self.assertEqual( action.get( 'name', '' ), expected[ 6 ] )
            self.assertEqual( action.get( 'url', '' ), expected[ 7 ] )
            self.assertEqual( action.get( 'category', '' ), expected[ 8 ] )

            self.assertEqual( transition[ 'variables' ], expected[ 9 ] )

            guard = transition[ 'guard' ]
            self.assertEqual( tuple( guard.get( 'permissions', () ) )
                            , expected[ 10 ] )
            self.assertEqual( tuple( guard.get( 'roles', () ) )
                            , expected[ 11 ] )
            self.assertEqual( tuple( guard.get( 'groups', () ) )
                            , expected[ 12 ] )
            self.assertEqual( guard.get( 'expression', '' ), expected[ 13 ] )

    def test_parseWorkflowXML_normal_variables( self ):

        from Products.CMFSetup.workflow import TRIGGER_TYPES

        WF_ID = 'normal'
        WF_TITLE = 'Normal DCWorkflow'
        WF_INITIAL_STATE = 'closed'

        site = self._initSite()

        configurator = self._makeOne( site ).__of__( site )

        ( workflow_id
        , title
        , state_variable
        , initial_state
        , states
        , transitions
        , variables
        , worklists
        , permissions
        , scripts
        ) = configurator.parseWorkflowXML(
                          _NORMAL_WORKFLOW_EXPORT
                          % { 'workflow_id' : WF_ID
                            , 'title' : WF_TITLE
                            , 'initial_state' : WF_INITIAL_STATE
                            , 'workflow_filename' : WF_ID.replace(' ', '_')
                            } )

        self.assertEqual( len( variables ), len( _WF_VARIABLES ) )

        for variable in variables:

            variable_id = variable[ 'variable_id' ]
            self.failUnless( variable_id in _WF_VARIABLES )

            expected = _WF_VARIABLES[ variable_id ]

            description = ''.join( variable[ 'description' ] )
            self.failUnless( expected[ 0 ] in description )

            default = variable[ 'default' ]
            self.assertEqual( default[ 'value' ], expected[ 1 ] )

            exp_type = 'n/a'

            if expected[ 1 ]:
                exp_value = expected[ 1 ]

                if isinstance( exp_value, bool ):
                    exp_type = 'bool'
                elif isinstance( exp_value, int ):
                    exp_type = 'int'
                elif isinstance( exp_value, float ):
                    exp_type = 'float'
                elif isinstance( exp_value, basestring ):
                    exp_type = 'string'
                else:
                    exp_type = 'XXX'

            self.assertEqual( default[ 'type' ], exp_type )
            self.assertEqual( default[ 'expression' ], expected[ 2 ] )

            self.assertEqual( variable[ 'for_catalog' ], expected[ 3 ] )
            self.assertEqual( variable[ 'for_status' ], expected[ 4 ] )
            self.assertEqual( variable[ 'update_always' ], expected[ 5 ] )

            guard = variable[ 'guard' ]
            self.assertEqual( tuple( guard.get( 'permissions', () ) )
                            , expected[ 6 ] )
            self.assertEqual( tuple( guard.get( 'roles', () ) )
                            , expected[ 7 ] )
            self.assertEqual( tuple( guard.get( 'groups', () ) )
                            , expected[ 8 ] )
            self.assertEqual( guard.get( 'expression', '' ), expected[ 9 ] )

    def test_parseWorkflowXML_normal_worklists( self ):

        from Products.CMFSetup.workflow import TRIGGER_TYPES

        WF_ID = 'normal'
        WF_TITLE = 'Normal DCWorkflow'
        WF_INITIAL_STATE = 'closed'

        site = self._initSite()

        configurator = self._makeOne( site ).__of__( site )

        ( workflow_id
        , title
        , state_variable
        , initial_state
        , states
        , transitions
        , variables
        , worklists
        , permissions
        , scripts
        ) = configurator.parseWorkflowXML(
                          _NORMAL_WORKFLOW_EXPORT
                          % { 'workflow_id' : WF_ID
                            , 'title' : WF_TITLE
                            , 'initial_state' : WF_INITIAL_STATE
                            , 'workflow_filename' : WF_ID.replace(' ', '_')
                            } )

        self.assertEqual( len( worklists ), len( _WF_WORKLISTS ) )

        for worklist in worklists:

            worklist_id = worklist[ 'worklist_id' ]
            self.failUnless( worklist_id in _WF_WORKLISTS )

            expected = _WF_WORKLISTS[ worklist_id ]

            self.assertEqual( worklist[ 'title' ], expected[ 0 ] )

            description = ''.join( worklist[ 'description' ] )
            self.failUnless( expected[ 1 ] in description )

            self.assertEqual( tuple( worklist[ 'match' ] )
                            , tuple( expected[ 2 ] ) )

            action = worklist[ 'action' ]
            self.assertEqual( action.get( 'name', '' ), expected[ 3 ] )
            self.assertEqual( action.get( 'url', '' ), expected[ 4 ] )
            self.assertEqual( action.get( 'category', '' ), expected[ 5 ] )

            guard = worklist[ 'guard' ]
            self.assertEqual( tuple( guard.get( 'permissions', () ) )
                            , expected[ 6 ] )
            self.assertEqual( tuple( guard.get( 'roles', () ) )
                            , expected[ 7 ] )
            self.assertEqual( tuple( guard.get( 'groups', () ) )
                            , expected[ 8 ] )
            self.assertEqual( guard.get( 'expression', '' ), expected[ 9 ] )

    def test_parseWorkflowXML_normal_permissions( self ):

        from Products.CMFSetup.workflow import TRIGGER_TYPES

        WF_ID = 'normal'
        WF_TITLE = 'Normal DCWorkflow'
        WF_INITIAL_STATE = 'closed'

        site = self._initSite()

        configurator = self._makeOne( site ).__of__( site )

        ( workflow_id
        , title
        , state_variable
        , initial_state
        , states
        , transitions
        , variables
        , worklists
        , permissions
        , scripts
        ) = configurator.parseWorkflowXML(
                          _NORMAL_WORKFLOW_EXPORT
                          % { 'workflow_id' : WF_ID
                            , 'title' : WF_TITLE
                            , 'initial_state' : WF_INITIAL_STATE
                            , 'workflow_filename' : WF_ID.replace(' ', '_')
                            } )

        self.assertEqual( len( permissions ), len( _WF_PERMISSIONS ) )

        for permission in permissions:

            self.failUnless( permission in _WF_PERMISSIONS )

    def test_parseWorkflowXML_normal_scripts( self ):

        from Products.CMFSetup.workflow import TRIGGER_TYPES

        WF_ID = 'normal'
        WF_TITLE = 'Normal DCWorkflow'
        WF_INITIAL_STATE = 'closed'

        site = self._initSite()

        configurator = self._makeOne( site ).__of__( site )

        ( workflow_id
        , title
        , state_variable
        , initial_state
        , states
        , transitions
        , variables
        , worklists
        , permissions
        , scripts
        ) = configurator.parseWorkflowXML(
                          _NORMAL_WORKFLOW_EXPORT
                          % { 'workflow_id' : WF_ID
                            , 'title' : WF_TITLE
                            , 'initial_state' : WF_INITIAL_STATE
                            , 'workflow_filename' : WF_ID.replace(' ', '_')
                            } )

        self.assertEqual( len( scripts ), len( _WF_SCRIPTS ) )

        for script in scripts:

            script_id = script[ 'script_id' ]
            self.failUnless( script_id in _WF_SCRIPTS )

            expected = _WF_SCRIPTS[ script_id ]

            self.assertEqual( script[ 'meta_type' ], expected[ 0 ] )

            # Body is not kept as part of the workflow XML

            self.assertEqual( script[ 'filename' ]
                            , expected[ 2 ] % workflow_id )


_WF_PERMISSIONS = \
( 'Open content for modifications'
, 'Modify content'
, 'Query history'
, 'Restore expired content'
)

_WF_GROUPS = \
( 'Content_owners'
, 'Content_assassins'
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
             , { 'is_opened':  True, 'is_closed':  False }
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
             , ( 'Content_assassins', )
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

_BEFORE_OPEN_SCRIPT = """\
## Script (Python) "before_open"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
return 'before_open'
"""

_AFTER_CLOSE_SCRIPT = """\
## Script (Python) "after_close"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
return 'after_close'
"""

_AFTER_KILL_SCRIPT = """\
## Script (Python) "after_kill"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
return 'after_kill'
"""

_WF_SCRIPTS = \
{ 'before_open':    ( PythonScript.meta_type
                    , _BEFORE_OPEN_SCRIPT
                    , 'workflows/%s/before_open.py'
                    )
, 'after_close':    ( PythonScript.meta_type
                    , _AFTER_CLOSE_SCRIPT
                    , 'workflows/%s/after_close.py'
                    )
, 'after_kill':     ( PythonScript.meta_type
                    , _AFTER_KILL_SCRIPT
                    , 'workflows/%s/after_kill.py'
                    )
}

_EMPTY_TOOL_EXPORT = """\
<?xml version="1.0"?>
<workflow-tool>
 <bindings>
  <default>
  </default>
 </bindings>
</workflow-tool>
"""

_BINDINGS_TOOL_EXPORT = """\
<?xml version="1.0"?>
<workflow-tool>
 <bindings>
  <default>
   <bound-workflow workflow_id="non_dcworkflow_0" />
   <bound-workflow workflow_id="non_dcworkflow_1" />
  </default>
  <type type_id="sometype">
   <bound-workflow workflow_id="non_dcworkflow_2" />
  </type>
  <type type_id="anothertype">
   <bound-workflow workflow_id="non_dcworkflow_3" />
  </type>
 </bindings>
</workflow-tool>
"""

_OVERRIDE_TOOL_EXPORT = """\
<?xml version="1.0"?>
<workflow-tool>
 <bindings>
  <default>
   <bound-workflow workflow_id="foo" />
   <bound-workflow workflow_id="bar" />
  </default>
  <type type_id="qux">
   <bound-workflow workflow_id="baz" />
  </type>
 </bindings>
</workflow-tool>
"""

_NORMAL_TOOL_EXPORT = """\
<?xml version="1.0"?>
<workflow-tool>
 <workflow
    workflow_id="non_dcworkflow"
    meta_type="Dummy Workflow"
    />
 <workflow
    workflow_id="dcworkflow"
    filename="workflows/dcworkflow/definition.xml"
    meta_type="Workflow"
    />
 <bindings>
  <default>
  </default>
 </bindings>
</workflow-tool>
"""

_NORMAL_TOOL_EXPORT_WITH_FILENAME = """\
<?xml version="1.0"?>
<workflow-tool>
 <workflow
    workflow_id="non_dcworkflow"
    meta_type="Dummy Workflow"
    />
 <workflow
    workflow_id="dcworkflow"
    filename="workflows/%s/definition.xml"
    meta_type="Workflow"
    />
 <bindings>
  <default>
  </default>
 </bindings>
</workflow-tool>
"""

_FILENAME_TOOL_EXPORT = """\
<?xml version="1.0"?>
<workflow-tool>
 <workflow
    workflow_id="name with spaces"
    filename="workflows/name_with_spaces/definition.xml"
    meta_type="Workflow"
    />
 <bindings>
  <default>
  </default>
 </bindings>
</workflow-tool>
"""

_EMPTY_WORKFLOW_EXPORT = """\
<?xml version="1.0"?>
<dc-workflow
    workflow_id="%s"
    title="%s"
    state_variable="state"
    initial_state="%s">
</dc-workflow>
"""

_NORMAL_WORKFLOW_EXPORT = """\
<?xml version="1.0"?>
<dc-workflow
    workflow_id="%(workflow_id)s"
    title="%(title)s"
    state_variable="state"
    initial_state="%(initial_state)s">
 <permission>Open content for modifications</permission>
 <permission>Modify content</permission>
 <permission>Query history</permission>
 <permission>Restore expired content</permission>
 <state
    state_id="closed"
    title="Closed">
  <description>Closed for modifications</description>
  <exit-transition
    transition_id="open"/>
  <exit-transition
    transition_id="kill"/>
  <exit-transition
    transition_id="expire"/>
  <permission-map
    acquired="False"
    name="Modify content">
  </permission-map>
  <assignment
    name="is_closed"
    type="bool">True</assignment>
  <assignment
    name="is_opened"
    type="bool">False</assignment>
 </state>
 <state
    state_id="expired"
    title="Expired">
  <description>Expiration date has passed</description>
  <exit-transition
    transition_id="open"/>
  <permission-map
    acquired="True"
    name="Modify content">
   <permission-role>Owner</permission-role>
   <permission-role>Manager</permission-role>
  </permission-map>
  <assignment
    name="is_closed"
    type="bool">False</assignment>
  <assignment
    name="is_opened"
    type="bool">False</assignment>
 </state>
 <state
    state_id="killed"
    title="Killed">
  <description>Permanently unavailable</description>
 </state>
 <state
    state_id="opened"
    title="Opened">
  <description>Open for modifications</description>
  <exit-transition
    transition_id="close"/>
  <exit-transition
    transition_id="kill"/>
  <exit-transition
    transition_id="expire"/>
  <permission-map
    acquired="True"
    name="Modify content">
   <permission-role>Owner</permission-role>
   <permission-role>Manager</permission-role>
  </permission-map>
  <group-map name="Content_owners">
   <group-role>Owner</group-role>
  </group-map>
  <assignment
    name="is_closed"
    type="bool">False</assignment>
  <assignment
    name="is_opened"
    type="bool">True</assignment>
 </state>
 <transition
    transition_id="close"
    title="Close"
    trigger="USER"
    new_state="closed"
    before_script=""
    after_script="after_close">
  <description>Close the object for modifications</description>
  <action
    category="workflow"
    url="string:${object_url}/close_for_modifications">Close</action>
  <guard>
   <guard-role>Owner</guard-role>
   <guard-role>Manager</guard-role>
  </guard>
 </transition>
 <transition
    transition_id="expire"
    title="Expire"
    trigger="AUTOMATIC"
    new_state="expired"
    before_script=""
    after_script="">
  <description>Retire objects whose expiration is past.</description>
  <guard>
   <guard-expression>python: object.expiration() &lt;= object.ZopeTime()</guard-expression>
  </guard>
  <assignment
    name="when_expired">object/ZopeTime</assignment>
 </transition>
 <transition
    transition_id="kill"
    title="Kill"
    trigger="USER"
    new_state="killed"
    before_script=""
    after_script="after_kill">
  <description>Make the object permanently unavailable.</description>
  <action
    category="workflow"
    url="string:${object_url}/kill_object">Kill</action>
  <guard>
   <guard-group>Content_assassins</guard-group>
  </guard>
  <assignment
    name="killed_by">string:${user/getId}</assignment>
 </transition>
 <transition
    transition_id="open"
    title="Open"
    trigger="USER"
    new_state="opened"
    before_script="before_open"
    after_script="">
  <description>Open the object for modifications</description>
  <action
    category="workflow"
    url="string:${object_url}/open_for_modifications">Open</action>
  <guard>
   <guard-permission>Open content for modifications</guard-permission>
  </guard>
  <assignment
    name="when_opened">object/ZopeTime</assignment>
 </transition>
 <worklist
    worklist_id="alive_list"
    title="Alive">
  <description>Worklist for content not yet expired / killed</description>
  <action
    category="workflow"
    url="string:${portal_url}/expired_items">Expired items</action>
  <guard>
   <guard-permission>Restore expired content</guard-permission>
  </guard>
  <match name="state" values="open; closed"/>
 </worklist>
 <worklist
    worklist_id="expired_list"
    title="Expired">
  <description>Worklist for expired content</description>
  <action
    category="workflow"
    url="string:${portal_url}/expired_items">Expired items</action>
  <guard>
   <guard-permission>Restore expired content</guard-permission>
  </guard>
  <match name="state" values="expired"/>
 </worklist>
 <variable
    variable_id="killed_by"
    for_catalog="True"
    for_status="False"
    update_always="True">
   <description>Killed by</description>
   <default>
    <value type="string">n/a</value>
   </default>
   <guard>
    <guard-role>Hangman</guard-role>
    <guard-role>Sherrif</guard-role>
   </guard>
 </variable>
 <variable
    variable_id="when_expired"
    for_catalog="True"
    for_status="False"
    update_always="True">
   <description>Expired when</description>
   <default>
    <expression>nothing</expression>
   </default>
   <guard>
    <guard-permission>Query history</guard-permission>
    <guard-permission>Open content for modifications</guard-permission>
   </guard>
 </variable>
 <variable
    variable_id="when_opened"
    for_catalog="True"
    for_status="False"
    update_always="True">
   <description>Opened when</description>
   <default>
    <expression>python:None</expression>
   </default>
   <guard>
    <guard-permission>Query history</guard-permission>
    <guard-permission>Open content for modifications</guard-permission>
   </guard>
 </variable>
 <script
    script_id="after_close"
    type="Script (Python)"
    filename="workflows/%(workflow_filename)s/after_close.py"
    />
 <script
    script_id="after_kill"
    type="Script (Python)"
    filename="workflows/%(workflow_filename)s/after_kill.py"
    />
 <script
    script_id="before_open"
    type="Script (Python)"
    filename="workflows/%(workflow_filename)s/before_open.py"
    />
</dc-workflow>
"""

class Test_exportWorkflow( _WorkflowSetup
                         , _GuardChecker
                         ):

    def test_empty( self ):

        site = self._initSite()
        context = DummyExportContext( site )

        from Products.CMFSetup.workflow import exportWorkflowTool
        exportWorkflowTool( context )

        self.assertEqual( len( context._wrote ), 1 )
        filename, text, content_type = context._wrote[ 0 ]
        self.assertEqual( filename, 'workflows.xml' )
        self._compareDOM( text, _EMPTY_TOOL_EXPORT )
        self.assertEqual( content_type, 'text/xml' )

    def test_normal( self ):

        WF_ID_NON = 'non_dcworkflow'
        WF_TITLE_NON = 'Non-DCWorkflow'
        WF_ID_DC = 'dcworkflow'
        WF_TITLE_DC = 'DCWorkflow'
        WF_INITIAL_STATE = 'closed'

        site = self._initSite()

        wf_tool = site.portal_workflow
        nondcworkflow = DummyWorkflow( WF_TITLE_NON )
        nondcworkflow.title = WF_TITLE_NON
        wf_tool._setObject( WF_ID_NON, nondcworkflow )

        dcworkflow = self._initDCWorkflow( WF_ID_DC )
        dcworkflow.title = WF_TITLE_DC
        dcworkflow.initial_state = WF_INITIAL_STATE
        dcworkflow.permissions = _WF_PERMISSIONS
        self._initVariables( dcworkflow )
        self._initStates( dcworkflow )
        self._initTransitions( dcworkflow )
        self._initWorklists( dcworkflow )
        self._initScripts( dcworkflow )

        context = DummyExportContext( site )

        from Products.CMFSetup.workflow import exportWorkflowTool
        exportWorkflowTool( context )

        self.assertEqual( len( context._wrote ), 2 )

        filename, text, content_type = context._wrote[ 0 ]
        self.assertEqual( filename, 'workflows.xml' )
        self._compareDOM( text, _NORMAL_TOOL_EXPORT )
        self.assertEqual( content_type, 'text/xml' )

        filename, text, content_type = context._wrote[ 1 ]
        self.assertEqual( filename, 'workflows/%s/definition.xml' % WF_ID_DC )
        self._compareDOM( text
                        , _NORMAL_WORKFLOW_EXPORT
                          % { 'workflow_id' : WF_ID_DC
                            , 'title' : WF_TITLE_DC
                            , 'initial_state' : WF_INITIAL_STATE
                            , 'workflow_filename' : WF_ID_DC.replace(' ', '_')
                            } )
        self.assertEqual( content_type, 'text/xml' )

    def test_with_filenames( self ):

        WF_ID_DC = 'name with spaces'
        WF_TITLE_DC = 'DCWorkflow with spaces'
        WF_INITIAL_STATE = 'closed'

        site = self._initSite()

        dcworkflow = self._initDCWorkflow( WF_ID_DC )
        dcworkflow.title = WF_TITLE_DC
        dcworkflow.initial_state = WF_INITIAL_STATE
        dcworkflow.permissions = _WF_PERMISSIONS
        self._initVariables( dcworkflow )
        self._initStates( dcworkflow )
        self._initTransitions( dcworkflow )
        self._initWorklists( dcworkflow )
        self._initScripts( dcworkflow )

        context = DummyExportContext( site )

        from Products.CMFSetup.workflow import exportWorkflowTool
        exportWorkflowTool( context )

        self.assertEqual( len( context._wrote ), 2 )

        filename, text, content_type = context._wrote[ 0 ]
        self.assertEqual( filename, 'workflows.xml' )
        self._compareDOM( text, _FILENAME_TOOL_EXPORT )
        self.assertEqual( content_type, 'text/xml' )

        filename, text, content_type = context._wrote[ 1 ]
        self.assertEqual( filename
                        , 'workflows/name_with_spaces/definition.xml' )
        self._compareDOM( text
                        , _NORMAL_WORKFLOW_EXPORT
                          % { 'workflow_id' : WF_ID_DC
                            , 'title' : WF_TITLE_DC
                            , 'initial_state' : WF_INITIAL_STATE
                            , 'workflow_filename' : WF_ID_DC.replace(' ', '_')
                            } )
        self.assertEqual( content_type, 'text/xml' )

class Test_importWorkflow( _WorkflowSetup
                         , _GuardChecker
                         ):

    def _importNormalWorkflow( self, wf_id, wf_title, wf_initial_state ):

        site = self._initSite()
        wf_tool = site.portal_workflow
        workflow_filename = wf_id.replace(' ', '_')

        context = DummyImportContext( site )
        context._files[ 'workflows.xml'
                      ] = _NORMAL_TOOL_EXPORT_WITH_FILENAME % workflow_filename

        context._files[ 'workflows/%s/definition.xml' % wf_id
                      ] = ( _NORMAL_WORKFLOW_EXPORT
                            % { 'workflow_id' : wf_id
                              , 'title' : wf_title
                              , 'initial_state' : wf_initial_state
                              , 'workflow_filename' : workflow_filename
                              }
                          )

        context._files[ 'workflows/%s/after_close.py' % workflow_filename
                      ] = _AFTER_CLOSE_SCRIPT

        context._files[ 'workflows/%s/after_kill.py' % workflow_filename
                      ] = _AFTER_KILL_SCRIPT

        context._files[ 'workflows/%s/before_open.py' % workflow_filename
                      ] = _BEFORE_OPEN_SCRIPT

        from Products.CMFSetup.workflow import importWorkflowTool
        importWorkflowTool( context )

        return wf_tool

    def test_empty_default_purge( self ):

        WF_ID_NON = 'non_dcworkflow_%s'
        WF_TITLE_NON = 'Non-DCWorkflow #%s'

        site = self._initSite()
        wf_tool = site.portal_workflow

        for i in range( 4 ):
            nondcworkflow = DummyWorkflow( WF_TITLE_NON % i )
            nondcworkflow.title = WF_TITLE_NON % i
            wf_tool._setObject( WF_ID_NON % i, nondcworkflow )

        wf_tool._default_chain = ( WF_ID_NON % 1, )
        wf_tool._chains_by_type[ 'sometype' ] = ( WF_ID_NON % 2, )
        self.assertEqual( len( wf_tool.objectIds() ), 4 )

        context = DummyImportContext( site )
        context._files[ 'workflows.xml' ] = _EMPTY_TOOL_EXPORT

        from Products.CMFSetup.workflow import importWorkflowTool
        importWorkflowTool( context )

        self.assertEqual( len( wf_tool.objectIds() ), 0 )
        self.assertEqual( len( wf_tool._default_chain ), 0 )
        self.assertEqual( len( wf_tool._chains_by_type ), 0 )

    def test_empty_explicit_purge( self ):

        WF_ID_NON = 'non_dcworkflow_%s'
        WF_TITLE_NON = 'Non-DCWorkflow #%s'

        site = self._initSite()
        wf_tool = site.portal_workflow

        for i in range( 4 ):
            nondcworkflow = DummyWorkflow( WF_TITLE_NON % i )
            nondcworkflow.title = WF_TITLE_NON % i
            wf_tool._setObject( WF_ID_NON % i, nondcworkflow )

        wf_tool._default_chain = ( WF_ID_NON % 1, )
        wf_tool._chains_by_type[ 'sometype' ] = ( WF_ID_NON % 2, )
        self.assertEqual( len( wf_tool.objectIds() ), 4 )

        context = DummyImportContext( site, True )
        context._files[ 'workflows.xml' ] = _EMPTY_TOOL_EXPORT

        from Products.CMFSetup.workflow import importWorkflowTool
        importWorkflowTool( context )

        self.assertEqual( len( wf_tool.objectIds() ), 0 )
        self.assertEqual( len( wf_tool._default_chain ), 0 )
        self.assertEqual( len( wf_tool._chains_by_type ), 0 )

    def test_empty_skip_purge( self ):

        WF_ID_NON = 'non_dcworkflow_%s'
        WF_TITLE_NON = 'Non-DCWorkflow #%s'

        site = self._initSite()
        wf_tool = site.portal_workflow

        for i in range( 4 ):
            nondcworkflow = DummyWorkflow( WF_TITLE_NON % i )
            nondcworkflow.title = WF_TITLE_NON % i
            wf_tool._setObject( WF_ID_NON % i, nondcworkflow )

        wf_tool._default_chain = ( WF_ID_NON % 1, )
        wf_tool._chains_by_type[ 'sometype' ] = ( WF_ID_NON % 2, )
        self.assertEqual( len( wf_tool.objectIds() ), 4 )

        context = DummyImportContext( site, False )
        context._files[ 'typestool.xml' ] = _EMPTY_TOOL_EXPORT

        from Products.CMFSetup.workflow import importWorkflowTool
        importWorkflowTool( context )

        self.assertEqual( len( wf_tool.objectIds() ), 4 )
        self.assertEqual( len( wf_tool._default_chain ), 1 )
        self.assertEqual( wf_tool._default_chain[ 0 ], WF_ID_NON % 1 )
        self.assertEqual( len( wf_tool._chains_by_type ), 1 )
        self.assertEqual( wf_tool._chains_by_type[ 'sometype' ]
                        , ( WF_ID_NON % 2, )
                        )

    def test_bindings_skip_purge( self ):

        WF_ID_NON = 'non_dcworkflow_%s'
        WF_TITLE_NON = 'Non-DCWorkflow #%s'

        site = self._initSite()
        wf_tool = site.portal_workflow

        for i in range( 4 ):
            nondcworkflow = DummyWorkflow( WF_TITLE_NON % i )
            nondcworkflow.title = WF_TITLE_NON % i
            wf_tool._setObject( WF_ID_NON % i, nondcworkflow )

        wf_tool._default_chain = ( WF_ID_NON % 1, )
        wf_tool._chains_by_type[ 'sometype' ] = ( WF_ID_NON % 2, )
        self.assertEqual( len( wf_tool.objectIds() ), 4 )

        context = DummyImportContext( site, False )
        context._files[ 'workflows.xml' ] = _BINDINGS_TOOL_EXPORT

        from Products.CMFSetup.workflow import importWorkflowTool
        importWorkflowTool( context )

        self.assertEqual( len( wf_tool.objectIds() ), 4 )
        self.assertEqual( len( wf_tool._default_chain ), 2 )
        self.assertEqual( wf_tool._default_chain[ 0 ], WF_ID_NON % 0 )
        self.assertEqual( wf_tool._default_chain[ 1 ], WF_ID_NON % 1 )
        self.assertEqual( len( wf_tool._chains_by_type ), 2 )
        self.assertEqual( wf_tool._chains_by_type[ 'sometype' ]
                        , ( WF_ID_NON % 2, )
                        )
        self.assertEqual( wf_tool._chains_by_type[ 'anothertype' ]
                        , ( WF_ID_NON % 3, )
                        )

    def test_from_empty_dcworkflow_top_level( self ):

        WF_ID = 'dcworkflow_tool'
        WF_TITLE = 'DC Workflow testing tool'
        WF_INITIAL_STATE = 'closed'

        tool = self._importNormalWorkflow( WF_ID, WF_TITLE, WF_INITIAL_STATE )

        self.assertEqual( len( tool.objectIds() ), 1 )
        self.assertEqual( tool.objectIds()[ 0 ], WF_ID )

    def test_from_empty_dcworkflow_workflow_attrs( self ):

        WF_ID = 'dcworkflow_attrs'
        WF_TITLE = 'DC Workflow testing attrs'
        WF_INITIAL_STATE = 'closed'

        tool = self._importNormalWorkflow( WF_ID, WF_TITLE, WF_INITIAL_STATE )

        workflow = tool.objectValues()[ 0 ]
        self.assertEqual( workflow.meta_type, DCWorkflowDefinition.meta_type )
        self.assertEqual( workflow.title, WF_TITLE )
        self.assertEqual( workflow.state_var, 'state' )
        self.assertEqual( workflow.initial_state, WF_INITIAL_STATE )

    def test_from_empty_dcworkflow_workflow_permissions( self ):

        WF_ID = 'dcworkflow_permissions'
        WF_TITLE = 'DC Workflow testing permissions'
        WF_INITIAL_STATE = 'closed'

        tool = self._importNormalWorkflow( WF_ID, WF_TITLE, WF_INITIAL_STATE )

        workflow = tool.objectValues()[ 0 ]

        permissions = workflow.permissions
        self.assertEqual( len( permissions ), len( _WF_PERMISSIONS ) )

        for permission in permissions:
            self.failUnless( permission in _WF_PERMISSIONS )

    def test_from_empty_dcworkflow_workflow_variables( self ):

        WF_ID = 'dcworkflow_variables'
        WF_TITLE = 'DC Workflow testing variables'
        WF_INITIAL_STATE = 'closed'

        tool = self._importNormalWorkflow( WF_ID, WF_TITLE, WF_INITIAL_STATE )

        workflow = tool.objectValues()[ 0 ]

        variables = workflow.variables

        self.assertEqual( len( variables.objectItems() )
                        , len( _WF_VARIABLES ) )

        for id, variable in variables.objectItems():

            expected = _WF_VARIABLES[ variable.getId() ]
            self.failUnless( expected[ 0 ] in variable.description )
            self.assertEqual( variable.default_value, expected[ 1 ] )
            self.assertEqual( variable.getDefaultExprText(), expected[ 2 ] )
            self.assertEqual( variable.for_catalog, expected[ 3 ] )
            self.assertEqual( variable.for_status, expected[ 4 ] )
            self.assertEqual( variable.update_always, expected[ 5 ] )

            guard = variable.getInfoGuard()

            self.assertEqual( guard.permissions, expected[ 6 ] )
            self.assertEqual( guard.roles, expected[ 7 ] )
            self.assertEqual( guard.groups, expected[ 8 ] )
            self.assertEqual( guard.getExprText(), expected[ 9 ] )

    def test_from_empty_dcworkflow_workflow_states( self ):

        WF_ID = 'dcworkflow_states'
        WF_TITLE = 'DC Workflow testing states'
        WF_INITIAL_STATE = 'closed'

        tool = self._importNormalWorkflow( WF_ID, WF_TITLE, WF_INITIAL_STATE )

        workflow = tool.objectValues()[ 0 ]

        states = workflow.states

        self.assertEqual( len( states.objectItems() )
                        , len( _WF_STATES ) )

        for id, state in states.objectItems():

            expected = _WF_STATES[ state.getId() ]
            self.assertEqual( state.title, expected[ 0 ] )
            self.failUnless( expected[ 1 ] in state.description )

            self.assertEqual( len( state.transitions ), len( expected[ 2 ] ) )

            for transition_id in state.transitions:
                self.failUnless( transition_id in expected[ 2 ] )

            for permission in state.getManagedPermissions():

                p_info = state.getPermissionInfo( permission )
                p_expected = expected[ 3 ].get( permission, [] )

                self.assertEqual( bool( p_info[ 'acquired' ] )
                                , type( p_expected ) is type( [] ) )

                self.assertEqual( len( p_info[ 'roles' ] ), len( p_expected ) )

                for role in p_info[ 'roles' ]:
                    self.failIf( role not in p_expected )

            group_roles = state.group_roles or {}
            self.assertEqual( len( group_roles ), len( expected[ 4 ] ) )

            for group_id, exp_roles in expected[ 4 ]:

                self.assertEqual( len( state.getGroupInfo( group_id ) )
                                , len( exp_roles ) )

                for role in state.getGroupInfo( group_id ):
                    self.failUnless( role in exp_roles )

            self.assertEqual( len( state.getVariableValues() )
                            , len( expected[ 5 ] ) )

            for var_id, value in state.getVariableValues():

                self.assertEqual( value, expected[ 5 ][ var_id ] )

    def test_from_empty_dcworkflow_workflow_transitions( self ):

        WF_ID = 'dcworkflow_transitions'
        WF_TITLE = 'DC Workflow testing transitions'
        WF_INITIAL_STATE = 'closed'

        tool = self._importNormalWorkflow( WF_ID, WF_TITLE, WF_INITIAL_STATE )

        workflow = tool.objectValues()[ 0 ]

        transitions = workflow.transitions

        self.assertEqual( len( transitions.objectItems() )
                        , len( _WF_TRANSITIONS ) )

        for id, transition in transitions.objectItems():

            expected = _WF_TRANSITIONS[ transition.getId() ]
            self.assertEqual( transition.title, expected[ 0 ] )
            self.failUnless( expected[ 1 ] in transition.description )
            self.assertEqual( transition.new_state_id, expected[ 2 ] )
            self.assertEqual( transition.trigger_type, expected[ 3 ] )
            self.assertEqual( transition.script_name, expected[ 4 ] )
            self.assertEqual( transition.after_script_name, expected[ 5 ] )
            self.assertEqual( transition.actbox_name, expected[ 6 ] )
            self.assertEqual( transition.actbox_url, expected[ 7 ] )
            self.assertEqual( transition.actbox_category, expected[ 8 ] )

            var_exprs = transition.var_exprs

            self.assertEqual( len( var_exprs ), len( expected[ 9 ] ) )

            for var_id, expr in var_exprs.items():
                self.assertEqual( expr, expected[ 9 ][ var_id ] )

            guard = transition.getGuard()

            self.assertEqual( guard.permissions, expected[ 10 ] )
            self.assertEqual( guard.roles, expected[ 11 ] )
            self.assertEqual( guard.groups, expected[ 12 ] )
            self.assertEqual( guard.getExprText(), expected[ 13 ] )

    def test_from_empty_dcworkflow_workflow_worklists( self ):

        WF_ID = 'dcworkflow_worklists'
        WF_TITLE = 'DC Workflow testing worklists'
        WF_INITIAL_STATE = 'closed'

        tool = self._importNormalWorkflow( WF_ID, WF_TITLE, WF_INITIAL_STATE )

        workflow = tool.objectValues()[ 0 ]

        worklists = workflow.worklists

        self.assertEqual( len( worklists.objectItems() )
                        , len( _WF_WORKLISTS ) )

        for id, worklist in worklists.objectItems():

            expected = _WF_WORKLISTS[ worklist.getId() ]
            self.failUnless( expected[ 1 ] in worklist.description )

            var_matches = worklist.var_matches

            self.assertEqual( len( var_matches ), len( expected[ 2 ] ) )

            for var_id, values in var_matches.items():
                exp_values = expected[ 2 ][ var_id ]
                self.assertEqual( len( values ), len( exp_values ) )

                for value in values:
                    self.failUnless( value in exp_values, values )

            self.assertEqual( worklist.actbox_name, expected[ 3 ] )
            self.assertEqual( worklist.actbox_url, expected[ 4 ] )
            self.assertEqual( worklist.actbox_category, expected[ 5 ] )

            guard = worklist.getGuard()

            self.assertEqual( guard.permissions, expected[ 6 ] )
            self.assertEqual( guard.roles, expected[ 7 ] )
            self.assertEqual( guard.groups, expected[ 8 ] )
            self.assertEqual( guard.getExprText(), expected[ 9 ] )

    def test_from_empty_dcworkflow_workflow_scripts( self ):

        WF_ID = 'dcworkflow_scripts'
        WF_TITLE = 'DC Workflow testing scripts'
        WF_INITIAL_STATE = 'closed'

        tool = self._importNormalWorkflow( WF_ID, WF_TITLE, WF_INITIAL_STATE )

        workflow = tool.objectValues()[ 0 ]

        scripts = workflow.scripts

        self.assertEqual( len( scripts.objectItems() )
                        , len( _WF_SCRIPTS ) )

        for script_id, script in scripts.objectItems():

            expected = _WF_SCRIPTS[ script_id ]

            self.assertEqual( script.meta_type, expected[ 0 ] )
            self.assertEqual( script.manage_FTPget(), expected[ 1 ] )

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite( WorkflowToolConfiguratorTests ),
        unittest.makeSuite( Test_exportWorkflow ),
        unittest.makeSuite( Test_importWorkflow ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
