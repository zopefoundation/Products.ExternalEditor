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
"""Simple int-matching criterion
$Id$
"""
__version__='$Revision$'[11:-2]

from AbstractCriterion import AbstractCriterion
from AccessControl import ClassSecurityInfo
from Topic import Topic
import Globals, interfaces, string

from Products.CMFCore import CMFCorePermissions
import TopicPermissions

class SimpleIntCriterion(AbstractCriterion):
    """\
    Represent a simple field-match for an integer value, including
    catalog range searches.    
    """
    __implements__ = (interfaces.Criterion,)
    meta_type = 'Integer Criterion'

    security = ClassSecurityInfo()
    _editableAttributes = ('value', 'direction',)

    MINIMUM = 'min'
    MAXIMUM = 'max'
    MINMAX = 'min:max'

    def __init__(self, id, field):
        self.id = id
        self.field = field
        self.value = self.direction = None

    security.declareProtected(TopicPermissions.ChangeTopics, 'getEditForm')
    def getEditForm(self):
        """ Used to build sequences of editable criteria """
        return 'sic_edit'

    security.declareProtected(TopicPermissions.ChangeTopics, 'edit')
    def edit(self, value, direction=None):
        """ Update the value we match against. """
        if type(value) == type('') and (not string.strip(value)):
            # An empty string was passed in, which evals to None
            self.value = self.direction = None
        elif direction:
            self.value = int(value)
            self.direction = direction
        else:
            self.value = int(value)
            self.direction = None

    security.declareProtected(CMFCorePermissions.View, 'getCriteriaItems')
    def getCriteriaItems(self):
        """ Used by Topic.buildQuery() """
        if self.value is None:
            return ()

        result = ((self.Field(), self.value),)

        if self.direction is not None:
            result = result + (('%s_usage' % self.Field(), 
                                'range:%s' % self.direction ),)
        return result



Globals.InitializeClass(SimpleIntCriterion)

# Register as a criteria type with the Topic class
Topic._criteriaTypes.append(SimpleIntCriterion)
