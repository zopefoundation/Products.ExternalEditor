""" Types tool export / import

$Id$
"""
from xml.sax import parseString

from AccessControl import ClassSecurityInfo
from Acquisition import Implicit
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.TypesTool import FactoryTypeInformation
from Products.CMFCore.TypesTool import ScriptableTypeInformation
from Products.CMFCore.utils import getToolByName

from permissions import ManagePortal
from utils import HandlerBase
from utils import _xmldir

class TypeInfoConfigurator( Implicit ):

    security = ClassSecurityInfo()   
    security.setDefaultAccess('allow')

    def __init__( self, site ):

        self._site = site

    security.declareProtected( ManagePortal, 'listTypeInfo' )
    def listTypeInfo( self ):

        """ Return a list of mappings for each type info in the site.

        o These mappings are pretty much equivalent to the stock
          'factory_type_information' elements used everywhere in the
          CMF.
        """
        result = []
        typestool = getToolByName( self._site, 'portal_types' )

        ids = typestool.listContentTypes()

        for id in ids:
            mapping = self._makeTIMapping( typestool.getTypeInfo( id ) )
            result.append( mapping )

        return result


    security.declareProtected(ManagePortal, 'generateXML' )
    def generateXML(self):

        """ Pseudo API.
        """
        return self._typeinfoConfig()

    #
    #   Helper methods
    #
    security.declarePrivate( '_typeinfoConfig' )
    _typeinfoConfig = PageTemplateFile( 'ticExport.xml'
                                      , _xmldir
                                      , __name__='typeinfoConfig'
                                      )

    security.declarePrivate( '_makeTIMapping' )
    def _makeTIMapping( self, ti ):

        """ Convert a TypeInformation object into the appropriate mapping.
        """
        result = { 'id'                     : ti.getId()
                 , 'title'                  : ti.Title()
                 , 'description'            : ti.Description()
                 , 'meta_type'              : ti.Metatype()
                 , 'icon'                   : ti.getIcon() 
                 , 'immediate_view'         : ti.immediate_view
                 , 'global_allow'           : ti.global_allow
                 , 'filter_content_types'   : ti.filter_content_types
                 , 'allowed_content_types'  : ti.allowed_content_types
                 , 'allow_discussion'       : ti.allow_discussion
                 , 'aliases'                : ti.getMethodAliases()
                 }

        if isinstance( ti, FactoryTypeInformation ):

            result[ 'kind' ]        = FactoryTypeInformation.meta_type
            result[ 'product' ]     = ti.product
            result[ 'factory' ]     = ti.factory

        elif isinstance( ti, ScriptableTypeInformation ):

            result[ 'kind' ]             = ScriptableTypeInformation.meta_type
            result[ 'permission' ]       = ti.permission
            result[ 'constructor_path' ] = ti.constructor_path

        result[ 'actions' ] = [ self._makeActionMapping( x )
                                    for x in ti.listActions() ]

        return result

    security.declarePrivate( '_makeActionMapping' )
    def _makeActionMapping( self, ai ):

        """ Convert an ActionInformation object into a mapping.
        """
        return { 'id'             : ai.getId()
               , 'title'          : ai.Title()
               , 'description'    : ai.Description()
               , 'action'         : ai.getActionExpression()
               , 'condition'      : ai.getCondition()
               , 'permissions'    : ai.getPermissions()
               , 'category'       : ai.getCategory()
               , 'visible'        : bool( ai.getVisibility() )
               }

InitializeClass( TypeInfoConfigurator )
