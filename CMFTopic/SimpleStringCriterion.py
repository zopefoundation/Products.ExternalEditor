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

"""Simple string-matching criterion class
$Id$
"""
__version__='$Revision$'[11:-2]

from AbstractCriterion import AbstractCriterion
from AccessControl import ClassSecurityInfo
from Topic import Topic
import Globals, interfaces

from Products.CMFCore import CMFCorePermissions
import TopicPermissions

class SimpleStringCriterion(AbstractCriterion):
    """
    Represent a simple field-match for a string value.
    """
    __implements__ = (interfaces.Criterion,)

    meta_type = 'String Criterion'
    security = ClassSecurityInfo()

    _editableAttributes = ('value',)

    def __init__(self, id, field):
        self.id = id
        self.field = field
        self.value = ''
        
    security.declareProtected(TopicPermissions.ChangeTopics, 'getEditForm')
    def getEditForm(self):
        " Return the skinned name of the edit form "
        return 'ssc_edit'
    
    security.declareProtected(TopicPermissions.ChangeTopics, 'edit')
    def edit(self, value):
        """ Update the value we are to match up against """
        self.value = str(value)
    
    security.declareProtected(CMFCorePermissions.View, 'getCriteriaItems')
    def getCriteriaItems( self ):
        """ Return a sequence of criteria items, used by Topic.buildQuery """
        return self.value is not '' and ((self.field, self.value),) or ()


Globals.InitializeClass(SimpleStringCriterion)

# Register as a criteria type with the Topic class
Topic._criteriaTypes.append(SimpleStringCriterion)
