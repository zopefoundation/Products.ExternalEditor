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
"""CMF staging tools product

$Id$
"""

import sys

from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore import utils

import VersionsTool, StagingTool, LockTool
import WorkflowRepository, WorkflowWithRepositoryTool

registerDirectory('skins', globals())

tools = (
    VersionsTool.VersionsTool,
    StagingTool.StagingTool,
    LockTool.LockTool,
    WorkflowWithRepositoryTool.WorkflowWithRepositoryTool,
    )

this_module = sys.modules[ __name__ ]
z_tool_bases = utils.initializeBasesPhase1( tools, this_module )

def initialize(context):
    utils.initializeBasesPhase2( z_tool_bases, context )
    utils.ToolInit('CMFStaging Tool', tools=tools,
                   product_name='CMFStaging', icon='tool.gif',
                   ).initialize(context)

    context.registerClass(
        WorkflowRepository.WorkflowRepository,
        constructors=(WorkflowRepository.manage_addWorkflowRepositoryForm,
                      WorkflowRepository.manage_addWorkflowRepository),
        icon='tool.gif',
        )

