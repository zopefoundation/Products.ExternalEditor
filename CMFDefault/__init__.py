##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
##############################################################################
"""
"""

ADD_CONTENT_PERMISSION = 'Add portal content'
 
import Portal
import Document, Link, NewsItem, File, Image, Favorite, SkinnedFolder
import Discussions, DiscussionItem
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
                         , ( 'Products.PTKBase.Discussions', Discussions )
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
                        )

bases = ( ( Portal.CMFSite
          , Discussions.Discussable
          , Discussions.DiscussionResponse
          , DublinCore.DefaultDublinCoreImpl
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

# Make the skins available as DirectoryViews.
registerDirectory('skins', globals())

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

    reg = Products.CMFCore.PortalFolder.addPortalTypeHandler
    reg( 'text/html', Document.Document )
    reg( 'text/plain', Document.Document )
    reg( 'image/png', Image.Image )
    reg( 'image/gif', Image.Image )
    reg( 'image/jpeg', Image.Image )
    reg( 'image/unknown', Image.Image )

    context.registerHelp()
    context.registerHelpTitle('CMF Default Help')
