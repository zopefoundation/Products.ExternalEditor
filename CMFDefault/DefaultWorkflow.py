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
A simple submit/review/publish workflow.
$Id$
'''
__version__='$Revision$'[11:-2]

import sys
import Globals
from Acquisition import aq_base, aq_inner, aq_parent
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.CMFCore.utils import modifyPermissionMappings, _checkPermission
from Products.CMFCore.utils import getToolByName, SimpleItemWithProperties
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.WorkflowTool import addWorkflowClass


class DefaultWorkflowDefinition (SimpleItemWithProperties):
    meta_type = 'Workflow'
    id = 'default_workflow'
    title = 'Simple Review / Publish Policy'
    _isAWorkflow = 1

    security = ClassSecurityInfo()

    def __init__(self, id):
        self.id = id

    security.declarePrivate('getReviewStateOf')
    def getReviewStateOf(self, ob):
        tool = aq_parent(aq_inner(self))
        status = tool.getStatusOf(self.getId(), ob)
        if status is not None:
            review_state = status['review_state']
        else:
            if hasattr(aq_base(ob), 'review_state'):
                # Backward compatibility.
                review_state = ob.review_state
            else:
                review_state = 'private'
        return review_state

    security.declarePrivate('getCatalogVariablesFor')
    def getCatalogVariablesFor(self, ob):
        '''
        Allows this workflow to make workflow-specific variables
        available to the catalog, making it possible to implement
        queues in a simple way.
        Returns a mapping containing the catalog variables
        that apply to ob.
        '''
        return {'review_state': self.getReviewStateOf(ob)}

    security.declarePrivate('listObjectActions')
    def listObjectActions(self, info):
        '''
        Allows this workflow to
        include actions to be displayed in the actions box.
        Called only when this workflow is applicable to
        info.content.
        Returns the actions to be displayed to the user.
        '''
        if info.isAnonymous:
            return None

        # The following operation is quite expensive.
        # We don't need to perform it if the user
        # doesn't have the required permission.
        content = info.content
        content_url = info.content_url
        content_creator = content.Creator()
        pm = getToolByName(self, 'portal_membership')
        current_user = pm.getAuthenticatedMember().getUserName()
        review_state = self.getReviewStateOf(content)
        actions = []

        allow_review = _checkPermission('Review portal content', content)
        allow_request = _checkPermission('Request review', content)

        append_action = (lambda name, p, url=content_url, a=actions.append:
                         a({'name': name,
                            'url': url + '/' + p,
                            'permissions': (),
                            'category': 'workflow'}))

        show_reject = 0
        show_retract = 0

        if review_state == 'private':
            if allow_review:
                append_action('Publish', 'content_publish_form')
            elif allow_request:
                append_action('Submit', 'content_submit_form')

        elif review_state == 'pending':
            if content_creator == current_user and allow_request:
                show_retract = 1
            if allow_review:
                append_action('Publish', 'content_publish_form')
                show_reject = 1

        elif review_state == 'published':
            if content_creator == current_user and allow_request:
                show_retract = 1
            if allow_review:
                show_reject = 1

        if show_retract:
            append_action('Retract', 'content_retract_form')
        if show_reject:
            append_action('Reject', 'content_reject_form')
        if allow_review or allow_request:
            append_action('Status history', 'content_status_history')

        return actions

    security.declarePrivate('listGlobalActions')
    def listGlobalActions(self, info):
        '''
        Allows this workflow to include actions to be displayed
        in the actions box.  Called on every request.
        
        Returns the actions to be displayed to the user.
        '''
        if info.isAnonymous:
            return None

        actions = []
        catalog = getToolByName(self, 'portal_catalog', None)
        if catalog is not None:
            pending = len(catalog.searchResults(
                review_state='pending'))
            if pending > 0:
                actions.append(
                    {'name': 'Pending review (%d)' % pending,
                     'url': info.portal_url +
                     '/search?review_state=pending',
                     'permissions': (),
                     'category': 'global'}
                    )
        return actions

    security.declarePrivate('isActionSupported')
    def isActionSupported(self, ob, action):
        '''
        Returns a true value if the given action name is supported.
        '''
        return (action in ('submit', 'retract', 'publish', 'reject',))

    security.declarePrivate('doActionFor')
    def doActionFor(self, ob, action, comment=''):
        '''
        Allows the user to request a workflow action.  This method
        must perform its own security checks.
        '''
        allow_review = _checkPermission('Review portal content', ob)
        allow_request = _checkPermission('Request review', ob)
        review_state = self.getReviewStateOf(ob)
        tool = aq_parent(aq_inner(self))

        if action == 'submit':
            if not allow_request:
                raise 'Unauthorized', 'Not authorized'
            elif review_state != 'private':
                raise 'Unauthorized', 'Already in submit state'
            self.setReviewStateOf(ob, 'pending', action, comment)

        elif action == 'retract':
            if not allow_request:
                raise 'Unauthorized', 'Not authorized'
            elif review_state == 'private':
                raise 'Unauthorized', 'Already private'
            content_creator = ob.Creator()
            pm = getToolByName(self, 'portal_membership')
            current_user = pm.getAuthenticatedMember().getUserName()
            if (content_creator != current_user) and not allow_review:
                raise 'Unauthorized', 'Not creator or reviewer'
            self.setReviewStateOf(ob, 'private', action, comment)

        elif action == 'publish':
            if not allow_review:
                raise 'Unauthorized', 'Not authorized'
            self.setReviewStateOf(ob, 'published', action, comment)

        elif action == 'reject':
            if not allow_review:
                raise 'Unauthorized', 'Not authorized'
            self.setReviewStateOf(ob, 'private', action, comment)

    security.declarePrivate('isInfoSupported')
    def isInfoSupported(self, ob, name):
        '''
        Returns a true value if the given info name is supported.
        '''
        return (name in ('review_state', 'review_history'))

    security.declarePrivate('getInfoFor')
    def getInfoFor(self, ob, name, default):
        '''
        Allows the user to request information provided by the
        workflow.  This method must perform its own security checks.
        '''
        # Treat this as public.
        if name == 'review_state':
            return self.getReviewStateOf(ob)

        allow_review = _checkPermission('Review portal content', ob)
        allow_request = _checkPermission('Request review', ob)
        if not allow_review and not allow_request:
            return default

        elif name == 'review_history':
            tool = aq_parent(aq_inner(self))
            history = tool.getHistoryOf(self.getId(), ob)
            # Make copies for security.
            return tuple(map(lambda dict: dict.copy(), history))

    security.declarePrivate('setReviewStateOf')
    def setReviewStateOf(self, ob, review_state, action, comment):
        tool = aq_parent(aq_inner(self))
        pm = getToolByName(self, 'portal_membership')
        current_user = pm.getAuthenticatedMember().getUserName()
        status = {
            'actor': current_user,
            'action': action,
            'review_state': review_state,
            'time': DateTime(),
            'comments': comment,
            }
        tool.setStatusOf(self.getId(), ob, status)
        self.updateRoleMappingsFor(ob)

    security.declarePrivate('notifyCreated')
    def notifyCreated(self, ob):
        '''
        Notifies this workflow after an object has been created
        and put in its new place.
        '''
        self.setReviewStateOf( ob, 'private', 'joined', '' )
        self.notifySuccess(ob, 'joined', '')

    security.declarePrivate('notifyBefore')
    def notifyBefore(self, ob, action):
        '''
        Notifies this workflow of an action before it happens,
        allowing veto by exception.  Unless an exception is thrown, either
        a notifySuccess() or notifyException() can be expected later on.
        The action usually corresponds to a method name.
        '''
        pass

    security.declarePrivate('notifySuccess')
    def notifySuccess(self, ob, action, result):
        '''
        Notifies this workflow that an action has taken place.
        '''
        pass

    security.declarePrivate('notifyException')
    def notifyException(self, ob, action, exc):
        '''
        Notifies this workflow that an action failed.
        '''
        pass

    security.declarePrivate('updateRoleMappingsFor')
    def updateRoleMappingsFor(self, ob):
        '''
        Changes the object permissions according to the current
        review_state.
        '''
        review_state = self.getReviewStateOf(ob)
        if review_state == 'private':
            anon_view = 0
            owner_modify = 1
            reviewer_view = 0
        elif review_state == 'pending':
            anon_view = 0
            owner_modify = 0  # Require a retraction for editing.
            reviewer_view = 1
        elif review_state == 'published':
            anon_view = 1
            owner_modify = 0
            reviewer_view = 1
        else:   # This object is in an unknown state
            anon_view = 0
            owner_modify = 1
            reviewer_view = 0

        # Modify role to permission mappings directly.

        return modifyPermissionMappings(ob,
            {'View': {'Anonymous': anon_view,
                      'Reviewer': reviewer_view,
                      'Owner': 1,
                      },
             'Modify portal content': {'Owner': owner_modify}})

Globals.InitializeClass(DefaultWorkflowDefinition)

addWorkflowClass(DefaultWorkflowDefinition)

