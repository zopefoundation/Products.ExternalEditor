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

"""List Criterion: A criterion that is a list
$Id$
"""
__version__='$Revision$'[11:-2]

from AccessControl import ClassSecurityInfo
from Topic import Topic
from AbstractCriterion import AbstractCriterion
import Globals, string, interfaces, operator

from Products.CMFCore import CMFCorePermissions
import TopicPermissions

class ListCriterion(AbstractCriterion):
    """\
    Represent a criterion which is a list of values (for an
    'OR' search).
    """
    __implements__ = (interfaces.Criterion,)

    meta_type = 'List Criterion'

    security = ClassSecurityInfo()

    _editableAttributes = ('value',)

    def __init__( self, id, field):
        self.id = id
        self.field = field
        
        self.value = ('',)

    security.declareProtected(TopicPermissions.ChangeTopics, 'getEditForm')
    def getEditForm(self):
        return "listc_edit"

    security.declareProtected(TopicPermissions.ChangeTopics, 'edit')
    def edit(self, value=None, REQUEST=None):
        """ Update the value we match against. """
        if value is not None:
            if type(value) == type(''):
                value = string.split(value, '\n')
            self.value = tuple(value)
        else:
            self.value = ('',)

    security.declareProtected(CMFCorePermissions.View, 'getCriteriaItems')
    def getCriteriaItems(self):
        """ Used by Topic.buildQuery to construct catalog queries """
        # filter out empty strings
        value = tuple(filter(operator.truth, self.value)) 
        return operator.truth(value) and ((self.field, self.value),) or ()



Globals.InitializeClass(ListCriterion)

# Register as a criteria type with the Topic class
Topic._criteriaTypes.append(ListCriterion)
