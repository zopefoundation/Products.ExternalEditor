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
""" CMFSetup:  Role-permission export / import

$Id$
"""

from xml.dom.minidom import parseString as domParseString

from AccessControl import ClassSecurityInfo
from AccessControl.Permission import Permission
from Acquisition import Implicit
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from permissions import ManagePortal
from utils import _getNodeAttribute
from utils import _getNodeAttributeBoolean
from utils import _xmldir

#
#   Configurator entry points
#
_FILENAME = 'rolemap.xml'

def importRolemap( context ):

    """ Import roles / permission map from an XML file.

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
    encoding = context.getEncoding()

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
        roles, permissions = rc.parseXML(text, encoding)

        immediate_roles = list( getattr( site, '__ac_roles__', [] ) )[:]
        already = {}

        for role in site.valid_roles():
            already[ role ] = 1

        for role in roles:

            if already.get( role ) is None:
                immediate_roles.append( role )
                already[ role ] = 1

        immediate_roles.sort()
        site.__ac_roles__ = tuple( immediate_roles )

        for permission in permissions:

            site.manage_permission( permission[ 'name' ]
                                  , permission[ 'roles' ]
                                  , permission[ 'acquire' ]
                                  )

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
    def parseXML( self, xml, encoding=None ):

        """ Pseudo API.
        """
        dom = domParseString(xml)

        return _extractRolemapNode(dom, encoding)

InitializeClass( RolemapConfigurator )


def _extractRolemapNode(parent, encoding=None):

    rm_node = parent.getElementsByTagName('rolemap')[0]

    r_node = rm_node.getElementsByTagName('roles')[0]
    roles = _extractRoleNodes(r_node, encoding)

    p_node = rm_node.getElementsByTagName('permissions')[0]
    permissions = _extractPermissionNodes(p_node, encoding)

    return roles, permissions

def _extractPermissionNodes(parent, encoding=None):

    result = []

    for p_node in parent.getElementsByTagName('permission'):
        name    = _getNodeAttribute(p_node, 'name', encoding)
        roles   = _extractRoleNodes(p_node, encoding)
        acquire = _getNodeAttributeBoolean(p_node, 'acquire')
        result.append( { 'name': name,
                         'roles': roles,
                         'acquire': acquire } )

    return tuple(result)

def _extractRoleNodes(parent, encoding=None):

    result = []

    for r_node in parent.getElementsByTagName('role'):
        value = _getNodeAttribute(r_node, 'name', encoding)
        result.append(value)

    return tuple(result)
