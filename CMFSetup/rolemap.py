""" CMFSetup:  Role-permission export / import

$Id$
"""
from xml.sax import parseString

from AccessControl import ClassSecurityInfo
from AccessControl.Permission import Permission
from Acquisition import Implicit
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from permissions import ManagePortal
from utils import HandlerBase
from utils import _xmldir

class _RolemapParser( HandlerBase ):

    def __init__( self, site, encoding='latin-1' ):

        self._site = site
        self._encoding = encoding
        self._roles = []
        self._permissions = []

    def startElement( self, name, attrs ):

        if name == 'role':
            self._roles.append( self._extract( attrs, 'name' )  )

        elif name == 'permission':

            acquire = self._extract( attrs, 'acquire' ).lower()
            acquire = acquire in ( '1', 'true', 'yes' )

            info = { 'name'     : self._extract( attrs, 'name' )
                   , 'roles'    : self._extract( attrs, 'roles' ).split()
                   , 'acquire'  : acquire
                   }

            self._permissions.append( info )

        elif name not in ( 'rolemap', 'permissions', 'roles' ):
            raise ValueError, 'Unknown element: %s' % name

    def endDocument( self ):

        immediate_roles = list( getattr( self._site, '__ac_roles__', [] ) )[:]
        already = {}
        for role in self._site.valid_roles():
            already[ role ] = 1

        for role in self._roles:

            if already.get( role ) is None:
                immediate_roles.append( role )
                already[ role ] = 1

        immediate_roles.sort()
        self._site.__ac_roles__ = tuple( immediate_roles )

        for permission in self._permissions:

            self._site.manage_permission( permission[ 'name' ]
                                        , permission[ 'roles' ]
                                        , permission[ 'acquire' ]
                                        )

class RolemapConfigurator( Implicit ):

    """ Synthesize XML description of sitewide role-permission settings.
    """
    security = ClassSecurityInfo()   
    security.setDefaultAccess( 'allow' )
    
    def __init__( self, site ):
        self._site = site

    _rolemap = PageTemplateFile( 'rmeExport.xml'
                               , _xmldir
                               , __name__='_rolemap'
                               )

    security.declareProtected( ManagePortal, 'listRoles' )
    def listRoles( self ):

        """ List the valid role IDs for our site.
        """
        return self._site.valid_roles()

    security.declareProtected( ManagePortal, 'listPermissions' )
    def listPermissions( self ):

        """ List permissions for export.

        o Returns a sqeuence of mappings describing locally-modified
          permission / role settings.  Keys include:
          
          'permission' -- the name of the permission
          
          'acquire' -- a flag indicating whether to acquire roles from the
              site's container
              
          'roles' -- the list of roles which have the permission.

        o Do not include permissions which both acquire and which define
          no local changes to the acquired policy.
        """
        permissions = []
        valid_roles = self.listRoles()

        for perm in self._site.ac_inherited_permissions( 1 ):

            name = perm[ 0 ]
            p = Permission( name, perm[ 1 ], self._site )
            roles = p.getRoles( default=[] )
            acquire = isinstance( roles, list )  # tuple means don't acquire
            roles = [ r for r in roles if r in valid_roles ]

            if roles or not acquire:
                permissions.append( { 'name'    : name
                                    , 'acquire' : acquire
                                    , 'roles'   : roles
                                    } )

        return permissions

    security.declareProtected( ManagePortal, 'generateXML' )
    def generateXML( self ):

        """ Pseudo API.
        """
        return self._rolemap()

    security.declareProtected( ManagePortal, 'parseXML' )
    def parseXML( self, text ):

        """ Pseudo API.
        """
        reader = getattr( text, 'read', None )

        if reader is not None:
            text = reader()

        parseString( text, _RolemapParser( self._site ) )

InitializeClass( RolemapConfigurator )


#
#   Configurator entry points
#
_FILENAME = 'rolemap.xml'

def importRolemap( context ):

    """ Export roles / permission map as an XML file

    o 'context' must implement IImportContext.

    o Register via Python:

      registry = site.portal_setup.setup_steps
      registry.registerStep( 'importRolemap'
                           , '20040518-01'
                           , Products.CMFSetup.rolemap.importRolemap
                           , ()
                           , 'Role / Permission import'
                           , 'Import additional roles, and map '
                           'roles to permissions'
                           )

    o Register via XML:
 
      <setup-step id="importRolemap"
                  version="20040518-01"
                  handler="Products.CMFSetup.rolemap.importRolemap"
                  title="Role / Permission import"
      >Import additional roles, and map roles to permissions.</setup-step>

    """
    site = context.getSite()

    if context.shouldPurge():

        items = site.__dict__.items()

        for k, v in items: # XXX: WAAA

            if k == '__ac_roles__':
                delattr( site, k )

            if k.startswith( '_' ) and k.endswith( '_Permission' ):
                delattr( site, k )

    text = context.readDataFile( _FILENAME )

    if text is not None:

        rc = RolemapConfigurator( site ).__of__( site )
        rc.parseXML( text )

    return 'Role / permission map imported.'


def exportRolemap( context ):

    """ Export roles / permission map as an XML file

    o 'context' must implement IExportContext.

    o Register via Python:

      registry = site.portal_setup.export_steps
      registry.registerStep( 'exportRolemap'
                           , Products.CMFSetup.rolemap.exportRolemap
                           , 'Role / Permission export'
                           , 'Export additional roles, and '
                             'role / permission map '
                           )

    o Register via XML:
 
      <export-script id="exportRolemap"
                     version="20040518-01"
                     handler="Products.CMFSetup.rolemap.exportRolemap"
                     title="Role / Permission export"
      >Export additional roles, and role / permission map.</export-script>

    """
    site = context.getSite()
    rc = RolemapConfigurator( site ).__of__( site )
    text = rc.generateXML()

    context.writeDataFile( _FILENAME, text, 'text/xml' )

    return 'Role / permission map exported.'
