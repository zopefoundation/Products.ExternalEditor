##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Uid Generator.

Provides support for generating unique ids.

$Id$
"""
__version__ = "$Revision$"

import os
import time, random, md5, socket

from BTrees.Length import Length

from Globals import InitializeClass, Persistent
from AccessControl import ClassSecurityInfo
from Acquisition import Implicit, aq_base, aq_parent

from OFS.SimpleItem import SimpleItem

from Products.CMFCore.utils import getToolByName, UniqueObject
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.permissions import ManagePortal

from Products.CMFUid.interfaces \
    import IUniqueIdGenerator, IAnnotatedUniqueId


class AnnotatedUniqueId(Persistent, Implicit):
    """Unique id object used as annotation on (content) objects.
    """
    
    __implements__ = (
        IAnnotatedUniqueId,
    )
    
    def __init__(self, uid):
        """See IAnnotatedUniqueId.
        """
        self._uid = uid
        
    def setId(self, id):
        """See IAnnotatedUniqueId.
        """
        self.id = id    # needed by opaque items implementation
        
    def getId(self):
        """See IAnnotatedUniqueId.
        """
        return self.id
    
    def __call__(self):
        """See IAnnotatedUniqueId.
        """
        return self._uid
        
    def manage_afterClone(self, item):
        """See IAnnotatedUniqueId.
        """
        # Duplicated unique ids on the copied object have to be avoided.
        # the uid object may already be removed by the 'manage_afterAdd'.
        # To be independent of the implementation of 'manage_afterAdd'
        # the unique id object probably gets removed another time.
        generator = getToolByName(item, 'portal_uidgenerator')
        if generator.remove_on_clone:
            try:
                delattr(item, self.id)
            except KeyError, AttributeError:
                pass
    
    def manage_beforeDelete(self, item, container):
        """See IAnnotatedUniqueId.
        """
        # This helps in distinguishing renaming from copying/adding and
        # importing in 'manage_afterAdd' (see below)
        generator = getToolByName(item, 'portal_uidgenerator')
        if generator.remove_on_add:
            self._cmf_uid_is_rename = True
    
    def manage_afterAdd(self, item, container):
        """See IAnnotatedUniqueId.
        """
        # 'is_rename' is set if deletion was caused by a rename/move.
        # The unique id is deleted only if the call is not part of 
        # a rename operation.
        # This way I the unique id gets deleted on imports.
        _is_rename = getattr(aq_base(self), '_cmf_uid_is_rename', None)
        generator = getToolByName(item, 'portal_uidgenerator')
        if generator.remove_on_add and generator.remove_on_clone \
           and not _is_rename:
            try:
                delattr(item, self.id)
            except KeyError, AttributeError:
                pass
        if _is_rename is not None:
            del self._cmf_uid_is_rename

InitializeClass(AnnotatedUniqueId)


class UniqueIdGeneratorTool(UniqueObject, SimpleItem, ActionProviderBase):
    """Generator of unique ids.
    """

    __implements__ = (
        SimpleItem.__implements__,
        IUniqueIdGenerator,
    )

    id = 'portal_uidgenerator'
    alternative_id = 'portal_standard_uidgenerator'
    meta_type = 'Unique Id Generator Tool'
    
    # make AnnotatedUniqueId class available through the tool
    # not meant to be altered on runtime !!!
    _uid_implementation = AnnotatedUniqueId
    
    security = ClassSecurityInfo()
    
    # XXX properties
    remove_on_add = True
    remove_on_clone = True
    
    security.declarePrivate('__init__')
    def __init__(self):
        """Initialize the generator
        """
        # Using the Length implementation of the BTree.Length module as 
        # counter handles zodb conflicts for us.
        self._uid_counter = Length(0)
    
    def reinitialize(self):
        """Reinitialze the uid generator.
        
        Avoids already existing unique ids beeing generated again.
        To be called e.g. after having imported content objects.
        """
        # XXX to be implemented by searching the max value in the catalog
        raise NotImplementedError
    
    security.declareProtected(ManagePortal, '__call__')
    def __call__(self):
        """See IUniqueIdGenerator.
        """
        self._uid_counter.change(+1)
        return self._uid_implementation(self._uid_counter())

InitializeClass(UniqueIdGeneratorTool)
