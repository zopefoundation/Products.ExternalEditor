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
"""Topic: Canned catalog queries
$Id$
"""
__version__='$Revision$'[11:-2]

 
import Topic
import SimpleStringCriterion
import SimpleIntCriterion
import ListCriterion
import DateCriteria
import SortCriterion
import Products.CMFCore

from ZClasses import createZClassForBase
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
import TopicPermissions

bases = (Topic.Topic,)


import sys
this_module = sys.modules[ __name__ ]

for base in bases:
    createZClassForBase( base, this_module )

# This is used by a script (external method) that can be run
# to set up Topics in an existing CMF Site instance.
topic_globals=globals()

# Make the skins available as DirectoryViews
registerDirectory('skins', globals())
registerDirectory('skins/topic', globals())

def initialize( context ):
    context.registerHelpTitle('CMF Topic Help')
    context.registerHelp(directory='help')

    # CMF Initializers
    utils.ContentInit(
        'CMF Topic Objects',
        content_types = (Topic.Topic,),
        permission = TopicPermissions.AddTopics,
        extra_constructors = (Topic.addTopic,),
        fti = Topic.factory_type_information,
        ).initialize(context)
