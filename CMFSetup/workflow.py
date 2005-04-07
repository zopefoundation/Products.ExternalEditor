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
""" Classes:  WorkflowConfigurator

$Id$
"""

import re
from xml.dom.minidom import parseString as domParseString

from AccessControl import ClassSecurityInfo
from Acquisition import Implicit
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.utils import getToolByName
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition

from permissions import ManagePortal
from utils import _coalesceTextNodeChildren
from utils import _extractDescriptionNode
from utils import _getNodeAttribute
from utils import _getNodeAttributeBoolean
from utils import _queryNodeAttribute
from utils import _xmldir
from utils import ConfiguratorBase
from utils import CONVERTER, DEFAULT, KEY


TRIGGER_TYPES = ( 'AUTOMATIC', 'USER' )

#
#   Configurator entry points
#
_FILENAME = 'workflows.xml'

def importWorkflowTool( context ):

    """ Import worflow tool and contained workflow definitions.

    o 'context' must implement IImportContext.

    o Register via Python:

      registry = site.portal_setup.getImportStepRegistry()
      registry.registerStep( 'importWorkflowTool'
                           , '20040602-01'
                           , Products.CMFSetup.workflow.importWorkflowTool
                           , ()
                           , 'Workflow import'
                           , 'Import worflow tool and contained workflow '
                             'definitions.'
                           )

    o Register via XML:

      <setup-step id="importWorkflowTool"
                  version="20040602-01"
                  handler="Products.CMFSetup.workflow.importWorkflowTool"
                  title="Workflow import"
      >Import worflow tool and contained workflow definitions.</setup-step>

    """
    site = context.getSite()
    encoding = context.getEncoding()
    tool = getToolByName( site, 'portal_workflow' )

    if context.shouldPurge():

        tool.setDefaultChain( '' )
        if tool._chains_by_type is not None:
            tool._chains_by_type.clear()

        for workflow_id in tool.getWorkflowIds():
            tool._delObject( workflow_id )

    text = context.readDataFile( _FILENAME )

    if text is not None:

        wftc = WorkflowToolConfigurator( site, encoding )
        tool_info = wftc.parseXML( text )

        wfdc = WorkflowDefinitionConfigurator( site )

        for info in tool_info[ 'workflows' ]:

            if info[ 'meta_type' ] == DCWorkflowDefinition.meta_type:

                filename = info[ 'filename' ]
                sep = filename.rfind( '/' )
                if sep == -1:
                    wf_text = context.readDataFile( filename )
                else:
                    wf_text = context.readDataFile( filename[sep+1:],
                                                    filename[:sep] )

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
                ) = wfdc.parseWorkflowXML( wf_text, encoding )

                workflow_id = str( workflow_id ) # No unicode!

                tool._setObject( workflow_id
                               , DCWorkflowDefinition( workflow_id ) )

                workflow = tool._getOb( workflow_id )

                _initDCWorkflow( workflow
                               , title
                               , state_variable
                               , initial_state
                               , states
                               , transitions
                               , variables
                               , worklists
                               , permissions
                               , scripts
                               , context
                               )
            else:
                pass # TODO: handle non-DCWorkflows

        for type_id, workflow_ids in tool_info[ 'bindings' ].items():

            chain = ','.join( workflow_ids )
            if type_id is None:
                tool.setDefaultChain( chain )
            else:
                tool.setChainForPortalTypes( ( type_id, ), chain )

    return 'Workflows imported.'


def exportWorkflowTool( context ):

    """ Export worflow tool and contained workflow definitions as an XML file.

    o 'context' must implement IExportContext.

    o Register via Python:

      registry = site.portal_setup.getExportStepRegistry()
      registry.registerStep( 'exportWorkflowTool'
                           , Products.CMFSetup.workflow.exportWorkflowTool
                           , 'Workflow export'
                           , 'Export worflow tool and contained workflow '
                             'definitions.'
                           )

    o Register via XML:

      <export-script id="exportWorkflowTool"
                     version="20040518-01"
                     handler="Products.CMFSetup.workflow.exportWorkflowTool"
                     title="Workflow export"
      >Export worflow tool and contained workflow definitions.</export-script>

    """
    site = context.getSite()
    wftc = WorkflowToolConfigurator( site ).__of__( site )
    wfdc = WorkflowDefinitionConfigurator( site ).__of__( site )
    wf_tool = getToolByName( site, 'portal_workflow' )
    text = wftc.generateXML()

    context.writeDataFile( _FILENAME, text, 'text/xml' )

    for wf_id in wf_tool.getWorkflowIds():

        wf_dirname = wf_id.replace( ' ', '_' )
        wf_xml = wfdc.generateWorkflowXML( wf_id )

        if wf_xml is not None:
            context.writeDataFile( 'definition.xml'
                                 , wf_xml
                                 , 'text/xml'
                                 , 'workflows/%s' % wf_dirname
                                 )

    return 'Workflows exported.'


class WorkflowToolConfigurator(ConfiguratorBase):
    """ Synthesize XML description of site's workflow tool.
    """
    security = ClassSecurityInfo()

    security.declareProtected(ManagePortal, 'getWorkflowInfo')
    def getWorkflowInfo(self, workflow_id):
        """ Return a mapping describing a given workflow.
        """
        workflow_tool = getToolByName( self._site, 'portal_workflow' )
        workflow = workflow_tool.getWorkflowById( workflow_id )

        workflow_info = { 'id'          : workflow_id
                        , 'meta_type'   : workflow.meta_type
                        , 'title'       : workflow.title_or_id()
                        }

        if workflow.meta_type == DCWorkflowDefinition.meta_type:
            workflow_info['filename'] = _getWorkflowFilename(workflow_id)

        return workflow_info

    security.declareProtected( ManagePortal, 'listWorkflowInfo' )
    def listWorkflowInfo( self ):

        """ Return a sequence of mappings for each workflow in the tool.

        o See 'getWorkflowInfo' for definition of the mappings.
        """
        workflow_tool = getToolByName( self._site, 'portal_workflow' )
        return [ self.getWorkflowInfo( workflow_id )
                    for workflow_id in workflow_tool.getWorkflowIds() ]

    security.declareProtected( ManagePortal, 'listWorkflowChains' )
    def listWorkflowChains( self ):

        """ Return a sequence of tuples binding workflows to each content type.

        o Tuples are in the format, '( type_id, [ workflow_id ] )'.

        o The default chain will be first in the list, with None for the
          'type_id'.

        o The list will only include type-specific chains for types which
          do not use the default chain.
        """
        workflow_tool = getToolByName( self._site, 'portal_workflow' )

        result = [ ( None, workflow_tool._default_chain ) ]
        if workflow_tool._chains_by_type is None:
            overrides = []
        else:
            overrides = workflow_tool._chains_by_type.items()
            overrides.sort()

        result.extend( overrides )

        return result

    def _getExportTemplate(self):

        return PageTemplateFile('wtcToolExport.xml', _xmldir)

    def _getImportMapping(self):

        return {
          'workflow-tool':
            { 'workflow':       {KEY: 'workflows', DEFAULT: (),
                                 CONVERTER: self._convertWorkflows},
              'bindings':       {CONVERTER: self._convertBindings} },
          'workflow':
            { 'workflow_id':    {},
              'meta_type':      {DEFAULT: '%(workflow_id)s'},
              'filename':       {DEFAULT: '%(workflow_id)s'} },
          'bindings':
            { 'default':        {KEY: 'bindings'},
              'type':           {KEY: 'bindings'} },
          'default':
            { 'type_id':        {DEFAULT: None},
              'bound-workflow': {KEY: 'bound_workflows', DEFAULT: ()} },
          'type':
            { 'type_id':        {DEFAULT: None},
              'bound-workflow': {KEY: 'bound_workflows', DEFAULT: ()} },
          'bound-workflow':
            { 'workflow_id':    {KEY: None} } }

    def _convertWorkflows(self, val):

        for wf in val:
            if wf['meta_type'] == DCWorkflowDefinition.meta_type:
                if wf['filename'] == wf['workflow_id']:
                    wf['filename'] = _getTypeFilename( wf['filename'] )
            else:
                wf['filename'] = None

        return val

    def _convertBindings(self, val):

        result = {}

        for binding in val[0]['bindings']:
            result[ binding['type_id'] ] = binding['bound_workflows']

        return result

InitializeClass(WorkflowToolConfigurator)


class WorkflowDefinitionConfigurator( Implicit ):
    """ Synthesize XML description of site's workflows.
    """
    security = ClassSecurityInfo()

    def __init__( self, site ):
        self._site = site

    security.declareProtected( ManagePortal, 'getWorkflowInfo' )
    def getWorkflowInfo( self, workflow_id ):

        """ Return a mapping describing a given workflow.

        o Keys in the mappings:

          'id' -- the ID of the workflow within the tool

          'meta_type' -- the workflow's meta_type

          'title' -- the workflow's title property

        o See '_extractDCWorkflowInfo' below for keys present only for
          DCWorkflow definitions.

        """
        workflow_tool = getToolByName( self._site, 'portal_workflow' )
        workflow = workflow_tool.getWorkflowById( workflow_id )

        workflow_info = { 'id'          : workflow_id
                        , 'meta_type'   : workflow.meta_type
                        , 'title'       : workflow.title_or_id()
                        }

        if workflow.meta_type == DCWorkflowDefinition.meta_type:
            self._extractDCWorkflowInfo( workflow, workflow_info )

        return workflow_info


    security.declareProtected( ManagePortal, 'generateWorkflowXML' )
    def generateWorkflowXML( self, workflow_id ):

        """ Pseudo API.
        """
        info = self.getWorkflowInfo( workflow_id )

        if info[ 'meta_type' ] != DCWorkflowDefinition.meta_type:
            return None

        return self._workflowConfig( workflow_id=workflow_id )

    security.declareProtected( ManagePortal, 'parseWorkflowXML' )
    def parseWorkflowXML( self, xml, encoding=None ):

        """ Pseudo API.
        """
        dom = domParseString( xml )

        root = dom.getElementsByTagName( 'dc-workflow' )[ 0 ]

        workflow_id = _getNodeAttribute( root, 'workflow_id', encoding )
        title = _getNodeAttribute( root, 'title', encoding )
        state_variable = _getNodeAttribute( root, 'state_variable', encoding )
        initial_state = _getNodeAttribute( root, 'initial_state', encoding )

        states = _extractStateNodes( root )
        transitions = _extractTransitionNodes( root )
        variables = _extractVariableNodes( root )
        worklists = _extractWorklistNodes( root )
        permissions = _extractPermissionNodes( root )
        scripts = _extractScriptNodes( root )

        return ( workflow_id
               , title
               , state_variable
               , initial_state
               , states
               , transitions
               , variables
               , worklists
               , permissions
               , scripts
               )

    security.declarePrivate( '_workflowConfig' )
    _workflowConfig = PageTemplateFile( 'wtcWorkflowExport.xml'
                                      , _xmldir
                                      , __name__='workflowConfig'
                                      )

    security.declarePrivate( '_extractDCWorkflowInfo' )
    def _extractDCWorkflowInfo( self, workflow, workflow_info ):

        """ Append the information for a 'workflow' into 'workflow_info'

        o 'workflow' must be a DCWorkflowDefinition instance.

        o 'workflow_info' must be a dictionary.

        o The following keys will be added to 'workflow_info':

          'permissions' -- a list of names of permissions managed
            by the workflow

          'state_variable' -- the name of the workflow's "main"
            state variable

          'initial_state' -- the name of the state in the workflow
            in which objects start their lifecycle.

          'variable_info' -- a list of mappings describing the
            variables tracked by the workflow (see '_extractVariables').

          'state_info' -- a list of mappings describing the
            states tracked by the workflow (see '_extractStates').

          'transition_info' -- a list of mappings describing the
            transitions tracked by the workflow (see '_extractTransitions').

          'worklist_info' -- a list of mappings describing the
            worklists tracked by the workflow (see '_extractWorklists').

          'script_info' -- a list of mappings describing the scripts which
            provide added business logic (wee '_extractScripts').
        """
        workflow_info[ 'filename' ] = _getWorkflowFilename( workflow.getId() )
        workflow_info[ 'state_variable' ] = workflow.state_var
        workflow_info[ 'initial_state' ] = workflow.initial_state
        workflow_info[ 'permissions' ] = workflow.permissions
        workflow_info[ 'variable_info' ] = self._extractVariables( workflow )
        workflow_info[ 'state_info' ] = self._extractStates( workflow )
        workflow_info[ 'transition_info' ] = self._extractTransitions(
                                                                   workflow )
        workflow_info[ 'worklist_info' ] = self._extractWorklists( workflow )
        workflow_info[ 'script_info' ] = self._extractScripts( workflow )

    security.declarePrivate( '_extractVariables' )
    def _extractVariables( self, workflow ):

        """ Return a sequence of mappings describing DCWorkflow variables.

        o Keys for each mapping will include:

          'id' -- the variable's ID

          'description' -- a textual description of the variable

          'for_catalog' -- whether to catalog this variable

          'for_status' -- whether to ??? this variable (XXX)

          'update_always' -- whether to update this variable whenever
            executing a transition (xxX)

          'default_value' -- a default value for the variable (XXX)

          'default_expression' -- a TALES expression for the default value

          'guard_permissions' -- a list of permissions guarding access
            to the variable

          'guard_roles' -- a list of roles guarding access
            to the variable

          'guard_groups' -- a list of groups guarding the transition

          'guard_expr' -- an expression guarding access to the variable
        """
        result = []

        items = workflow.variables.objectItems()
        items.sort()

        for k, v in items:

            guard = v.getInfoGuard()

            default_type = _guessVariableType( v.default_value )

            info = { 'id'                   : k
                   , 'description'          : v.description
                   , 'for_catalog'          : bool( v.for_catalog )
                   , 'for_status'           : bool( v.for_status )
                   , 'update_always'        : bool( v.update_always )
                   , 'default_value'        : v.default_value
                   , 'default_type'         : default_type
                   , 'default_expr'         : v.getDefaultExprText()
                   , 'guard_permissions'    : guard.permissions
                   , 'guard_roles'          : guard.roles
                   , 'guard_groups'         : guard.groups
                   , 'guard_expr'           : guard.getExprText()
                   }

            result.append( info )

        return result

    security.declarePrivate( '_extractStates' )
    def _extractStates( self, workflow ):

        """ Return a sequence of mappings describing DCWorkflow states.

        o Within the workflow mapping, each 'state_info' mapping has keys:

          'id' -- the state's ID

          'title' -- the state's title

          'description' -- the state's description

          'transitions' -- a list of IDs of transitions out of the state

          'permissions' -- a list of mappings describing the permission
            map for the state

          'groups' -- a list of ( group_id, (roles,) ) tuples describing the
            group-role assignments for the state

          'variables' -- a list of mapping for the variables
            to be set when entering the state.

        o Within the state_info mappings, each 'permissions' mapping
          has the keys:

          'name' -- the name of the permission

          'roles' -- a sequence of role IDs which have the permission

          'acquired' -- whether roles are acquired for the permission

        o Within the state_info mappings, each 'variable' mapping
          has the keys:

          'name' -- the name of the variable

          'type' -- the type of the value (allowed values are:
                    'string', 'datetime', 'bool', 'int')

          'value' -- the value to be set
        """
        result = []

        items = workflow.states.objectItems()
        items.sort()

        for k, v in items:

            groups = v.group_roles and list( v.group_roles.items() ) or []
            groups = [ x for x in groups if x[1] ]
            groups.sort()

            variables = list( v.getVariableValues() )
            variables.sort()

            v_info = []

            for v_name, value in variables:
                v_info.append( { 'name' : v_name
                               , 'type' :_guessVariableType( value )
                               , 'value' : value
                               } )

            info = { 'id'           : k
                   , 'title'        : v.title
                   , 'description'  : v.description
                   , 'transitions'  : v.transitions
                   , 'permissions'  : self._extractStatePermissions( v )
                   , 'groups'       : groups
                   , 'variables'    : v_info
                   }

            result.append( info )

        return result

    security.declarePrivate( '_extractStatePermissions' )
    def _extractStatePermissions( self, state ):

        """ Return a sequence of mappings for the permissions in a state.

        o Each mapping has the keys:

          'name' -- the name of the permission

          'roles' -- a sequence of role IDs which have the permission

          'acquired' -- whether roles are acquired for the permission
        """
        result = []

        items = state.permission_roles.items()
        items.sort()

        for k, v in items:

            result.append( { 'name' : k
                           , 'roles' : v
                           , 'acquired' : not isinstance( v, tuple )
                           } )

        return result


    security.declarePrivate( '_extractTransitions' )
    def _extractTransitions( self, workflow ):

        """ Return a sequence of mappings describing DCWorkflow transitions.

        o Each mapping has the keys:

          'id' -- the transition's ID

          'title' -- the transition's ID

          'description' -- the transition's description

          'new_state_id' -- the ID of the state into which the transition
            moves an object

          'trigger_type' -- one of the following values, indicating how the
            transition is fired:

            - "AUTOMATIC" -> fired opportunistically whenever the workflow
               notices that its guard conditions permit

            - "USER" -> fired in response to user request

          'script_name' -- the ID of a script to be executed before
             the transition

          'after_script_name' -- the ID of a script to be executed after
             the transition

          'actbox_name' -- the name of the action by which the user
             triggers the transition

          'actbox_url' -- the URL of the action by which the user
             triggers the transition

          'actbox_category' -- the category of the action by which the user
             triggers the transition

          'variables' -- a list of ( id, expr ) tuples defining how variables
            are to be set during the transition

          'guard_permissions' -- a list of permissions guarding the transition

          'guard_roles' -- a list of roles guarding the transition

          'guard_groups' -- a list of groups guarding the transition

          'guard_expr' -- an expression guarding the transition

        """
        result = []

        items = workflow.transitions.objectItems()
        items.sort()

        for k, v in items:

            guard = v.getGuard()

            v_info = []

            for v_name, expr in v.getVariableExprs():
                v_info.append( { 'name' : v_name, 'expr' : expr } )

            info = { 'id'                   : k
                   , 'title'                : v.title
                   , 'description'          : v.description
                   , 'new_state_id'         : v.new_state_id
                   , 'trigger_type'         : TRIGGER_TYPES[ v.trigger_type ]
                   , 'script_name'          : v.script_name
                   , 'after_script_name'    : v.after_script_name
                   , 'actbox_name'          : v.actbox_name
                   , 'actbox_url'           : v.actbox_url
                   , 'actbox_category'      : v.actbox_category
                   , 'variables'            : v_info
                   , 'guard_permissions'    : guard.permissions
                   , 'guard_roles'          : guard.roles
                   , 'guard_groups'         : guard.groups
                   , 'guard_expr'           : guard.getExprText()
                   }

            result.append( info )

        return result

    security.declarePrivate( '_extractWorklists' )
    def _extractWorklists( self, workflow ):

        """ Return a sequence of mappings describing DCWorkflow transitions.

        o Each mapping has the keys:

          'id' -- the ID of the worklist

          'title' -- the title of the worklist

          'description' -- a textual description of the worklist

          'var_match' -- a list of ( key, value ) tuples defining
            the variables used to "activate" the worklist.

          'actbox_name' -- the name of the "action" corresponding to the
            worklist

          'actbox_url' -- the URL of the "action" corresponding to the
            worklist

          'actbox_category' -- the category of the "action" corresponding
            to the worklist

          'guard_permissions' -- a list of permissions guarding access
            to the worklist

          'guard_roles' -- a list of roles guarding access
            to the worklist

          'guard_expr' -- an expression guarding access to the worklist

        """
        result = []

        items = workflow.worklists.objectItems()
        items.sort()

        for k, v in items:

            guard = v.getGuard()

            var_match = [ ( id, v.getVarMatchText( id ) )
                            for id in v.getVarMatchKeys() ]

            info = { 'id'                   : k
                   , 'title'                : v.title
                   , 'description'          : v.description
                   , 'var_match'            : var_match
                   , 'actbox_name'          : v.actbox_name
                   , 'actbox_url'           : v.actbox_url
                   , 'actbox_category'      : v.actbox_category
                   , 'guard_permissions'    : guard.permissions
                   , 'guard_roles'          : guard.roles
                   , 'guard_groups'         : guard.groups
                   , 'guard_expr'           : guard.getExprText()
                   }

            result.append( info )

        return result

    security.declarePrivate( '_extractScripts' )
    def _extractScripts( self, workflow ):

        """ Return a sequence of mappings describing DCWorkflow scripts.

        o Each mapping has the keys:

          'id' -- the ID of the script

          'meta_type' -- the title of the worklist

          'body' -- the text of the script

          'filename' -- the name of the file to / from which the script
            is stored / loaded
        """
        result = []

        items = workflow.scripts.objectItems()
        items.sort()

        for k, v in items:

            filename = _getScriptFilename( workflow.getId(), k, v.meta_type )

            info = { 'id'                   : k
                   , 'meta_type'            : v.meta_type
                   , 'body'                 : v.read()
                   , 'filename'             : filename
                   }

            result.append( info )

        return result

InitializeClass( WorkflowDefinitionConfigurator )


def _getWorkflowFilename( workflow_id ):

    """ Return the name of the file which holds info for a given workflow.
    """
    return 'workflows/%s/definition.xml' % workflow_id.replace( ' ', '_' )

def _getScriptFilename( workflow_id, script_id, meta_type ):

    """ Return the name of the file which holds the script.
    """
    wf_dir = workflow_id.replace( ' ', '_' )
    suffix = _METATYPE_SUFFIXES[ meta_type ]
    return 'workflows/%s/%s.%s' % ( wf_dir, script_id, suffix )

def _extractStateNodes( root, encoding=None ):

    result = []

    for s_node in root.getElementsByTagName( 'state' ):

        info = { 'state_id' : _getNodeAttribute( s_node, 'state_id', encoding )
               , 'title' : _getNodeAttribute( s_node, 'title', encoding )
               , 'description' : _extractDescriptionNode( s_node, encoding )
               }

        info[ 'transitions' ] = [ _getNodeAttribute( x, 'transition_id'
                                                   , encoding )
                                  for x in s_node.getElementsByTagName(
                                                        'exit-transition' ) ]

        info[ 'permissions' ] = permission_map = {}

        for p_map in s_node.getElementsByTagName( 'permission-map' ):

            name = _getNodeAttribute( p_map, 'name', encoding )
            acquired = _getNodeAttributeBoolean( p_map, 'acquired' )

            roles = [ _coalesceTextNodeChildren( x, encoding )
                        for x in p_map.getElementsByTagName(
                                            'permission-role' ) ]

            if not acquired:
                roles = tuple( roles )

            permission_map[ name ] = roles

        info[ 'groups' ] = group_map = []

        for g_map in s_node.getElementsByTagName( 'group-map' ):

            name = _getNodeAttribute( g_map, 'name', encoding )

            roles = [ _coalesceTextNodeChildren( x, encoding )
                        for x in g_map.getElementsByTagName(
                                            'group-role' ) ]

            group_map.append( ( name, tuple( roles ) ) )

        info[ 'variables' ] = var_map = {}

        for assignment in s_node.getElementsByTagName( 'assignment' ):

            name = _getNodeAttribute( assignment, 'name', encoding )
            type_id = _getNodeAttribute( assignment, 'type', encoding )
            value = _coalesceTextNodeChildren( assignment, encoding )

            var_map[ name ] = { 'name'  : name
                              , 'type'  : type_id
                              , 'value' : value
                              }

        result.append( info )

    return result

def _extractTransitionNodes( root, encoding=None ):

    result = []

    for t_node in root.getElementsByTagName( 'transition' ):

        info = { 'transition_id' : _getNodeAttribute( t_node, 'transition_id'
                                                    , encoding )
               , 'title' : _getNodeAttribute( t_node, 'title', encoding )
               , 'description' : _extractDescriptionNode( t_node, encoding )
               , 'new_state' : _getNodeAttribute( t_node, 'new_state'
                                                , encoding )
               , 'trigger' : _getNodeAttribute( t_node, 'trigger', encoding )
               , 'before_script' : _getNodeAttribute( t_node, 'before_script'
                                                  , encoding )
               , 'after_script' : _getNodeAttribute( t_node, 'after_script'
                                                   , encoding )
               , 'action' : _extractActionNode( t_node, encoding )
               , 'guard' : _extractGuardNode( t_node, encoding )
               }

        info[ 'variables' ] = var_map = {}

        for assignment in t_node.getElementsByTagName( 'assignment' ):

            name = _getNodeAttribute( assignment, 'name', encoding )
            expr = _coalesceTextNodeChildren( assignment, encoding )
            var_map[ name ] = expr

        result.append( info )

    return result

def _extractVariableNodes( root, encoding=None ):

    result = []

    for v_node in root.getElementsByTagName( 'variable' ):

        info = { 'variable_id' : _getNodeAttribute( v_node, 'variable_id'
                                                    , encoding )
               , 'description' : _extractDescriptionNode( v_node, encoding )
               , 'for_catalog' : _getNodeAttributeBoolean( v_node
                                                         , 'for_catalog'
                                                         )
               , 'for_status' : _getNodeAttributeBoolean( v_node
                                                        , 'for_status'
                                                        )
               , 'update_always' : _getNodeAttributeBoolean( v_node
                                                           , 'update_always'
                                                           )
               , 'default' : _extractDefaultNode( v_node, encoding )
               , 'guard' : _extractGuardNode( v_node, encoding )
               }

        result.append( info )

    return result

def _extractWorklistNodes( root, encoding=None ):

    result = []

    for w_node in root.getElementsByTagName( 'worklist' ):

        info = { 'worklist_id' : _getNodeAttribute( w_node, 'worklist_id'
                                                    , encoding )
               , 'title' : _getNodeAttribute( w_node, 'title' , encoding )
               , 'description' : _extractDescriptionNode( w_node, encoding )
               , 'match' : _extractMatchNode( w_node, encoding )
               , 'action' : _extractActionNode( w_node, encoding )
               , 'guard' : _extractGuardNode( w_node, encoding )
               }

        result.append( info )

    return result

def _extractScriptNodes( root, encoding=None ):

    result = []

    for s_node in root.getElementsByTagName( 'script' ):


        info = { 'script_id' : _getNodeAttribute( s_node, 'script_id' )
               , 'meta_type' : _getNodeAttribute( s_node, 'type' , encoding )
               }

        filename = _queryNodeAttribute( s_node, 'filename' , None, encoding )

        if filename is not None:
            info[ 'filename' ] = filename

        result.append( info )

    return result

def _extractPermissionNodes( root, encoding=None ):

    result = []

    for p_node in root.getElementsByTagName( 'permission' ):

        result.append( _coalesceTextNodeChildren( p_node, encoding ) )

    return result

def _extractActionNode( parent, encoding=None ):

    nodes = parent.getElementsByTagName( 'action' )
    assert len( nodes ) <= 1, nodes

    if len( nodes ) < 1:
        return { 'name' : '', 'url' : '', 'category' : '' }

    node = nodes[ 0 ]

    return { 'name' : _coalesceTextNodeChildren( node, encoding )
           , 'url' : _getNodeAttribute( node, 'url', encoding )
           , 'category' : _getNodeAttribute( node, 'category', encoding )
           }

def _extractGuardNode( parent, encoding=None ):

    nodes = parent.getElementsByTagName( 'guard' )
    assert len( nodes ) <= 1, nodes

    if len( nodes ) < 1:
        return { 'permissions' : (), 'roles' : (), 'groups' : (), 'expr' : '' }

    node = nodes[ 0 ]

    expr_nodes = node.getElementsByTagName( 'guard-expression' )
    assert( len( expr_nodes ) <= 1 )

    expr_text = expr_nodes and _coalesceTextNodeChildren( expr_nodes[ 0 ]
                                                        , encoding
                                                        ) or ''

    return { 'permissions' : [ _coalesceTextNodeChildren( x, encoding )
                                for x in node.getElementsByTagName(
                                                    'guard-permission' ) ]
           , 'roles' : [ _coalesceTextNodeChildren( x, encoding )
                          for x in node.getElementsByTagName( 'guard-role' ) ]
           , 'groups' : [ _coalesceTextNodeChildren( x, encoding )
                          for x in node.getElementsByTagName( 'guard-group' ) ]
           , 'expression' : expr_text
           }

def _extractDefaultNode( parent, encoding=None ):

    nodes = parent.getElementsByTagName( 'default' )
    assert len( nodes ) <= 1, nodes

    if len( nodes ) < 1:
        return { 'value' : '', 'expression' : '', 'type' : 'n/a' }

    node = nodes[ 0 ]

    value_nodes = node.getElementsByTagName( 'value' )
    assert( len( value_nodes ) <= 1 )

    value_type = 'n/a'
    if value_nodes:
        value_type = value_nodes[ 0 ].getAttribute( 'type' ) or 'n/a'

    value_text = value_nodes and _coalesceTextNodeChildren( value_nodes[ 0 ]
                                                          , encoding
                                                          ) or ''

    expr_nodes = node.getElementsByTagName( 'expression' )
    assert( len( expr_nodes ) <= 1 )

    expr_text = expr_nodes and _coalesceTextNodeChildren( expr_nodes[ 0 ]
                                                        , encoding
                                                        ) or ''

    return { 'value' : value_text
           , 'type' : value_type
           , 'expression' : expr_text
           }

_SEMICOLON_LIST_SPLITTER = re.compile( r';[ ]*' )

def _extractMatchNode( parent, encoding=None ):

    nodes = parent.getElementsByTagName( 'match' )

    result = {}

    for node in nodes:

        name = _getNodeAttribute( node, 'name', encoding )
        values = _getNodeAttribute( node, 'values', encoding )
        result[ name ] = _SEMICOLON_LIST_SPLITTER.split( values )

    return result

def _guessVariableType( value ):

    from DateTime.DateTime import DateTime

    if value is None:
        return 'none'

    if isinstance( value, DateTime ):
        return 'datetime'

    if isinstance( value, bool ):
        return 'bool'

    if isinstance( value, int ):
        return 'int'

    if isinstance( value, float ):
        return 'float'

    if isinstance( value, basestring ):
        return 'string'

    return 'unknown'

def _convertVariableValue( value, type_id ):

    from DateTime.DateTime import DateTime

    if type_id == 'none':
        return None

    if type_id == 'datetime':

        return DateTime( value )

    if type_id == 'bool':

        if isinstance( value, basestring ):

            value = str( value ).lower()

            return value in ( 'true', 'yes', '1' )

        else:
            return bool( value )

    if type_id == 'int':
        return int( value )

    if type_id == 'float':
        return float( value )

    return value

from Products.PythonScripts.PythonScript import PythonScript
from Products.ExternalMethod.ExternalMethod import ExternalMethod
from OFS.DTMLMethod import DTMLMethod

_METATYPE_SUFFIXES = \
{ PythonScript.meta_type : 'py'
, ExternalMethod.meta_type : 'em'
, DTMLMethod.meta_type : 'dtml'
}

def _initDCWorkflow( workflow
                   , title
                   , state_variable
                   , initial_state
                   , states
                   , transitions
                   , variables
                   , worklists
                   , permissions
                   , scripts
                   , context
                   ):
    """ Initialize a DC Workflow using values parsed from XML.
    """
    workflow.title = title
    workflow.state_var = state_variable
    workflow.initial_state = initial_state

    permissions = permissions[:]
    permissions.sort()
    workflow.permissions = permissions

    _initDCWorkflowVariables( workflow, variables )
    _initDCWorkflowStates( workflow, states )
    _initDCWorkflowTransitions( workflow, transitions )
    _initDCWorkflowWorklists( workflow, worklists )
    _initDCWorkflowScripts( workflow, scripts, context )


def _initDCWorkflowVariables( workflow, variables ):

    """ Initialize DCWorkflow variables
    """
    from Products.DCWorkflow.Variables import VariableDefinition

    for v_info in variables:

        id = str( v_info[ 'variable_id' ] ) # no unicode!
        v = VariableDefinition( id )
        workflow.variables._setObject( id, v )
        v = workflow.variables._getOb( id )

        guard = v_info[ 'guard' ]
        props = { 'guard_roles' : ';'.join( guard[ 'roles' ] )
                , 'guard_permissions' : ';'.join( guard[ 'permissions' ] )
                , 'guard_groups' : ';'.join( guard[ 'groups' ] )
                , 'guard_expr' : guard[ 'expression' ]
                }

        default = v_info[ 'default' ]
        default_value = _convertVariableValue( default[ 'value' ]
                                             , default[ 'type' ] )

        v.setProperties( description = v_info[ 'description' ]
                       , default_value = default_value
                       , default_expr = default[ 'expression' ]
                       , for_catalog = v_info[ 'for_catalog' ]
                       , for_status = v_info[ 'for_status' ]
                       , update_always = v_info[ 'update_always' ]
                       , props = props
                       )


def _initDCWorkflowStates( workflow, states ):

    """ Initialize DCWorkflow states
    """
    from Globals import PersistentMapping
    from Products.DCWorkflow.States import StateDefinition

    for s_info in states:

        id = str( s_info[ 'state_id' ] ) # no unicode!
        s = StateDefinition( id )
        workflow.states._setObject( id, s )
        s = workflow.states._getOb( id )

        s.setProperties( title = s_info[ 'title' ]
                       , description = s_info[ 'description' ]
                       , transitions = s_info[ 'transitions' ]
                       )

        for k, v in s_info[ 'permissions' ].items():
            s.setPermission( k, isinstance(v, list), v )

        gmap = s.group_roles = PersistentMapping()

        for group_id, roles in s_info[ 'groups' ]:
            gmap[ group_id ] = roles

        vmap = s.var_values = PersistentMapping()

        for name, v_info in s_info[ 'variables' ].items():

            value = _convertVariableValue( v_info[ 'value' ]
                                         , v_info[ 'type' ] )

            vmap[ name ] = value


def _initDCWorkflowTransitions( workflow, transitions ):

    """ Initialize DCWorkflow transitions
    """
    from Globals import PersistentMapping
    from Products.DCWorkflow.Transitions import TransitionDefinition

    for t_info in transitions:

        id = str( t_info[ 'transition_id' ] ) # no unicode!
        t = TransitionDefinition( id )
        workflow.transitions._setObject( id, t )
        t = workflow.transitions._getOb( id )

        trigger_type = list( TRIGGER_TYPES ).index( t_info[ 'trigger' ] )

        action = t_info[ 'action' ]

        guard = t_info[ 'guard' ]
        props = { 'guard_roles' : ';'.join( guard[ 'roles' ] )
                , 'guard_permissions' : ';'.join( guard[ 'permissions' ] )
                , 'guard_groups' : ';'.join( guard[ 'groups' ] )
                , 'guard_expr' : guard[ 'expression' ]
                }

        t.setProperties( title = t_info[ 'title' ]
                       , description = t_info[ 'description' ]
                       , new_state_id = t_info[ 'new_state' ]
                       , trigger_type = trigger_type
                       , script_name = t_info[ 'before_script' ]
                       , after_script_name = t_info[ 'after_script' ]
                       , actbox_name = action[ 'name' ]
                       , actbox_url = action[ 'url' ]
                       , actbox_category = action[ 'category' ]
                       , props = props
                       )

        t.var_exprs = PersistentMapping( t_info[ 'variables' ].items() )

def _initDCWorkflowWorklists( workflow, worklists ):

    """ Initialize DCWorkflow worklists
    """
    from Globals import PersistentMapping
    from Products.DCWorkflow.Worklists import WorklistDefinition

    for w_info in worklists:

        id = str( w_info[ 'worklist_id' ] ) # no unicode!
        w = WorklistDefinition( id )
        workflow.worklists._setObject( id, w )

        w = workflow.worklists._getOb( id )

        action = w_info[ 'action' ]

        guard = w_info[ 'guard' ]
        props = { 'guard_roles' : ';'.join( guard[ 'roles' ] )
                , 'guard_permissions' : ';'.join( guard[ 'permissions' ] )
                , 'guard_groups' : ';'.join( guard[ 'groups' ] )
                , 'guard_expr' : guard[ 'expression' ]
                }

        w.setProperties( description = w_info[ 'description' ]
                       , actbox_name = action[ 'name' ]
                       , actbox_url = action[ 'url' ]
                       , actbox_category = action[ 'category' ]
                       , props = props
                       )

        w.var_matches = PersistentMapping()
        for k, v in w_info[ 'match' ].items():
            w.var_matches[ str( k ) ] = tuple( [ str(x) for x in v ] )

def _initDCWorkflowScripts( workflow, scripts, context ):

    """ Initialize DCWorkflow scripts
    """
    for s_info in scripts:

        id = str( s_info[ 'script_id' ] ) # no unicode!
        meta_type = s_info[ 'meta_type' ]
        filename = s_info[ 'filename' ]

        file = context.readDataFile( filename )

        if meta_type == PythonScript.meta_type:
            script = PythonScript( id )
            script.write( file )

        #elif meta_type == ExternalMethod.meta_type:
        #    script = ExternalMethod( id, title, module, function )

        elif meta_type == DTMLMethod.meta_type:
            script = DTMLMethod( file, __name__=id )

        workflow.scripts._setObject( id, script )
