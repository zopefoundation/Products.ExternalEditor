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
"""Unique id generation and handling.

$Id$
"""

from sys import modules

from Products.CMFCore import utils

import UniqueIdAnnotationTool
import UniqueIdGeneratorTool
import UniqueIdHandlerTool

tools = (
    UniqueIdAnnotationTool.UniqueIdAnnotationTool,
    UniqueIdGeneratorTool.UniqueIdGeneratorTool,
    UniqueIdHandlerTool.UniqueIdHandlerTool,
)

this_module = modules[ __name__ ]

z_tool_bases = utils.initializeBasesPhase1(tools, this_module)

my_globals=globals()

def initialize(context):

    utils.initializeBasesPhase2(z_tool_bases, context)

    utils.ToolInit( 'CMF Unique Id Tool'
                  , tools=tools
                  , product_name='CMFUid'
                  , icon='tool.gif'
                  ).initialize(context)
