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
"""Various date criteria

$Id$
"""
__version__ = '$Revision$'[11:-2]

from Products.CMFTopic.AbstractCriterion import AbstractCriterion
from Products.CMFTopic.interfaces import Criterion
from Products.CMFTopic.Topic import Topic
from Products.CMFTopic.Topic import TopicPermissions

from Products.CMFCore import CMFCorePermissions

from AccessControl import ClassSecurityInfo
from DateTime.DateTime import DateTime
import Globals

import string, operator

class FriendlyDateCriterion( AbstractCriterion ):
    """
        Put a friendly interface on date range searches, like
        'where effective date is less than 5 days old'.
    """
    __implements__ = ( Criterion, )

    meta_type = 'Friendly Date Criterion'

    security = ClassSecurityInfo()

    _editableAttributes = ( 'value', 'operation', 'daterange' )

    _defaultDateOptions = ( (     1, '1 Day'    )
                          , (     2, '2 Days'   )
                          , (     5, '5 Days'   )
                          , (     7, '1 Week'   )
                          , (    14, '2 Weeks'  )
                          , (    31, '1 Month'  )
                          , (  31*3, '3 Months' )
                          , (  31*6, '6 Months' )
                          , (   365, '1 Year'   )
                          , ( 365*2, '2 years'  )
                          )

    def __init__( self, id, field ):

        self.id = id
        self.field = field
        self.value = None
        self.operation = 'min'
        self.daterange = 'old'

    security.declarePublic( 'defaultDateOptions' )
    def defaultDateOptions( self ):
        """
            Return a list of default values and labels for date options.
        """
        return self._defaultDateOptions

    security.declareProtected( TopicPermissions.ChangeTopics, 'getEditForm' )
    def getEditForm( self ):
        """
            Return the name of the skin method used by Topic to edit
            criteria of this type.
        """
        return 'friendlydatec_editform'

    security.declareProtected( TopicPermissions.ChangeTopics, 'edit' )
    def edit( self
            , value=None
            , operation='min'
            , daterange='old'
            ):
        """
            Update the values to match against.
        """
        if value in ( None, '' ):
            self.value = None
        else:
            try:
                self.value = int( value )
            except:
                raise ValueError, 'Supplied value should be an int'

        if operation in ( 'min','max' ):
            self.operation = operation
        else:
            raise ValueError, 'Operation type not in set {min,max}'

        if daterange in ( 'old', 'ahead' ):
            self.daterange = daterange
        else:
            raise ValueError, 'Date range not in set {old,ahead}'

    security.declareProtected( CMFCorePermissions.View, 'getCriteriaItems' )
    def getCriteriaItems( self ):
        """
            Return a sequence of items to be used to build the catalog query.
        """
        result = []

        if self.value is not None:

            field = self.Field()
            value = self.value

            # Negate the value for 'old' days
            if self.daterange == 'old':
                value = -value

            date = DateTime() + value

            result.append( ( field, date ) )

            result.append( ( '%s_usage' % field
                           , 'range:%s' % self.operation
                           ) )

        return result

Globals.InitializeClass( FriendlyDateCriterion )

# Register as a criteria type with the Topic class
Topic._criteriaTypes.append( FriendlyDateCriterion )
