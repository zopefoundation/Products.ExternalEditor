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
