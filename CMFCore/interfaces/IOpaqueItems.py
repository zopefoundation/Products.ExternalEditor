##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
""" Marker interface for callable opaque items with manage_* hooks.

$Id$
"""

from Interface import Attribute
from Interface import Interface


class ICallableOpaqueItemWithHooks(Interface):
    """Marker interface for callable opaque items with manage_* hooks.

    Opaque items are subelements that are contained using something that
    is not an ObjectManager.

    On add, copy, move and delete operations a marked opaque items
    'manage_afterAdd', 'manage_afterClone' and 'manage_beforeDelete' hooks
    get called.
    """
