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
"""Home of the abstract Criterion base class.
$Id$
"""
__version__='$Revision$'[11:-2]

from OFS.SimpleItem import Item
from Globals import Persistent, InitializeClass
from Acquisition import Implicit
from AccessControl import ClassSecurityInfo
import string, operator

from Products.CMFCore.CMFCorePermissions import AccessContentsInformation
from TopicPermissions import ChangeTopics

class AbstractCriterion(Persistent, Item, Implicit):
    """ Abstract base class for Criterion objects. """

    security = ClassSecurityInfo()

    security.declareProtected(ChangeTopics, 'apply')
    def apply(self, command):
        """\
        command is expected to be a dictionary.  It gets applied
        to self.edit, and exists to make using Python Scripts
        easier.
        """
        apply(self.edit, (), command)

    security.declareProtected(ChangeTopics, 'editableAttributes')
    def editableAttributes(self):
        """\
        Return a list of editable attributes, used by topics
        to build commands to send to the 'edit' command of each
        criterion, which may vary.

        Requires concrete subclasses to implement the attribute
        '_editableAttributes' which is a tuple of attributes
        that can be edited, for example:

          _editableAttributes = ('value', 'direction',)
        """
        return self._editableAttributes

    security.declareProtected(AccessContentsInformation, 'Type')
    def Type(self):
        """\
        Return the Type of Criterion this object is.  This
        method can be overriden in subclasses, or those
        concrete subclasses must define the 'meta_type'
        attribute.
        """
        return self.meta_type
    
    security.declareProtected(AccessContentsInformation, 'Field')
    def Field(self):
        """\
        Return the field that this criterion searches on.  The
        concrete subclasses can override this method, or have
        the 'field' attribute.
        """
        return self.field

    security.declareProtected(AccessContentsInformation, 'Description')
    def Description(self):
        """\
        Return a brief but helpful description of the Criterion type,
        preferably based on the classes __doc__ string.
        """
        strip = string.strip
        split = string.split
        
        return string.join(             # Sew a string together after we:
            filter(operator.truth,      # Filter out empty lines
                   map(strip,           # strip whitespace off each line
                       split(self.__doc__, '\n') # from the classes doc string
                       )
                   )
            )

InitializeClass(AbstractCriterion)

        
