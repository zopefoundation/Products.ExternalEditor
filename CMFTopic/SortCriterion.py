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
"""
    Declare simple string-match criterion class.
"""
from AbstractCriterion import AbstractCriterion
from AccessControl import ClassSecurityInfo
from Topic import Topic
import Globals, interfaces

from Products.CMFCore import CMFCorePermissions
import TopicPermissions

class SortCriterion(AbstractCriterion):
    """
        Represent a mock criterion, to allow spelling the sort order
        and reversal items in a catalog query.
    """
    __implements__ = (interfaces.Criterion,)

    meta_type = 'Sort Criterion'
    security = ClassSecurityInfo()
    field = None # Don't prevent use of field in other criteria

    _editableAttributes = ('reversed',)

    def __init__(self, id, index):
        self.id = id
        self.index = index
        self.reversed = 0
        
    # inherit permissions
    def Field( self ):
        """
            Map the stock Criterion interface.
        """
        return self.index

    security.declareProtected(TopicPermissions.ChangeTopics, 'getEditForm')
    def getEditForm(self):
        " Return the skinned name of the edit form "
        return 'sort_edit'
    
    security.declareProtected(TopicPermissions.ChangeTopics, 'edit')
    def edit(self, reversed):
        """ Update the value we are to match up against """
        self.reversed = not not reversed
    
    security.declareProtected(CMFCorePermissions.View, 'getCriteriaItems')
    def getCriteriaItems( self ):
        """ Return a sequence of criteria items, used by Topic.buildQuery """
        result = [ ( 'sort_on', self.index ) ]
        if self.reversed:
            result.append( ( 'sort_order', 'reverse' ) )
        return tuple( result )


Globals.InitializeClass(SortCriterion)

# Register as a criteria type with the Topic class
Topic._criteriaTypes.append(SortCriterion)
