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
import os
from Globals import HTMLFile, package_home, InitializeClass
from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore import utils
from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent, aq_inner

# Import permission names
from Products.CMFCore import CMFCorePermissions
import TopicPermissions

# Factory type information -- makes Topic objects play nicely
# with the Types Tool (portal_types)
factory_type_information = (
    {'id': 'Topic',
     'meta_type': 'Portal Topic',
     'description': ('Topics are canned queries for organizing content '
                     'with up to date queries into the catalog.'),
     'product': 'CMFTopic',
     'factory': 'addTopic',
     'immediate_view': 'topic_edit',
     'actions': ({'name': 'View',
                  'action': 'topic_view',
                  'permissions': (CMFCorePermissions.View,)},
                 {'name': 'Edit',
                  'action': 'topic_edit',
                  'permissions': (TopicPermissions.ChangeTopics,)},
                 {'name': 'Criteria',
                  'action': 'topic_criteria',
                  'permissions': (TopicPermissions.ChangeTopics,)},
                 {'name': 'Subtopics',
                  'action': 'topic_subtopics',
                  'permissions': (TopicPermissions.ChangeTopics,)},
                 ),                     # End Actions
     },
    )

def addTopic(self, id, title='', REQUEST=None):
    """
    Create an empty topic.
    """
    topic = Topic(id)
    topic.id = id
    topic.title = title
    self._setObject(id, topic)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( 'manage_main' )


class Topic( PortalFolder ):
    """
    Topics are a 'canned query'.  You construct catalog queries out
    of Criteria objects.
    """
    meta_type='Portal Topic'

    # Use Zope 2.3 declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(CMFCorePermissions.View)

    acquireCriteria = 1
    _criteriaTypes = []

    TOPIC_ACTION = 'manage_addProduct/CMFTopic/manage_addPortalTopicForm'
    topicMetatype = ({ 'name'         : meta_type,
                       'action'       : TOPIC_ACTION,
                       'permission'   : TopicPermissions.AddTopics,
                       },
                     )


    def _criteria_metatype_ids(self):
        result = []
        for mt in self._criteriaTypes:
            result.append(mt.meta_type)
        return tuple(result)
 
    security.declareProtected(TopicPermissions.ChangeTopics, 'listCriteria')
    def listCriteria(self):
        """ Return a list of our criteria objects """
        return self.objectValues(self._criteria_metatype_ids())


    security.declareProtected(TopicPermissions.ChangeTopics,
                              'listCriteriaTypes')
    def listCriteriaTypes(self):
        out = []
        for ct in self._criteriaTypes:
            out.append({
                'name': ct.meta_type,
                })
        return out
    
    security.declareProtected(TopicPermissions.ChangeTopics,
                              'listAvailableFields')
    def listAvailableFields(self):
        """ Return a list of available fields for new criteria """
        portal_catalog = utils.getToolByName(self, 'portal_catalog')
        currentfields = map(lambda x: x.field, self.listCriteria())
        availfields = filter(
            lambda field, cf=currentfields: field not in cf,
            portal_catalog.indexes()
            )
        return availfields

    security.declareProtected(TopicPermissions.ChangeTopics, 'listSubtopics')
    def listSubtopics(self):
        """ Return a list of our subtopics """
        return self.objectValues(self.meta_type)

    security.declareProtected(TopicPermissions.ChangeTopics, 'edit')
    def edit(self, acquireCriteria, title=None, REQUEST=None):
        """ Enable the acquisition of criteria from parent topics """
        self.acquireCriteria = acquireCriteria
        if title is not None: self.title = title
        
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect('%s/topic_view' % self.absolute_url())
    
    security.declareProtected(CMFCorePermissions.View, 'buildQuery')
    def buildQuery(self):
        """ Uses the criteria objects to construct a catalog query. """
        result = {}

        if self.acquireCriteria:
            try:
                parent = aq_parent(aq_inner(self))
                result.update(parent.buildQuery())
            except:
                pass

        for criterion in self.listCriteria():
            for key, value in criterion.getCriteriaItems():
                result[key] = value
        
        return result
    
    security.declareProtected(CMFCorePermissions.View, 'queryCatalog')
    def queryCatalog(self, REQUEST=None, **kw):
        """\
        Call self.buildQuery and augment any passed in query
        before calling the catalog.
        """
        kw.update(self.buildQuery())
        portal_catalog = utils.getToolByName(self, 'portal_catalog')
        return apply(portal_catalog.searchResults, (REQUEST,), kw)


    ### Criteria adding/editing/deleting
    security.declareProtected(TopicPermissions.ChangeTopics, 'addCriteria')
    def addCriteria(self, field, criteria_type, REQUEST=None):
        """ Create a new search criteria in this topic """
        crit = None
        newid = 'crit__%s' % field
        for ct in self._criteriaTypes:
            if criteria_type == ct.meta_type:
                crit = ct(newid, field)

        if crit is None:
            # No criteria type matched passed in value
            raise NameError, 'Unknown Criteria Type: %s' % criteria_type
        
        self._setObject(newid, crit)

        if REQUEST is not None:
            message = 'New criteria added.'
            REQUEST['RESPONSE'].redirect(
                '%s/topic_criteria?portal_status_message=%s' % (
                self.absolute_url(), message)
                )

    security.declareProtected(TopicPermissions.ChangeTopics, 'deleteCriteria')
    def deleteCriteria(self, criterion_ids=[], REQUEST=None):
        """ Delete selected criteria """
        for cid in criterion_ids:
            self._delObject(cid)

        if REQUEST is not None:
            message = 'Criteria deleted.'
            REQUEST['RESPONSE'].redirect(
                '%s/topic_criteria?portal_status_message=%s' % (
                self.absolute_url(), message)
                )

    security.declareProtected(TopicPermissions.ChangeTopics, 'editCriteria')
    def editCriteria(self, criteria=[], REQUEST=None):
        """\
        Save changes to the list of criteria.  This is done by going over
        the submitted criteria records and comparing them against the
        criteria object's editable attributes.  A 'command' object is
        built to send to the Criteria objects 'edit' command.
        """
        for rec in criteria:
            crit = self._getOb(rec.id)
            command = {}
            for attr in crit._editableAttributes:
                tmp = getattr(rec, attr, None)
                # Due to having multiple radio buttons on the same page
                # with the same name, but belonging to different records,
                # they needed to be associated with different ids.
                if tmp is None:
                    tmp = getattr(rec, '%s__%s' % (attr, rec.id), None)
                
                command[attr] = tmp
            apply(crit.edit, (), command)

        if REQUEST is not None:
            message = 'Changes saved.'
            REQUEST['RESPONSE'].redirect(
                '%s/topic_criteria?portal_status_message=%s' % (
                self.absolute_url(), message)
                )

    security.declareProtected(TopicPermissions.AddTopics, 'addSubtopic')
    def addSubtopic(self, id, REQUEST=None):
        """ Add a new subtopic """
        types = utils.getToolByName(self, 'portal_types')
        topictype = types.getTypeInfo('Topic')

        topictype.constructInstance(self, id)

        if REQUEST is not None:
            action = topictype.getActionById('subtopics')
            url = '%s/%s?portal_status_message=%s' % (
                self.absolute_url(), action,
                "Subtopic '%s' added" % id )
            REQUEST['RESPONSE'].redirect(url)
        else:
            return self._getOb(id)


# Intialize the Topic class, setting up security.
InitializeClass(Topic)

# Waah.  This seems to be the only way to get the icon in correctly
from Products.CMFCore.register import registerPortalContent
registerPortalContent(
    Topic,
    meta_type='Portal Topic',
    icon = 'images/topic.gif',
    permission = TopicPermissions.AddTopics,
    productGlobals = globals(),
    )
