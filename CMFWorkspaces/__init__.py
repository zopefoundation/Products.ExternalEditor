##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
""" CMFWorkspaces Product Initialization

$Id$
"""

import sys

from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory

import Workspace
import OrganizationTool
from permissions import AddPortalFolders


registerDirectory('skins', globals())

tools = (
    OrganizationTool.OrganizationTool,
    )


this_module = sys.modules[ __name__ ]
z_tool_bases = utils.initializeBasesPhase1(tools, this_module)


def initialize(context):

    utils.initializeBasesPhase2(z_tool_bases, context)
    context.registerBaseClass(Workspace.Workspace)

    utils.ContentInit(
        'CMF Workspace',
        content_types=(Workspace.Workspace,),
        permission=AddPortalFolders,
        extra_constructors=(Workspace.addWorkspace,),
        fti=Workspace.factory_type_information
        ).initialize(context)

    utils.ToolInit('CMFWorkspaces Tool', tools=tools,
                   product_name='CMFWorkspaces', icon='tool.gif',
                   ).initialize(context)

