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
import marshal

import Globals
import webdav
from DateTime import DateTime
from AccessControl import ClassSecurityInfo, User, getSecurityManager
from Products.CMFCore import PortalContent
from Products.CMFCore.CMFCorePermissions import View
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl

from References import ReferenceCollection


# Permission name
ManageWorkspaces = 'Manage Workspaces'


factory_type_information = (
  { 'id'             : 'Workspace'
  , 'meta_type'      : 'Workspace'
  , 'description'    : """\
Workspaces are places to put temporary references
to content you are currently working on.  Workspaces are designed to help
you navigate efficiently.
"""
  , 'icon'           : 'folder_icon.gif'
  , 'product'        : 'CMFWorkspaces'
  , 'factory'        : 'addWorkspace'
  , 'filter_content_types' : 0
  , 'immediate_view' : 'workspace_view'
  , 'actions'        : ( { 'id'            : 'view'
                         , 'name'          : 'Workspace'
                         , 'action'        : 'string:workspace_view'
                         , 'permissions'   : (View,)
                         , 'category'      : 'object'
                         }
                       , { 'id'            : 'metadata'
                         , 'name'          : 'Metadata'
                         , 'action'        : 'string:metadata_edit_form'
                         , 'permissions'   : (View,)
                         , 'category'      : 'object'
                         }
                       )
  }
,
)


class Workspace (PortalContent.PortalContent, 
                 DefaultDublinCoreImpl,
                 webdav.Collection.Collection):
    __doc__ = __doc__                   # Use the module docstring.

    meta_type = portal_type = 'Workspace'

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
        
    ## Basic FTP Support ##
    
    # The main thing we are punting on right now is generic PUT support into
    # the workspace. Subobjects can implement there own PUT factories to deal
    # with it down below.
    
    security.declareProtected(ManageWorkspaces, 'manage_FTPlist')
    def manage_FTPlist(self, REQUEST):
        """ FTP dir list """
        # Things currently missing: recursion and globbing support
        # Hey, I said it was basic ;^)
        out = []
        obs = [('..', self.aq_parent)] + self.listReferencedItems()
        for id, ob in obs:
            try:
                stat = marshal.loads(ob.manage_FTPstat(REQUEST))
            except:
                pass # Skip broken objects
            else:
                out.append((id, stat))
        
        return marshal.dumps(out)
    
    security.declareProtected(ManageWorkspaces, 'manage_FTPstat')
    def manage_FTPstat(self, REQUEST):
        """ FTP stat for listings """
        mode = 0040000
        
        try:
            if getSecurityManager().validateValue(self.manage_FTPlist):
                mode=mode | 0770
        except: 
            pass
        
        # Check for anonymous access
        if User.nobody.allowed(
                    self.manage_FTPlist,
                    self.manage_FTPlist.__roles__):
            mode=mode | 0007
            
        mtime=self.bobobase_modification_time().timeTime()
        
        # get owner and group
        owner=group='Zope'
        for user, roles in self.get_local_roles():
            if 'Owner' in roles:
                owner=user
                break
                
        return marshal.dumps((mode,0,0,1,owner,group,0,mtime,mtime,mtime))
        
    ## Basic traversal support ##        

    def __getitem__(self, key):
        """ Returns an object based on its unique workspace key """
        # Return the referenced object wrapped in our context
        try:
            return self._refs[key].dereference(self)
        except KeyError:
            request = getattr(self, 'REQUEST', None)
            if request is not None:
                method=request.get('REQUEST_METHOD', 'GET')
                if (request.maybe_webdav_client and 
                    not method in ('GET', 'POST')):
                    return webdav.NullResource.NullResource(
                        self, key, request).__of__(self)
        raise KeyError, key            

    security.declareProtected(ManageWorkspaces, 'has_key')
    def has_key(self, key):
        """ read-only mapping interface """
        return self._refs.has_key(key)

    security.declareProtected(ManageWorkspaces, 'objectValues')
    def objectValues(self):
        """Required by WebDAV"""
        return [ref.dereferenceDefault(self) for ref in self._refs.values()]
    
        
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

