""" Class: BasePlugin

$Id$
"""
from OFS.SimpleItem import SimpleItem
from Acquisition import aq_parent, aq_inner
from AccessControl import ClassSecurityInfo
from App.class_init import default__class_init__ as InitializeClass
from Interface.Implements import flattenInterfaces

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.PluggableAuthService.permissions import ManageUsers

class BasePlugin(SimpleItem):

    """ Base class for all PluggableAuthService Plugins
    """

    security = ClassSecurityInfo()

    __implements__ = SimpleItem.__implements__

    manage_options = ( ( { 'label': 'Activate', 
                           'action': 'manage_activateInterfacesForm', }
                         ,
                       )
                     + SimpleItem.manage_options
                     )

    security.declareProtected( ManageUsers, 'manage_activateInterfacesForm' )
    manage_activateInterfacesForm = PageTemplateFile(
        'www/bpActivateInterfaces', globals(), 
        __name__='manage_activateInterfacesForm')

    security.declareProtected( ManageUsers, 'listInterfaces' )
    def listInterfaces( self ):
        """ For ZMI update of interfaces. """
        
        results = []

        for iface in flattenInterfaces( self.__implements__ ):
            results.append( iface.__name__ )

        return results

    security.declareProtected( ManageUsers, 'testImplements' )
    def testImplements( self, interface ):
        """ Can't access Interface.isImplementedBy() directly in ZPT. """
        return interface.isImplementedBy( self )

    security.declareProtected( ManageUsers, 'manage_activateInterfaces' )
    def manage_activateInterfaces( self, interfaces, RESPONSE=None ):
        """ For ZMI update of active interfaces. """

        parent = aq_parent( aq_inner( self ) )
        plugins = parent._getOb( 'plugins' )

        active_interfaces = []

        for iface_name in interfaces:
            active_interfaces.append( plugins._getInterfaceFromName( 
                                                iface_name ) )

        pt = plugins._plugin_types
        id = self.getId()

        for type in pt:
            ids = plugins.listPluginIds( type )
            if id not in ids and type in active_interfaces:
                plugins.activatePlugin( type, id ) # turn us on
            elif id in ids and type not in active_interfaces:
                plugins.deactivatePlugin( type, id ) # turn us off

        if RESPONSE is not None:
            RESPONSE.redirect('%s/manage_workspace'
                              '?manage_tabs_message='
                              'Interface+activations+updated.'
                            % self.absolute_url())

InitializeClass(BasePlugin)
