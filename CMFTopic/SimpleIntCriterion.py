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

from Products.CMFTopic import TopicPermissions
from Products.CMFTopic.AbstractCriterion import AbstractCriterion
from Products.CMFTopic.Topic import Topic
from Products.CMFTopic.interfaces import Criterion

from Products.CMFCore import CMFCorePermissions

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

class SimpleIntCriterion( AbstractCriterion ):
    """
        Represent a simple field-match for an integer value, including
        catalog range searches.    
    """
    __implements__ = ( Criterion, )

    meta_type = 'Integer Criterion'

    security = ClassSecurityInfo()
    _editableAttributes = ( 'value', 'direction' )

    MINIMUM = 'min'
    MAXIMUM = 'max'
    MINMAX = 'min:max'

    def __init__(self, id, field):
        self.id = id
        self.field = field
        self.value = self.direction = None

    security.declareProtected( TopicPermissions.ChangeTopics, 'getEditForm' )
    def getEditForm( self ):
        """
            Return the name of skin method which renders the form
            used to edit this kind of criterion.
        """
        return 'sic_edit'

    security.declareProtected( TopicPermissions.ChangeTopics, 'getValueString' )
    def getValueString( self ):
        """
            Return a string representation of the value for which this
            criterion filters.
        """
        if self.value is None:
            return ''

        if self.direction == self.MINMAX:

            value = self.value

            if type( value ) is not type( () ):
                value = ( value, value )

            return '%s %s' % value

        return str( self.value )

    security.declareProtected( TopicPermissions.ChangeTopics, 'edit' )
    def edit( self, value, direction=None ):
        """
            Update the value to be filtered, and the "direction" qualifier.
        """
        from string import strip, split # XXX: WAAAA! 2.3 compatibility

        if type( value ) == type( '' ):
           value = strip( value )

        if not value:
            # An empty string was passed in, which evals to None
            self.value = self.direction = None

        elif direction:

            if direction == self.MINMAX:

                if type( value ) == type( '' ):
                    minimum, maximum = split( value, ' ' )
                else:
                    minimum, maximum = value

                self.value = ( int( minimum ), int( maximum ) )

            else:
                self.value = int( value )

            self.direction = direction

        else:
            self.value = int( value )
            self.direction = None

    security.declareProtected( CMFCorePermissions.View, 'getCriteriaItems' )
    def getCriteriaItems( self ):
        """
            Return a tuple of query elements to be passed to the catalog
            (used by 'Topic.buildQuery()').
        """
        if self.value is None:
            return ()

        result = [ ( self.Field(), self.value ) ]

        if self.direction is not None:
            result.append( ( '%s_usage' % self.Field()
                           , 'range:%s' % self.direction
                           ) )

        return tuple( result )



InitializeClass( SimpleIntCriterion )

# Register as a criteria type with the Topic class
Topic._criteriaTypes.append( SimpleIntCriterion )
