# Copyright (c) 2001 Zope Corporation.  All Rights Reserved.

# This software is subject to the provisions of the Zope Public License,
# Version 1.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE.

from Products.CMFDefault import Portal
import Collector, CollectorIssue
import Products.CMFCore

from Products.CMFCore import utils, CMFCorePermissions
from Products.CMFCore.DirectoryView import registerDirectory
import CollectorPermissions

import sys
this_module = sys.modules[ __name__ ]

factory_type_information = (
    (Collector.factory_type_information
     + CollectorIssue.factory_type_information

     + ({'id': 'Collector Issue Transcript',
         #     'content_icon': 'event_icon.gif',
         'meta_type': 'Document',
         'description': ('A transcript of issue activity, including comments,'
                         ' state changes, and so forth.'), 
         'product': 'CMFDefault',
         'factory': None,               # So not included in 'New' add form
         'allowed_content_types': None,
         'immediate_view': 'collector_transcript_view',
         'actions': ({'id': 'view',
                      'name': 'View',
                      'action': '../',
                      'permissions': (CMFCorePermissions.View,)},
                     {'id': 'addcomment',
                      'name': 'Add Comment',
                      'action': 'collector_transcript_comment_form',
                      'permissions':
                      (CollectorPermissions.AddCollectorIssueComment,)},
                     {'id': 'edittranscript',
                      'name': 'Edit Transcript',
                      'action': 'collector_transcript_edit_form',
                      'permissions':
                      (CollectorPermissions.EditCollectorIssue,)},
                     ),
         },
        )
     )
    )

contentClasses = (Collector.Collector, CollectorIssue.CollectorIssue)
contentConstructors = (Collector.addCollector,
                       CollectorIssue.addCollectorIssue)
z_bases = utils.initializeBasesPhase1(contentClasses, this_module)
# This is used by a script (external method) that can be run
# to set up collector in an existing CMF Site instance.
collector_globals = globals()

# Make the skins available as DirectoryViews
registerDirectory('skins', globals())
registerDirectory('skins/collector', globals())

def initialize(context):
    utils.initializeBasesPhase2(z_bases, context)
    context.registerHelp(directory='help')
    context.registerHelpTitle('CMF Collector Help')

    context.registerClass(Collector.Collector,
                          constructors = (Collector.addCollector,),
                          permission = CMFCorePermissions.AddPortalContent)

    context.registerClass(CollectorIssue.CollectorIssue,
                          constructors = (CollectorIssue.addCollectorIssue,),
                          permission = CollectorPermissions.AddCollectorIssue)
