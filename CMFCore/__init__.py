##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Portal services base objects

$Id$
"""

from sys import modules

import PortalObject, PortalContent, PortalFolder
import MembershipTool, WorkflowTool, CatalogTool, DiscussionTool
import ActionsTool, UndoTool, RegistrationTool, SkinsTool
import MemberDataTool, TypesTool
import URLTool
import DirectoryView, FSImage, FSFile, FSPropertiesObject
import FSDTMLMethod, FSPythonScript, FSSTXMethod
import FSPageTemplate
import FSZSQLMethod
import ActionInformation
import CookieCrumbler
import ContentTypeRegistry
import CachingPolicyManager
import utils

from permissions import AddPortalFolders
from permissions import ManagePortal


bases = (
    PortalObject.PortalObjectBase,
    PortalFolder.PortalFolder,
    PortalContent.PortalContent,
    )

tools = (
    MembershipTool.MembershipTool,
    RegistrationTool.RegistrationTool,
    WorkflowTool.WorkflowTool,
    CatalogTool.CatalogTool,
    DiscussionTool.DiscussionTool,
    ActionsTool.ActionsTool,
    UndoTool.UndoTool,
    SkinsTool.SkinsTool,
    MemberDataTool.MemberDataTool,
    TypesTool.TypesTool,
    URLTool.URLTool,
    )

this_module = modules[ __name__ ]

z_bases = utils.initializeBasesPhase1(bases, this_module)
z_tool_bases = utils.initializeBasesPhase1(tools, this_module)

FolderConstructorForm = ( 'manage_addPortalFolderForm'
                        , PortalFolder.manage_addPortalFolderForm
                        )

cmfcore_globals=globals()

def initialize(context):

    utils.initializeBasesPhase2(z_bases, context)
    utils.initializeBasesPhase2(z_tool_bases, context)

    context.registerClass(
        DirectoryView.DirectoryViewSurrogate,
        constructors=(('manage_addDirectoryViewForm',
                       DirectoryView.manage_addDirectoryViewForm),
                      DirectoryView.manage_addDirectoryView,
                      DirectoryView.manage_listAvailableDirectories,
                      ),
        icon='images/dirview.gif'
        )

    context.registerClass(
        CookieCrumbler.CookieCrumbler,
        constructors=(CookieCrumbler.manage_addCCForm,
                      CookieCrumbler.manage_addCC),
        icon = 'images/cookie.gif'
        )

    context.registerClass(
        ContentTypeRegistry.ContentTypeRegistry,
        constructors=( ContentTypeRegistry.manage_addRegistry, ),
        icon = 'images/registry.gif'
        )

    context.registerClass(
        CachingPolicyManager.CachingPolicyManager,
        constructors=( CachingPolicyManager.manage_addCachingPolicyManager, ),
        icon = 'images/registry.gif'
        )

    context.registerClass(
        ActionInformation.ActionCategory,
        permission=ManagePortal,
        constructors=(ActionInformation.manage_addActionCategoryForm,
                      ActionInformation.manage_addActionCategory),
        icon='images/cmf_action_category.gif',
        visibility=None)

    context.registerClass(
        ActionInformation.Action,
        permission=ManagePortal,
        constructors=(ActionInformation.manage_addActionForm,
                      ActionInformation.manage_addAction),
        icon='images/cmf_action.gif',
        visibility=None)

    context.registerClass(
        TypesTool.FactoryTypeInformation,
        permission=ManagePortal,
        constructors=( TypesTool.manage_addFactoryTIForm, ),
        icon='images/typeinfo.gif',
        visibility=None)

    context.registerClass(
        TypesTool.ScriptableTypeInformation,
        permission=ManagePortal,
        constructors=( TypesTool.manage_addScriptableTIForm, ),
        icon='images/typeinfo.gif',
        visibility=None)

    utils.registerIcon(FSDTMLMethod.FSDTMLMethod,
                       'images/fsdtml.gif', globals())
    utils.registerIcon(FSPythonScript.FSPythonScript,
                       'images/fspy.gif', globals())
    utils.registerIcon(FSImage.FSImage,
                       'images/fsimage.gif', globals())
    utils.registerIcon(FSFile.FSFile,
                       'images/fsfile.gif', globals())
    utils.registerIcon(FSPageTemplate.FSPageTemplate,
                       'images/fspt.gif', globals())
    utils.registerIcon(FSPropertiesObject.FSPropertiesObject,
                       'images/fsprops.gif', globals())
    utils.registerIcon(FSZSQLMethod.FSZSQLMethod,
                       'images/fssqlmethod.gif', globals())

    utils.ToolInit( 'CMF Core Tool'
                  , tools=tools
                  , product_name='CMFCore'
                  , icon='tool.gif'
                  ).initialize( context )

    utils.ContentInit( 'CMF Core Content'
                     , content_types=( PortalFolder.PortalFolder, )
                     , permission=AddPortalFolders
                     , extra_constructors=(
                           PortalFolder.manage_addPortalFolder, )
                     , fti=PortalFolder.factory_type_information
                     ).initialize( context )

    # make registerHelp work with 2 directories
    help = context.getProductHelp()
    lastRegistered = help.lastRegistered
    context.registerHelp(directory='help', clear=1)
    context.registerHelp(directory='interfaces', clear=1)
    if help.lastRegistered != lastRegistered:
        help.lastRegistered = None
        context.registerHelp(directory='help', clear=1)
        help.lastRegistered = None
        context.registerHelp(directory='interfaces', clear=0)
    context.registerHelpTitle('CMF Core Help')

