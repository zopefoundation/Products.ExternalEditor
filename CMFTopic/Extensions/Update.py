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

from Products.CMFCore.utils import getToolByName
from cStringIO import StringIO
import sys

def update(self):
    """\
    Calls into UpdateTopic to perform updates on CMF Topic installations.
    """
    out = StringIO()
    Updater = UpdateTopic(out)
    out.write('Updating types tool configuration 1.0 to 1.1...\n')
    Updater.update_TypesToolConfiguration_10_11(target=self)

    return out.getvalue()


class UpdateTopic:
    """\
    A suite of methods for applying updates to CMF Topic installations,
    used by external method(s) or other upgrade scenarios.
    """

    def __init__(self, stream):
        """\
        stream is expected to be some writable file object,
        like a StringIO, that output will be sent to.
        """
        self.stream = stream

    def update_TypesToolConfiguration_10_11(self, target):
        """\
        This updates the types tool configuration to reflect the name
        changes from 'topic_edit' to 'topic_edit_form' (etc), and sets
        the immediate_view to 'topic_edit_form'.
        """
        typestool = getToolByName(target, 'portal_types')
        write = self.stream.write

        for ti in typestool.listTypeInfo():
            if ti.content_meta_type != 'Portal Topic':
                continue
            acts = list(ti.getActions())
            for action in acts:
                ta = action['action']
                if ta in ('topic_edit', 'topic_criteria', 'topic_subtopics',):
                    write(" Changed '%s' in %s to '%s_form'\n" % (ta,
                                                                  ti.id,
                                                                  ta,
                                                                   )
                          )
                    ta = '%s_form' % ta
                action['action'] = ta
            ti._actions = tuple(acts)
            initial = getattr(ti, 'immediate_view', None)
            if initial == 'topic_edit':
                s="Changed the immediate view in %s to topic_edit_form" % ti.id
                write("  %s\n" % s)
                ti.immediate_view = 'topic_edit_form'
