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
'''
Programmatically creates a workflow.
$Id$
'''
__version__='$Revision$'[11:-2]

from Products.CMFCore.CMFCorePermissions import RequestReview, \
                                                ModifyPortalContent, \
                                                ReviewPortalContent
from Products.CMFCore.WorkflowTool import addWorkflowFactory
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from AccessControl.Permissions import view, access_contents_information

p_access = access_contents_information
p_modify = ModifyPortalContent
p_view = view
p_review = ReviewPortalContent
p_request = RequestReview

r_anon = 'Anonymous'
r_manager = 'Manager'
r_reviewer = 'Reviewer'
r_owner = 'Owner'
r_member = 'Member'



def setupDefaultWorkflowRev2(wf):
    '''
    Sets up a DCWorkflow with the addition of a visible state,
    the show and hide transitions, and corresponding changes.
    wf is a DCWorkflow instance.
    '''
    wf.setProperties(title='CMF default workflow [Revision 2]')

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
    sdef.setPermission(p_access, 1, (r_manager, r_owner, r_reviewer))
    sdef.setPermission(p_view, 1, (r_manager, r_owner, r_reviewer))
    sdef.setPermission(p_modify, 0, (r_manager, r_reviewer))

    sdef = wf.states['published']
    sdef.setProperties(
        title='Public',
        transitions=('reject', 'retract',))
    sdef.setPermission(p_access, 1, (r_anon, r_manager))
    sdef.setPermission(p_view, 1, (r_anon, r_manager))
    sdef.setPermission(p_modify, 0, (r_manager,))

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
                       default_expr='transition/getId|nothing',
                       for_status=1, update_always=1)

    vdef = wf.variables['actor']
    vdef.setProperties(description='The ID of the user who performed '
                       'the last transition',
                       default_expr='user/getUserName',
                       for_status=1, update_always=1)

    vdef = wf.variables['comments']
    vdef.setProperties(description='Comments about the last transition',
                       default_expr="python:state_change.kwargs.get('comment', '')",
                       for_status=1, update_always=1)

    vdef = wf.variables['review_history']
    vdef.setProperties(description='Provides access to workflow history',
                       default_expr="state_change/getHistory",
                       props={'guard_permissions':
                              p_request + ';' + p_review})

    vdef = wf.variables['time']
    vdef.setProperties(description='Time of the last transition',
                       default_expr="state_change/getDateTime",
                       for_status=1, update_always=1)

    ldef = wf.worklists['reviewer_queue']
    ldef.setProperties(description='Reviewer tasks',
                       actbox_name='Pending (%(count)d)',
                       actbox_url='%(portal_url)s/search?review_state=pending',
                       props={'var_match_review_state':'pending',
                              'guard_permissions':p_review})
    

def createDefaultWorkflowRev2(id):
    '''
    '''
    ob = DCWorkflowDefinition(id)
    setupDefaultWorkflowRev2(ob)
    return ob

addWorkflowFactory(createDefaultWorkflowRev2, id='default_workflow',
                   title='Web-configurable workflow [Revision 2]')









def setupDefaultWorkflowClassic(wf):
    '''
    Sets up a DCWorkflow as close as possible to the old DefaultWorkflow,
    with only the private, pending, and published states.
    wf is a DCWorkflow instance.
    '''
    wf.setProperties(title='CMF default workflow [Classic]')

    for s in ('private', 'pending', 'published'):
        wf.states.addState(s)
    for t in ('publish', 'reject', 'retract', 'submit'):
        wf.transitions.addTransition(t)
    for v in ('action', 'actor', 'comments', 'review_history', 'time'):
        wf.variables.addVariable(v)
    for l in ('reviewer_queue',):
        wf.worklists.addWorklist(l)
    for p in (p_access, p_modify, p_view):
        wf.addManagedPermission(p)

    wf.states.setInitialState('private')

    sdef = wf.states['private']
    sdef.setProperties(
        title='Non-visible and editable only by owner',
        transitions=('submit', 'publish',))
    sdef.setPermission(p_access, 0, (r_manager, r_owner))
    sdef.setPermission(p_view, 0, (r_manager, r_owner))
    sdef.setPermission(p_modify, 0, (r_manager, r_owner))

    sdef = wf.states['pending']
    sdef.setProperties(
        title='Waiting for reviewer',
        transitions=('publish', 'reject', 'retract',))
    sdef.setPermission(p_access, 1, (r_manager, r_owner, r_reviewer))
    sdef.setPermission(p_view, 1, (r_manager, r_owner, r_reviewer))
    sdef.setPermission(p_modify, 0, (r_manager, r_reviewer))

    sdef = wf.states['published']
    sdef.setProperties(
        title='Public',
        transitions=('reject', 'retract',))
    sdef.setPermission(p_access, 1, (r_anon, r_manager))
    sdef.setPermission(p_view, 1, (r_anon, r_manager))
    sdef.setPermission(p_modify, 0, (r_manager,))

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
        new_state_id='private',
        actbox_name='Reject',
        actbox_url='%(content_url)s/content_reject_form',
        props={'guard_permissions':p_review})

    tdef = wf.transitions['retract']
    tdef.setProperties(
        title='Member retracts submission',
        new_state_id='private',
        actbox_name='Retract',
        actbox_url='%(content_url)s/content_retract_form',
        props={'guard_permissions':p_request})

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
                       default_expr='transition/getId|nothing',
                       for_status=1, update_always=1)

    vdef = wf.variables['actor']
    vdef.setProperties(description='The ID of the user who performed '
                       'the last transition',
                       default_expr='user/getUserName',
                       for_status=1, update_always=1)

    vdef = wf.variables['comments']
    vdef.setProperties(description='Comments about the last transition',
                       default_expr="python:state_change.kwargs.get('comment', '')",
                       for_status=1, update_always=1)

    vdef = wf.variables['review_history']
    vdef.setProperties(description='Provides access to workflow history',
                       default_expr="state_change/getHistory",
                       props={'guard_permissions':
                              p_request + ';' + p_review})

    vdef = wf.variables['time']
    vdef.setProperties(description='Time of the last transition',
                       default_expr="state_change/getDateTime",
                       for_status=1, update_always=1)

    ldef = wf.worklists['reviewer_queue']
    ldef.setProperties(description='Reviewer tasks',
                       actbox_name='Pending (%(count)d)',
                       actbox_url='%(portal_url)s/search?review_state=pending',
                       props={'var_match_review_state':'pending',
                              'guard_permissions':p_review})
    


def createDefaultWorkflowClassic(id):
    '''
    '''
    ob = DCWorkflowDefinition(id)
    setupDefaultWorkflowClassic(ob)
    return ob

addWorkflowFactory(createDefaultWorkflowClassic, id='default_workflow',
                   title='Web-configurable workflow [Classic]')

