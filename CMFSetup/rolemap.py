""" CMFSetup:  Role-permission export / import

$Id$
"""

from AccessControl import ClassSecurityInfo
from AccessControl.Permission import Permission
from Acquisition import Implicit
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from permissions import ManagePortal
from utils import _xmldir

#
# Import
#
from xml.sax import parseString
from xml.sax.handler import ContentHandler

class _RolemapParser( ContentHandler ):

    def __init__( self, site, encoding='latin-1' ):

        self._site = site
        self._encoding = encoding
        self._roles = []
        self._permissions = []

    def startElement( self, name, attrs ):

        if name == 'role':
            self._roles.append( attrs[ 'name' ].encode( self._encoding )  )

        elif name == 'permission':
            p_name = attrs[ 'name' ].encode( self._encoding )
            roles = attrs[ 'roles' ].encode( self._encoding ).split()
            acquire = attrs[ 'acquire' ].encode( self._encoding ).lower()
            acquire = acquire in ( '1', 'true', 'yes' )
            info = { 'name' : p_name, 'roles' : roles, 'acquire' : acquire }
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

#
# Export
#
class RolemapConfigurator( Implicit ):

    """ Synthesize XML description of sitewide role-permission settings.
    """
    security = ClassSecurityInfo()   
    security.setDefaultAccess( 'allow' )
    
    def __init__( self, site ):
        self.site = site

    _rolemap = PageTemplateFile( 'rmeExport.xml'
                               , _xmldir
                               , __name__='_rolemap'
                               )

    security.declareProtected( ManagePortal, 'listRoles' )
    def listRoles( self ):

        """ List the valid role IDs for our site.
        """
        return self.site.valid_roles()

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

        for perm in self.site.ac_inherited_permissions( 1 ):

            name = perm[ 0 ]
            p = Permission( name, perm[ 1 ], self.site )
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

        parseString( text, _RolemapParser( self.site ) )

InitializeClass( RolemapConfigurator )

def exportRolemap(site):

    """ Export roles / permission map as an XML file
    """
    rpe = RolemapConfigurator( site ).__of__( site )
    return rpe.generateXML(), 'text/xml', 'rolemap.xml'
