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
"""
"""

ADD_CONTENT_PERMISSION = 'Add portal content'
 
import Portal
import Document, Link, NewsItem, File, Image, Favorite, SkinnedFolder

import DiscussionItem
import PropertiesTool, MembershipTool, MetadataTool
import RegistrationTool, URLTool, DublinCore, DiscussionTool
import SyndicationTool
from Products.CMFCore import utils
import Products.CMFCore
from Products.CMFCore.DirectoryView import registerDirectory
import DefaultWorkflow


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#   N.B.:  The following symbol controls whether we "inject" the
#          content types which formerly lived in CMFCore back into
#          it.  While it is initially true (to allow existing portal
#          content to load), in a future release it will be set to
#          false;  the behavior it governs will eventually be removed
#          altogether.  YOU HAVE BEEN WARNED!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
SUPPLY_DEPRECATED_PTK_BASE_ALIASES = 0

if SUPPLY_DEPRECATED_PTK_BASE_ALIASES:

    #   Get the old module names aliased into sys.modules...
    __module_aliases__ = ( ( 'Products.PTKBase.Document', Document )
                         , ( 'Products.PTKBase.File', File )
                         , ( 'Products.PTKBase.Image', Image )
                         , ( 'Products.PTKBase.Link', Link )
                         , ( 'Products.PTKBase.NewsItem', NewsItem )
                         )

    #   ...and make sure we can find them in PTKBase when we do
    #   'manage_migrate_content()'.
    Products.PTKBase.Document = Document
    Products.PTKBase.File = File
    Products.PTKBase.Image = Image
    Products.PTKBase.Link = Link
    Products.PTKBase.NewsItem = NewsItem

contentClasses = ( Document.Document
                 , File.File
                 , Image.Image
                 , Link.Link
                 , Favorite.Favorite
                 , NewsItem.NewsItem
                 , SkinnedFolder.SkinnedFolder
                 )


contentConstructors = ( Document.addDocument
                      , File.addFile
                      , Image.addImage
                      , Link.addLink
                      , Favorite.addFavorite
                      , NewsItem.addNewsItem
                      , SkinnedFolder.addSkinnedFolder
                      )

bases = ( ( Portal.CMFSite
          , DublinCore.DefaultDublinCoreImpl
          , DiscussionItem.DiscussionItem
          )
          + contentClasses
        )

tools = ( DiscussionTool.DiscussionTool
        , MembershipTool.MembershipTool
        , RegistrationTool.RegistrationTool
        , PropertiesTool.PropertiesTool
        , URLTool.URLTool
        , MetadataTool.MetadataTool
        , SyndicationTool.SyndicationTool
        )

import sys
this_module = sys.modules[ __name__ ]

z_bases = utils.initializeBasesPhase1( bases, this_module )
z_tool_bases = utils.initializeBasesPhase1( tools, this_module )

cmfdefault_globals=globals()

# Make the skins available as DirectoryViews.
registerDirectory('skins', globals())
registerDirectory('help', globals())

def initialize( context ):

    utils.initializeBasesPhase2( z_bases, context )
    utils.initializeBasesPhase2( z_tool_bases, context )
    utils.ToolInit('CMFDefault Tool', tools=tools,
                   product_name='CMFDefault', icon='tool.gif',
                   ).initialize( context )

    utils.ContentInit( 'CMFDefault Content'
                     , content_types=contentClasses
                     , permission=ADD_CONTENT_PERMISSION
                     , extra_constructors=contentConstructors
                     , fti=Portal.factory_type_information
                     ).initialize( context )

    context.registerClass(Portal.CMFSite,
                          constructors=(Portal.manage_addCMFSiteForm,
                                        Portal.manage_addCMFSite,
                                        ),
                          icon='portal.gif')
    utils.registerIcon(DefaultWorkflow.DefaultWorkflowDefinition,
                       'images/workflow.gif', globals())

    context.registerHelp()
    context.registerHelpTitle('CMF Default Help')
