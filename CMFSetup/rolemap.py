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
# Export
#
class RolemapExporter( Implicit ):

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

InitializeClass( RolemapExporter )

def exportRolemap(site):

    """ Export roles / permission map as an XML file
    """
    rpe = RolemapExporter( site ).__of__( site )
    return rpe.generateXML(), 'text/xml', 'rolemap.xml'
