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

"""Basic workflow tool.
$Id$
"""
__version__='$Revision$'[11:-2]


from utils import UniqueObject, _checkPermission, getToolByName
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass
from AccessControl.Permission import Permission
from AccessControl import ClassSecurityInfo


class WorkflowTool (UniqueObject, SimpleItem):
    # This tool accesses and changes the workflow state of content.
    # This default implementation assumes there is a review_state
    # attribute on all content objects.  This assumption can be
    # changed in subclasses of WorkflowTool.
    id = 'portal_workflow'
    meta_type = 'CMF Workflow Tool'

    security = ClassSecurityInfo()

    security.declarePublic('getStateFor')
    def getStateFor(self, content):
        '''Returns the current workflow state of content.  State
        is implemented as a mapping object.
        '''
        return content.getReviewState()

    security.declarePublic('listAllowableTransitionsFor')
    def listAllowableTransitionsFor(self, content):
        '''Returns the list of transition names which are available
        to the current user from the state of content.
        '''
        # Note that (1) this default implementation allows
        # a transition from any review state to any other state and
        # (2) the transition names are the same as the new state names.
        # Neither of these assumptions is necessary in different
        # implementations of workflow.
        state = content.getReviewState()
        r = []
        if state == 'private':
            if _checkPermission('Modify portal content', content):
                r.append('private')
            if _checkPermission('Request review', content):
                r.append('pending')
            if _checkPermission('Review portal content', content):
                r.append('published')
        elif state == 'pending':
            if _checkPermission('Modify portal content', content):
                r.append('private')
                r.append('pending')
            if _checkPermission('Review portal content', content):
                r.append('published')
        elif state == 'published':
            if _checkPermission('Modify portal content', content):
                r.append('private')
                r.append('pending')
                r.append('published')
        return tuple(r)

    security.declarePublic('changeStateFor')
    def changeStateFor(self, content, transition, comment, **kw):
        '''Executes the given transition name on content with the
        keyword arguments as modifiers and the comment as a history
        attribute. Returns content, which may be in a new location.
        Remember there are no implicit security assertions;
        implementations will need to add code that calls checkPermission.
        '''
        if transition not in self.listAllowableTransitionsFor(content):
            raise 'WorkflowException', 'Specified transition is not allowed.'
        content.setReviewState(transition, comment)

        set = self.getPermissionUpdatesFor(content)
        for role, grant, revoke in set:
            for p in content.ac_inherited_permissions(1):
                name, value = p[:2]
                p=Permission(name, value, content)
                if name in grant:
                    p.setRole(role, 1)
                elif name in revoke:
                    p.setRole(role, 0)

        content.reindexObject()
        return content

    security.declarePrivate('getPermissionUpdatesFor')
    def getPermissionUpdatesFor(self, content):
        '''Returns a list of roles and the permissions that
        should be granted or revoked.'''
        review_state = content.getReviewState()
        if content.review_state == 'private':
            # Revoke 'View' from Anonymous and Reviewer
            set = (
                ('Anonymous', (), ('View',)),
                ('Reviewer', (), ('View',)),
                )
        elif content.review_state == 'pending':
            # Give Reviewer 'View', revoke from Anonymous
            set = (
                ('Anonymous', (), ('View',)),
                ('Reviewer', ('View',), ()),
                )
        elif content.review_state == 'published':
            # Give Anonymous 'View'
            set = (
                ('Anonymous', ('View',), ()),
                )
        return set

    security.declarePublic('listAddableTypesFor')
    def listAddableTypesFor(self, container):
        '''Lists the meta types that are allowed to be added by
        the user to the given container.
        '''
        # Not implemented.  Is this the right way to add new content?
        pass

    security.declarePrivate('listActions')
    def listActions(self, info):
        actions = None
        # The following operation is quite expensive.
        # We don't need to perform it if the user
        # doesn't have the required permission.
        # Note we make the assumption that anonymous users aren't allowed
        # to review content; this might need to be configurable.
        if not info.isAnonymous:
            content = info.content
            content_url = info.content_url
            content_creator = content.Creator()
            membership = getToolByName(self, 'portal_membership')
            current_user = membership.getAuthenticatedMember().getUserName()
            review_state = getattr(content, 'review_state', None)
            actions = []

            if review_state == 'private':
                actions.append({'name': 'Submit',
                                'url': content_url + '/content_submit_form',
                                'permission': 'Request review',
                                'category': 'object' })

            if review_state == 'pending':
                if _checkPermission('Review portal content', info.portal):
                    actions.extend([{'name': 'Publish',
                                     'url': content_url + '/content_publish_form',
                                     'permission': 'Review portal content',
                                     'category': 'object' },
                                    {'name': 'Reject',
                                     'url': content_url + '/content_reject_form',
                                     'permission': 'Review portal content',
                                     'category': 'object' }])

                if content_creator == current_user:
                    actions.append({'name': 'Retract',
                                    'url': content_url + '/content_retract_form',
                                    'permission': 'Request review',
                                    'category': 'object' })

            if (review_state == 'published' and content_creator == current_user):
                actions.append({'name': 'Retract',
                                'url': content_url + '/content_retract_form',
                                'permission': 'Request review',
                                'category': 'object' })

            catalog = getToolByName(self, 'portal_catalog', None)
            if catalog is not None:
                pending = len(catalog.searchResults(
                    review_state='pending'))
                if pending > 0:
                    actions.append(
                        {'name': 'Pending review (%d)' % pending,
                         'url': info.portal_url +
                         '/search?review_state=pending',
                         'permissions': ['Review portal content'],
                         'category': 'global'},
                        )
        return actions


InitializeClass(WorkflowTool)
