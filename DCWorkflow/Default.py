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
'''
Programmatically creates a workflow.
$Id$
'''
__version__='$Revision$'[11:-2]

from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition

p_access = 'Access contents information'
p_modify = 'Modify portal content'
p_view = 'View'
p_review = 'Review portal content'
p_request = 'Request review'

r_anon = 'Anonymous'
r_manager = 'Manager'
r_reviewer = 'Reviewer'
r_owner = 'Owner'
r_member = 'Member'


def setupDefaultWorkflow(wf):
    '''
    wf is a DCWorkflow instance.
    '''
    wf.setProperties(title='CMF default workflow rev 2')

    for s in ('private', 'visible', 'pending', 'published'):
        wf.states.addState(s)
    for t in ('publish', 'reject', 'retract', 'submit', 'hide', 'show'):
        wf.transitions.addTransition(t)
    for v in ('action', 'actor', 'comments', 'review_history', 'time'):
        wf.variables.addVariable(v)
    for l in ('reviewer_queue',):
        wf.worklists.addWorklist(l)
    for p in (p_access, p_modify, p_view):
        wf.addManagedPermission(p)

    wf.states.setInitialState('visible')

    sdef = wf.states['private']
    sdef.setProperties(
        title='Visible and editable only by owner',
        transitions=('show',))
    sdef.setPermission(p_access, 0, (r_manager, r_owner))
    sdef.setPermission(p_view, 0, (r_manager, r_owner))
    sdef.setPermission(p_modify, 0, (r_manager, r_owner))

    sdef = wf.states['pending']
    sdef.setProperties(
        title='Waiting for reviewer',
        transitions=('hide', 'publish', 'reject', 'retract',))
    sdef.setPermission(p_access, 1, (r_anon, r_manager, r_reviewer))
    sdef.setPermission(p_view, 1, (r_anon, r_manager, r_reviewer))
    sdef.setPermission(p_modify, 0, (r_manager, r_reviewer))

    sdef = wf.states['published']
    sdef.setProperties(
        title='Public',
        transitions=('reject', 'retract',))
    sdef.setPermission(p_access, 1, (r_anon, r_manager))
    sdef.setPermission(p_view, 1, (r_anon, r_manager))
    sdef.setPermission(p_modify, 0, (r_manager))

    sdef = wf.states['visible']
    sdef.setProperties(
        title='Visible but not published',
        transitions=('hide', 'publish', 'submit',))
    sdef.setPermission(p_access, 1, (r_anon, r_manager, r_reviewer))
    sdef.setPermission(p_view, 1, (r_anon, r_manager, r_reviewer))
    sdef.setPermission(p_modify, 0, (r_manager, r_owner))

    tdef = wf.transitions['hide']
    tdef.setProperties(
        title='Member makes content private',
        new_state_id='private',
        actbox_name='Make private',
        actbox_url='%(content_url)s/content_hide_form',
        props={'guard_roles':r_owner})

    tdef = wf.transitions['publish']
    tdef.setProperties(
        title='Reviewer publishes content',
        new_state_id='published',
        actbox_name='Publish',
        actbox_url='%(content_url)s/content_publish_form',
        props={'guard_permissions':p_review})

    tdef = wf.transitions['reject']
    tdef.setProperties(
        title='Reviewer rejects submission',
        new_state_id='visible',
        actbox_name='Reject',
        actbox_url='%(content_url)s/content_reject_form',
        props={'guard_permissions':p_review})

    tdef = wf.transitions['retract']
    tdef.setProperties(
        title='Member retracts submission',
        new_state_id='visible',
        actbox_name='Retract',
        actbox_url='%(content_url)s/content_retract_form',
        props={'guard_permissions':p_request})

    tdef = wf.transitions['show']
    tdef.setProperties(
        title='Member makes content visible',
        new_state_id='visible',
        actbox_name='Make visible',
        actbox_url='%(content_url)s/content_show_form',
        props={'guard_roles':r_owner})

    tdef = wf.transitions['submit']
    tdef.setProperties(
        title='Member requests publishing',
        new_state_id='pending',
        actbox_name='Submit',
        actbox_url='%(content_url)s/content_submit_form',
        props={'guard_permissions':p_request})

    wf.variables.setStateVar('review_state')

    vdef = wf.variables['action']
    vdef.setProperties(description='The last transition',
                       default_expr='transition',
                       for_status=1)

    vdef = wf.variables['actor']
    vdef.setProperties(description='The ID of the user who performed '
                       'the last transition',
                       default_expr='_.SecurityGetUser().getUserName()',
                       for_status=1)

    vdef = wf.variables['comments']
    vdef.setProperties(description='Comments about the last transition',
                       default_expr="kwargs.get('comment', '')",
                       for_status=1)

    vdef = wf.variables['review_history']
    vdef.setProperties(description='Provides access to workflow history',
                       default_expr="getHistory()",
                       props={'guard_permissions':
                              p_request + ';' + p_review})

    vdef = wf.variables['time']
    vdef.setProperties(description='Time of the last transition',
                       default_expr="_.DateTime()",
                       for_status=1)

    ldef = wf.worklists['reviewer_queue']
    ldef.setProperties(description='Reviewer tasks',
                       actbox_name='Pending (%(count)d)',
                       actbox_url='%(portal_url)s/search?review_state=pending',
                       props={'var_match_review_state':'pending',
                              'guard_permissions':p_review})
    

def manage_addDefaultWorkflow(self):
    '''
    '''
    ob = DCWorkflowDefinition('default_workflow_rev2')
    self._setObject(ob.id, ob)
    setupDefaultWorkflow(self.this()._getOb(ob.id))
    return self.manage_main(self, self.REQUEST)
