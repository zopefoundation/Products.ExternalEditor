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
"""Reference objects, used for indirect dependencies between content objects.

In particular, references are used in workspaces to maintain handles on
content that is effectively, but not actually contained in the workspace.
References also are used for content which consists of multiple parts.

$Id$
"""

import time

from ExtensionClass import Base
from Acquisition import aq_inner, aq_parent
from ZODB import Persistent
import Globals
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName


class RelativeReference (Base):
    """Provides an indirection for a reference to portal content.

    The indirection is relative to a base object."""

    security = ClassSecurityInfo()

    def __init__(self, object):
        """Retain a reference to the target object."""
        base = self._getBaseObject(object)
        o_path = object.getPhysicalPath()
        b_path = base.getPhysicalPath()
        if o_path[:len(b_path)] != b_path:
            raise RuntimeError, (
                'Referenced object %s is outside scope %s' % (
                '/'.join(o_path), '/'.join(b_path)))
        self._path = o_path[len(b_path):]
        self.id = object.getId()
        self.creation_time = time.time()

    def _getBaseObject(self, context):
        # Meant to be overridden.
        raise NotImplementedError

    security.declarePublic('getId')
    def getId(self):
        return self.id

    security.declarePublic('dereferenceDefault')
    def dereferenceDefault(self, context, default=None):
        """Returns the original object, wrapped in the specified context.

        Returns the default value if not found.
        """
        base = self._getBaseObject(context)
        ob = base.restrictedTraverse(self._path, None)
        if ob is None:
            return default
        return ob.__of__(context)

    security.declarePublic('dereference')
    def dereference(self, context):
        """Returns the original object, wrapped in the specified context.
        """
        base = self._getBaseObject(context)
        ob = base.restrictedTraverse(self._path)
        return ob.__of__(context)

    def __repr__(self):
        return '<%s, path=%s>' % (self.__class__.__name__,
                                  '/'.join(self._path))

    def __cmp__(self, other):
        """Compares this object with another.

        References that point to the same object are equivalent."""
        if isinstance(other, self.__class__):
            return cmp(self._path, other._path)
        return -1

Globals.InitializeClass(RelativeReference)



class PortalRelativeReference (RelativeReference):
    """Reference relative to a portal."""

    def _getBaseObject(self, context):
        url_tool = getToolByName(context, 'portal_url')
        return aq_parent(aq_inner(url_tool))

Globals.InitializeClass(PortalRelativeReference)



class ReferenceCollection (Persistent):
    "An unordered collection of references, each stored under a unique id."

    security = ClassSecurityInfo()

    _reference_factory = PortalRelativeReference
    _ignore_dups = 1

    def __init__(self):
        self._refs = {}

    def _new_id(self, object):
        """Produce a new, locally unique string id for an object."""
        id = object.getId()
        i = 0
        while self._refs.has_key(id):
            i += 1
            id = '%s~%d' % (object.getId(), i)
        return id

    security.declarePrivate('addReference')
    def addReference(self, object):
        """Store a reference under a new, unique id."""
        r = self._reference_factory(object)
        if self._ignore_dups:
            for other in self._refs.values():
                if other == r:
                    # We already have a reference to this object.
                    return
        self._refs[self._new_id(object)] = r
        self._p_changed = 1

    security.declarePrivate('removeReference')
    def removeReference(self, collection_id):
        """Remove an existing reference according to collection id.

        Raises KeyError if the id does not exist."""
        del self._refs[collection_id]
        self._p_changed = 1

    # Dictionary-like access - delegates to actual dictionary.
    security.declarePrivate('keys')
    def keys(self):
        """Return all reference ids."""
        return self._refs.keys()
        
    security.declarePrivate('has_key')
    def has_key(self, key):
        """Check for existence of key"""
        return self._refs.has_key(key)

    security.declarePrivate('values')
    def values(self):
        """Return all reference values."""
        return self._refs.values()

    security.declarePrivate('items')
    def items(self):
        """Return all reference (key, values) pairs."""
        return self._refs.items()

    def __getitem__(self, id):
        """Return value at id.

        Raises KeyError if the id does not exist."""
        return self._refs[id]

    def __len__(self):
        return len(self._refs)

    def __repr__(self):
        return ("<%s with %d elements at 0x%s>"
                % (self.__class__.__name__, len(self), hex(id(self))[2:]))

Globals.InitializeClass(ReferenceCollection)

