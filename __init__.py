""" PluggableAuthService product initialization.

$Id$
"""

from utils import allTests

from AccessControl.Permissions import manage_users as ManageUsers

from Products.PluginRegistry import PluginRegistry

from PluggableAuthService import registerMultiPlugin

import PluggableAuthService

from permissions import ManageGroups

from plugins import HTTPBasicAuthHelper as HBAH
from plugins import CookieAuthHelper as CAH
from plugins import SessionAuthHelper as SAH
from plugins import DomainAuthHelper as DAH
from plugins import ScriptablePlugin
from plugins import ZODBGroupManager
from plugins import ZODBUserManager
from plugins import ZODBRoleManager
from plugins import LocalRolePlugin
from plugins import DelegatingMultiPlugin as DMP
from plugins import SearchPrincipalsPlugin as SPP
from plugins import RecursiveGroupsPlugin as RGP
from plugins import DynamicGroupsPlugin as DGP

registerMultiPlugin(HBAH.HTTPBasicAuthHelper.meta_type)
registerMultiPlugin(DAH.DomainAuthHelper.meta_type)
registerMultiPlugin(SAH.SessionAuthHelper.meta_type)
registerMultiPlugin(CAH.CookieAuthHelper.meta_type)
registerMultiPlugin(ScriptablePlugin.ScriptablePlugin.meta_type)
registerMultiPlugin(ZODBGroupManager.ZODBGroupManager.meta_type)
registerMultiPlugin(ZODBUserManager.ZODBUserManager.meta_type)
registerMultiPlugin(ZODBRoleManager.ZODBRoleManager.meta_type)
registerMultiPlugin(LocalRolePlugin.LocalRolePlugin.meta_type)
registerMultiPlugin(DMP.DelegatingMultiPlugin.meta_type)
registerMultiPlugin(SPP.SearchPrincipalsPlugin.meta_type)
registerMultiPlugin(RGP.RecursiveGroupsPlugin.meta_type)
registerMultiPlugin(DGP.DynamicGroupsPlugin.meta_type)

def initialize(context):

    context.registerClass( PluggableAuthService.PluggableAuthService
                         , permission=ManageUsers
                         , constructors=(
                            PluggableAuthService.addPluggableAuthService, )
                         , icon='www/PluggableAuthService.png'
                         )

    context.registerClass( HBAH.HTTPBasicAuthHelper
                         , permission=ManageUsers
                         , constructors=(
                            HBAH.manage_addHTTPBasicAuthHelperForm,
                            HBAH.addHTTPBasicAuthHelper, )
                         , visibility=None
                         , icon='plugins/www/HTTPBasicAuthHelper.png'
                         )

    context.registerClass( CAH.CookieAuthHelper
                         , permission=ManageUsers
                         , constructors=(
                            CAH.manage_addCookieAuthHelperForm,
                            CAH.addCookieAuthHelper, )
                         , visibility=None
                         , icon='plugins/www/CookieAuthHelper.gif'
                         )

    context.registerClass( DAH.DomainAuthHelper
                         , permission=ManageUsers
                         , constructors=(
                            DAH.manage_addDomainAuthHelperForm,
                            DAH.manage_addDomainAuthHelper, )
                         , visibility=None
                         , icon='plugins/www/DomainAuthHelper.png'
                         )

    context.registerClass( SAH.SessionAuthHelper
                         , permission=ManageUsers
                         , constructors=(
                            SAH.manage_addSessionAuthHelperForm,
                            SAH.manage_addSessionAuthHelper, )
                         , visibility=None
                         , icon='plugins/www/SessionAuthHelper.gif'
                         )

    context.registerClass( ScriptablePlugin.ScriptablePlugin
                         , permission=ManageUsers
                         , constructors=(
                            ScriptablePlugin.manage_addScriptablePluginForm,
                            ScriptablePlugin.addScriptablePlugin, )
                         , visibility=None
                         , icon='plugins/www/ScriptablePlugin.png'
                         )

    context.registerClass( ZODBGroupManager.ZODBGroupManager
                         , permission=ManageGroups
                         , constructors=(
                            ZODBGroupManager.manage_addZODBGroupManagerForm,
                            ZODBGroupManager.addZODBGroupManager, )
                         , visibility=None
                         , icon='plugins/www/ZODBGroupManager.gif'
                         )

    context.registerClass( ZODBUserManager.ZODBUserManager
                         , permission=ManageUsers
                         , constructors=(
                            ZODBUserManager.manage_addZODBUserManagerForm,
                            ZODBUserManager.addZODBUserManager, )
                         , visibility=None
                         , icon='plugins/www/ZODBUserManager.gif'
                         )

    context.registerClass( ZODBRoleManager.ZODBRoleManager
                         , permission=ManageUsers
                         , constructors=(
                            ZODBRoleManager.manage_addZODBRoleManagerForm,
                            ZODBRoleManager.addZODBRoleManager, )
                         , visibility=None
                         , icon='plugins/www/ZODBRoleManager.gif'
                         )

    context.registerClass( LocalRolePlugin.LocalRolePlugin
                         , permission=ManageUsers
                         , constructors=(
                            LocalRolePlugin.manage_addLocalRolePluginForm,
                            LocalRolePlugin.addLocalRolePlugin, )
                         , visibility=None
                         , icon='plugins/www/ZODBRoleManager.gif'
                         )

    context.registerClass( DMP.DelegatingMultiPlugin
                         , permission=ManageUsers
                         , constructors=(
                            DMP.manage_addDelegatingMultiPluginForm,
                            DMP.manage_addDelegatingMultiPlugin, )
                         , visibility=None
                         , icon='plugins/www/DelegatingMultiPlugin.png'
                         )

    context.registerClass( SPP.SearchPrincipalsPlugin
                         , permission=ManageUsers
                         , constructors=(
                            SPP.addSearchPrincipalsPluginForm,
                            SPP.addSearchPrincipalsPlugin, )
                         , visibility=None
                         , icon='plugins/www/DelegatingMultiPlugin.png'
                         )

    context.registerClass( RGP.RecursiveGroupsPlugin
                         , permission=ManageUsers
                         , constructors=(
                            RGP.manage_addRecursiveGroupsPluginForm,
                            RGP.addRecursiveGroupsPlugin, )
                         , visibility=None
                         , icon='plugins/www/RecursiveGroupsPlugin.png'
                         )

    context.registerClass( DGP.DynamicGroupsPlugin
                         , permission=ManageUsers
                         , constructors=(
                            DGP.manage_addDynamicGroupsPluginForm,
                            DGP.addDynamicGroupsPlugin, )
                         , visibility=None
                         , icon='plugins/www/DynamicGroupsPlugin.png'
                         )
