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
"""Workspaces are for gathering content references into logical collections.

Workspaces in general provide:

  - Mechanism for adding and removing content element references.

  - Mechanism for adding contained references to other workspaces.

  - Presentation of the content references, indicating the content's:

    o Title, as a link to the actual content

    o Type

    o Creation date

    o Lock / staging status (distinguishing whether or not the
      workspace visitor is the owner of the lock)

    and so forth.

  - Knobs to adjust the sorting of the entries according to column
    and direction

$Id$
"""

from types import StringType

import Globals
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions, PortalContent

from References import ReferenceCollection


# Permission name
ManageWorkspaces = 'Manage Workspaces'


factory_type_information = (
    { 'id'             : 'Workspace',
      'meta_type'      : 'Workspace',
      'description'    : """Workspaces are places to put temporary references
to content you are currently working on.  Workspaces are designed to help
you navigate efficiently.""",
      'icon'           : 'folder_icon.gif',
      'product'        : 'CMFWorkspaces',
      'factory'        : 'addWorkspace',
      'filter_content_types' : 0,
      'immediate_view' : 'workspace_view',
      'actions'        :
      ({'id'            : 'view',
        'name'          : 'Workspace',
        'action'        : 'workspace_view',
        'permissions'   : (CMFCorePermissions.View,),
        'category'      : 'object',
        },
       )
      },
    )


class Workspace (PortalContent.PortalContent):
    __doc__ = __doc__                   # Use the module docstring.

    meta_type = 'Workspace'

    security = ClassSecurityInfo()
    security.setPermissionDefault(ManageWorkspaces, ('Manager', 'Owner'))
    security.declareObjectProtected(ManageWorkspaces)

    # Responsibilities:
    #  - Retain a collection of explicitly selected references
    #  - Provide an editing interface on those references
    #  - Return sorted list of objects in collection
    #    - Sorting options are by-attribute, in ascending or descending order

    _refs = None

    _allowed_sort_attrs = ('Title', 'Type', 'CreationDate')

    def __init__(self, id, title=""):
        self._refs = ReferenceCollection()
        self.id = id
        self.title = title

    # Editing interface:
    # We add by object, but remove by reference id.

    security.declareProtected(ManageWorkspaces, 'addReference')
    def addReference(self, object):
        """Adds an item to the collection."""
        self._refs.addReference(object)

    security.declareProtected(ManageWorkspaces, 'removeReference')
    def removeReference(self, id):
        """Removes an existing item according to reference collection id.

        Raises KeyError if the id does not exist."""
        self._refs.removeReference(id)

    security.declareProtected(ManageWorkspaces, 'listReferencedItems')
    def listReferencedItems(self, sort_attr='Title', sort_order='normal'):
        """Returns a list of pairs containing (collection_id, object)."""
        if not sort_attr in self._allowed_sort_attrs:
            raise ValueError, "'%s' is not a valid sort attribute." % sort_attr
        if not sort_order in ('normal', 'reverse'):
            raise ValueError, (
                "'%s' is not a valid sort order." % sort_order)
        seq = []
        for cid, ref in self._refs.items():
            ob = ref.dereferenceDefault(self)
            if ob is None:
                ob = MissingObject(repr(ref))
                sort_key = ''
            else:
                v = getattr(ob, sort_attr, None)
                if v is None:
                    sort_key = ob
                elif callable(v):
                    sort_key = v()
                else:
                    sort_key = v
                sort_key = str(sort_key).lower()
            seq.append((sort_key, cid, ob))

        seq.sort()
        if sort_order == 'reverse':
            seq.reverse()

        return map(lambda item: item[1:], seq)

Globals.InitializeClass(Workspace)



class MissingObject:
    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

    def __init__(self, s):
        self.title = '(Missing or inaccessible: %s)' % s

    def Title(self):
        return self.title

    def absolute_url(self):
        return '#'

Globals.InitializeClass(MissingObject)


def addWorkspace(dispatcher, id, title='', REQUEST=None):
    """Add a new workspace."""

    workspace = Workspace(id, title)
    dispatcher._setObject(id, workspace)
    workspace = dispatcher._getOb(id)
    if REQUEST is not None:
        return dispatcher.manage_main(dispatcher, REQUEST)

