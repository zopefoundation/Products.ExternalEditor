##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Utilities for CMFStaging.

$Id$
"""

import types
from cStringIO import StringIO
from cPickle import Pickler, Unpickler

from Acquisition import aq_inner, aq_parent
from AccessControl.PermissionRole import rolesForPermissionOn
from AccessControl import getSecurityManager


_marker = []  # Create a new marker.

def getPortal(context, default=_marker):
    portal = context
    while not getattr(portal, '_isPortalRoot', 0):
        portal = aq_parent(aq_inner(portal))
        if portal is None:
            if default is _marker:
                raise ValueError("Object is not in context of a portal")
            return default
    return portal


def verifyPermission(permission, obj):
    roles = rolesForPermissionOn(permission, obj)
    if type(roles) is types.StringType:
        roles=[roles]
    # C implementation of validate does not take keyword arguments
    accessed, container, name, value = obj, obj, '', obj
    getSecurityManager().validate(accessed, container, name, value, roles)


def unproxied(obj):
    """Removes proxy wrappers, returning the target, which might be unwrapped.
    
    The References product generates proxies of this sort.
    """
    try:
        d = obj.__dict__
    except AttributeError:
        return obj
    return d.get('_Proxy__target', obj)


def getProxyReference(obj):
    """Returns the reference that created a proxy.

    If the argument is not a proxy, an error will occur.
    """
    return obj.__dict__["_Proxy__reference"]


def cloneByPickle(obj):
    """Makes a copy of a ZODB object, loading ghosts as needed.
    """
    def persistent_id(o):
        if getattr(o, '_p_changed', 0) is None:
            o._p_changed = 0
        return None

    stream = StringIO()
    p = Pickler(stream, 1)
    p.persistent_id = persistent_id
    p.dump(obj)
    stream.seek(0)
    u = Unpickler(stream)
    return u.load()

