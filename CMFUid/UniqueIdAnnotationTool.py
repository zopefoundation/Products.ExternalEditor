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
"""Unique Id Annotation Tool

Provides support for managing unique id annotations.

$Id$
"""
__version__ = "$Revision$"

from Globals import InitializeClass, Persistent
from AccessControl import ClassSecurityInfo
from Acquisition import Implicit, aq_base

from OFS.SimpleItem import SimpleItem

from Products.CMFCore.utils import getToolByName, UniqueObject
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.permissions import ManagePortal

from Products.CMFUid.interfaces import IAnnotatedUniqueId

class AnnotatedUniqueId(Persistent, Implicit):
    """Unique id object used as annotation on (content) objects.
    """
    
    __implements__ = (
        IAnnotatedUniqueId,
    )
    
    def __init__(self, obj, id):
        """See IAnnotatedUniqueId.
        """
        self._uid = None
        self.id = id
        setattr(obj, id, self)
    
    def __call__(self):
        """See IAnnotatedUniqueId.
        """
        return self._uid
        
    def getId(self):
        """See IAnnotatedUniqueId.
        """
        return self.id
    
    def setUid(self, uid):
        """See IAnnotatedUniqueId.
        """
        self._uid = uid
        
    def manage_afterClone(self, item):
        """See IAnnotatedUniqueId.
        """
        # Duplicated unique ids on the copied object have to be avoided.
        # the uid object may already be removed by the 'manage_afterAdd'.
        # To be independent of the implementation of 'manage_afterAdd'
        # the unique id object probably gets removed another time.
        anno_tool = getToolByName(item, 'portal_uidannotation')
        if anno_tool.remove_on_clone:
            try:
                delattr(item, self.id)
            except KeyError, AttributeError:
                pass
    
    def manage_beforeDelete(self, item, container):
        """See IAnnotatedUniqueId.
        """
        # This helps in distinguishing renaming from copying/adding and
        # importing in 'manage_afterAdd' (see below)
        anno_tool = getToolByName(item, 'portal_uidannotation')
        if anno_tool.remove_on_add:
            self._cmf_uid_is_rename = True
    
    def manage_afterAdd(self, item, container):
        """See IAnnotatedUniqueId.
        """
        # 'is_rename' is set if deletion was caused by a rename/move.
        # The unique id is deleted only if the call is not part of 
        # a rename operation.
        # This way I the unique id gets deleted on imports.
        _is_rename = getattr(aq_base(self), '_cmf_uid_is_rename', None)
        anno_tool = getToolByName(item, 'portal_uidannotation')
        if anno_tool.remove_on_add and anno_tool.remove_on_clone \
           and not _is_rename:
            try:
                delattr(item, self.id)
            except KeyError, AttributeError:
                pass
        if _is_rename is not None:
            del self._cmf_uid_is_rename

InitializeClass(AnnotatedUniqueId)


class UniqueIdAnnotationTool(UniqueObject, SimpleItem, ActionProviderBase):
    __doc__ = __doc__ # copy from module

    __implements__ = (
        SimpleItem.__implements__,
    )

    id = 'portal_uidannotation'
    alternative_id = "portal_standard_uidannotation"
    meta_type = 'Unique Id Annotation Tool'
    
    # XXX make Zope properties out of those:
    remove_on_add = True
    remove_on_clone = True # caution when setting this to False!!!
    
    def __call__(self, obj, id):
        """return an empty unique id annotation
        """
        return AnnotatedUniqueId(obj, id)
