##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Uid Generator.

Provides support for generating unique ids.

$Id$
"""

import os
import time, random, md5, socket

from BTrees.Length import Length

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Acquisition import Implicit, aq_base, aq_parent

from OFS.SimpleItem import SimpleItem

from Products.CMFCore.utils import getToolByName, UniqueObject
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.permissions import ManagePortal

from Products.CMFUid.interfaces import IUniqueIdGenerator


class UniqueIdGeneratorTool(UniqueObject, SimpleItem, ActionProviderBase):
    """Generator of unique ids.
    """

    __implements__ = (
        IUniqueIdGenerator,
        ActionProviderBase.__implements__,
        SimpleItem.__implements__,
    )

    id = 'portal_uidgenerator'
    alternative_id = 'portal_standard_uidgenerator'
    meta_type = 'Unique Id Generator Tool'
    
    security = ClassSecurityInfo()
    
    security.declarePrivate('__init__')
    def __init__(self):
        """Initialize the generator
        """
        # Using the Length implementation of the BTree.Length module as 
        # counter handles zodb conflicts for us.
        self._uid_counter = Length(0)
    
    security.declarePrivate('__call__')
    def __call__(self):
        """See IUniqueIdGenerator.
        """
        self._uid_counter.change(+1)
        return self._uid_counter()
        
    security.declarePrivate('convert')
    def convert(self, uid):
        """See IUniqueIdGenerator.
        """
        return int(uid)

InitializeClass(UniqueIdGeneratorTool)
