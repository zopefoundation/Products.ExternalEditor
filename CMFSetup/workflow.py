""" Classes:  WorkflowConfigurator

$Id$
"""
from xml.sax import parseString

from AccessControl import ClassSecurityInfo
from Acquisition import Implicit
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.utils import getToolByName
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition

from permissions import ManagePortal
from utils import HandlerBase
from utils import _xmldir

TRIGGER_TYPES = ( 'AUTOMATIC', 'USER', 'WORKFLOW_METHOD' )

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

    if context.shouldPurge():

        workflow_tool = getToolByName( site, 'portal_workflow' )
        for provider_id in workflow_tool.listWorkflowTool():
            workflow_tool.deleteActionProvider( provider_id )

    text = context.readDataFile( _FILENAME )

    if text is not None:

        apc = WorkflowToolConfigurator( site ).__of__( site )
        apc.parseXML( text, encoding )

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
    apc = WorkflowToolConfigurator( site ).__of__( site )
    text = apc.generateXML()

    context.writeDataFile( _FILENAME, text, 'text/xml' )

    return 'Workflows exported.'


class WorkflowToolConfigurator( Implicit ):

    """ Synthesize XML description of site's action providers.
    """
    security = ClassSecurityInfo()   
    security.setDefaultAccess( 'allow' )
    
    def __init__( self, site ):
        self._site = site

    _providers = PageTemplateFile( 'wtcExport.xml'
                                 , _xmldir
                                 , __name__='_workflows'
                                 )

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

    security.declareProtected( ManagePortal, 'generateToolXML' )
    def generateToolXML( self ):

        """ Pseudo API.
        """
        return self._toolConfig()

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
        overrides = workflow_tool._chains_by_type.items()
        overrides.sort()

        result.extend( overrides )

        return result

    #
    #   Helper methods
    #
    security.declarePrivate( '_toolConfig' )
    _toolConfig = PageTemplateFile( 'wtcToolExport.xml'
                                  , _xmldir
                                  , __name__='toolConfig'
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
        workflow_info[ 'filename' ] = ( 'workflows/%s/definition.xml'
                                      % workflow.getId())
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

        for k, v in workflow.variables.objectItems():

            guard = v.getInfoGuard()

            info = { 'id'                   : k
                   , 'description'          : v.description
                   , 'for_catalog'          : bool( v.for_catalog )
                   , 'for_status'           : bool( v.for_status )
                   , 'update_always'        : bool( v.update_always )
                   , 'default_value'        : v.default_value
                   , 'default_expr'         : v.getDefaultExprText()
                   , 'guard_permissions'    : guard.getPermissionsText()
                   , 'guard_roles'          : guard.getRolesText()
                   , 'guard_groups'         : guard.getGroupsText()
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

          'variables' -- a list of ( name, value ) tuples for the variables
            to be set when entering the state.

        o Within the state_info mappings, each 'permissions' mapping
          has the keys:

          'name' -- the name of the permission

          'roles' -- a sequence of role IDs which have the permission

          'acquired' -- whether roles are acquired for the permission
        """
        result = []

        for k, v in workflow.states.objectItems():

            info = { 'id'           : k
                   , 'title'        : v.title
                   , 'description'  : v.description
                   , 'transitions'  : v.transitions
                   , 'permissions'  : self._extractStatePermissions( v )
                   }

            result.append( info )

        return result

    security.declarePrivate( '_extractStatePermissions' )
    def _extractStatePermissions( self, state ):

        """ Return a sequence of mappings for the permssions in a state.

        o Each mapping has the keys:

          'name' -- the name of the permission

          'roles' -- a sequence of role IDs which have the permission

          'acquired' -- whether roles are acquired for the permission
        """
        result = []

        for k, v in state.permission_roles.items():

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

            - "WORKFLOW_METHOD" -> fired as the result of execting a
               WorkflowMethod

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

        for k, v in workflow.transitions.objectItems():

            guard = v.getGuard()

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
                   , 'variables'            : v.getVariableExprs()
                   , 'guard_permissions'    : guard.getPermissionsText()
                   , 'guard_roles'          : guard.getRolesText()
                   , 'guard_groups'         : guard.getGroupsText()
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

        for k, v in workflow.worklists.objectItems():

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
                   , 'guard_permissions'    : guard.getPermissionsText()
                   , 'guard_roles'          : guard.getRolesText()
                   , 'guard_groups'         : guard.getGroupsText()
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

        """
        result = []

        for k, v in workflow.scripts.objectItems():

            info = { 'id'                   : k
                   , 'meta_type'            : v.meta_type
                   , 'body'                 : v.read()
                   }

            result.append( info )

        return result


InitializeClass( WorkflowToolConfigurator )
