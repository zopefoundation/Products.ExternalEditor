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
A simple submit/review/publish workflow.
$Id$
'''

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
        tool.notifyBefore(ob, action)
        try:
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
        except:
            tool.notifyException(ob, action, sys.exc_info())
            raise
        else:
            tool.notifySuccess(ob, action)
            catalog = getToolByName(self, 'portal_catalog', None)
            if catalog is not None:
                catalog.reindexObject(ob)

    security.declarePrivate('notifyCreated')
    def notifyCreated(self, ob):
        '''
        Notifies this workflow after an object has been created
        and put in its new place.
        '''
        self.updateRoleMappingsFor(ob)

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
        self.updateRoleMappingsFor(ob)

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
        # Modify role to permission mappings directly.

        return modifyPermissionMappings(ob,
            {'View': {'Anonymous': anon_view,
                      'Reviewer': reviewer_view,
                      'Owner': 1,
                      },
             'Modify portal content': {'Owner': owner_modify}})

Globals.InitializeClass(DefaultWorkflowDefinition)

addWorkflowClass(DefaultWorkflowDefinition)

