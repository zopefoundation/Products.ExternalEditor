##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################
"""Portal services base objects"""
__version__='$Revision$'[11:-2]

import PortalObject, PortalContent, PortalFolder
import MembershipTool, WorkflowTool, CatalogTool, DiscussionTool
import ActionsTool, UndoTool, RegistrationTool, SkinsTool
import MemberDataTool, TypesTool
import DirectoryView, FSImage, FSPropertiesObject
import FSDTMLMethod, FSPythonScript, FSSTXMethod
import FSZSQLMethod
import CookieCrumbler
import ContentTypeRegistry
import utils

try:
    import FSPageTemplate
except ImportError:
    HAS_PAGE_TEMPLATES = 0
else:
    HAS_PAGE_TEMPLATES = 1


ADD_FOLDERS_PERMISSION = 'Add portal folders'

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
    )


import sys
this_module = sys.modules[ __name__ ]

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

    if HAS_PAGE_TEMPLATES:
        utils.registerIcon(FSPageTemplate.FSPageTemplate,
                        'images/fspt.gif', globals())
    utils.registerIcon(FSDTMLMethod.FSDTMLMethod,
                       'images/fsdtml.gif', globals())
    utils.registerIcon(FSPythonScript.FSPythonScript,
                       'images/fspy.gif', globals())
    utils.registerIcon(FSImage.FSImage,
                       'images/fsimage.gif', globals())
    utils.registerIcon(FSPropertiesObject.FSPropertiesObject,
                       'images/fsprops.gif', globals())
    utils.registerIcon(FSZSQLMethod.FSZSQLMethod,
                       'images/fssqlmethod.gif', globals())
    utils.registerIcon(TypesTool.FactoryTypeInformation,
                       'images/typeinfo.gif', globals())
    utils.registerIcon(TypesTool.ScriptableTypeInformation,
                       'images/typeinfo.gif', globals())

    try:
        context.registerHelpTitle( 'CMF Core Help' )
        context.registerHelp(directory='interfaces')
    except: # AARGH!!
        pass

    utils.ToolInit( 'CMF Core Tool'
                  , tools=tools
                  , product_name='CMFCore'
                  , icon='tool.gif'
                  ).initialize( context )

    utils.ContentInit( 'CMF Core Content'
                     , content_types=( PortalFolder.PortalFolder, )
                     , permission=ADD_FOLDERS_PERMISSION
                     , extra_constructors=(
                           PortalFolder.manage_addPortalFolder, )
                     , fti=PortalFolder.factory_type_information
                     ).initialize( context )

