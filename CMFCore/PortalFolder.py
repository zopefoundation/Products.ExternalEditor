##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
##############################################################################
"""
    Portal folders organize content.
"""
ADD_FOLDERS_PERMISSION = 'Add portal folders'
ADD_CONTENT_PERMISSION = 'Add portal content'

import Globals, re, base64, marshal, string
import CMFCorePermissions

from CMFCorePermissions import View, ManageProperties
from CMFCorePermissions import AddPortalFolders, AddPortalContent
from OFS.Folder import Folder
from OFS.ObjectManager import REPLACEABLE
from Globals import HTMLFile
from AccessControl import getSecurityManager, ClassSecurityInfo
from Acquisition import aq_parent, aq_inner, aq_base
from DynamicType import DynamicType
from utils import getToolByName

factory_type_information = ( { 'id'             : 'Folder'
                             , 'meta_type'      : 'Portal Folder'
                             , 'description'    : """\
Use folders to put content in categories."""
                             , 'icon'           : 'folder_icon.gif'
                             , 'product'        : 'CMFCore'
                             , 'factory'        : 'manage_addPortalFolder'
                             , 'filter_content_types' : 0
                             , 'immediate_view' : 'folder_edit_form'
                             , 'actions'        :
                                ( { 'name'          : 'View'
                                  , 'action'        : ''
                                  , 'permissions'   : (View,)
                                  , 'category'      : 'folder'
                                  }
                                , { 'name'          : 'Edit'
                                  , 'action'        : 'folder_edit_form'
                                  , 'permissions'   : (ManageProperties,)
                                  , 'category'      : 'folder'
                                  }
                                , { 'name'          : 'Syndication'
                                  , 'action'        : 'synPropertiesForm'
                                  , 'permissions'   : (ManageProperties,)
                                  , 'category'      : 'folder'
                                  }
                                )
                             }
                           ,
                           )


class PortalFolder( Folder, DynamicType ):
    """
        Implements portal content management, but not UI details.
    """
    meta_type = 'Portal Folder'
    portal_type = 'Folder'

    security = ClassSecurityInfo()

    description = ''

    def __init__( self, id, title='' ):
        self.id = id
        self.title = title

    security.declareProtected(CMFCorePermissions.ManageProperties, 'edit')
    def edit(self, title='', description=''):
        """
        Edit the folder title (and possibly other attributes later)
        """
        self.title = title
        self.description = description

    security.declarePublic('allowedContentTypes')
    def allowedContentTypes( self ):
        """
            List type info objects for types which can be added in
            this folder.
        """
        result = []
        portal_types = getToolByName(self, 'portal_types')
        pt = self._getPortalTypeName()
        myType = portal_types.getTypeInfo(pt)

        if myType is not None:
            for contentType in portal_types.listTypeInfo():
                if myType.allowType( contentType.Type() ):
                    result.append( contentType )
        else:
            result = portal_types.listTypeInfo()

        return filter( lambda typ, container=self:
                          typ.isConstructionAllowed( container )
                     , result )
    
    security.declareProtected(AddPortalFolders, 'manage_addPortalFolder')
    def manage_addPortalFolder(self, id, title='', REQUEST=None):
        """Add a new PortalFolder object with id *id*.
        """
        ob=PortalFolder(id, title)
        self._setObject(id, ob)
        if REQUEST is not None:
            return self.folder_contents(
                self, REQUEST, portal_status_message="Folder added")
    
    def _morphSpec(self, spec):
        '''
        spec is a sequence of meta_types, a string containing one meta type,
        or None.  If spec is empty or None, returns all contentish
        meta_types.  Otherwise ensures all of the given meta types are
        contentish.
        '''
        new_spec = []
        types_tool = getToolByName(self, 'portal_types')
        types = types_tool.listContentTypes( container=self, by_metatype=1 )
        if spec is not None:
            if type(spec) == type(''):
                spec = [spec]
            for meta_type in spec:
                if not meta_type in types:
                    raise ValueError, ('%s is not a content type'
                                       % meta_type )
                new_spec.append(meta_type)
        return new_spec or types
    
    def _filteredItems( self, ids, filter ):
        """
            Apply filter, a mapping, to child objects indicated by 'ids',
            returning a sequence of ( id, obj ) tuples.
        """
        query = apply( ContentFilter, (), filter )
        result = []
        append = result.append
        get = self._getOb
        always_incl_folders = not filter.get('FilterIncludesFolders', 0)
        for id in ids:
            obj = get( id )
            include = 0
            if (always_incl_folders and hasattr(obj, 'meta_type') and
                obj.meta_type == PortalFolder.meta_type):
                include = 1
            elif query(obj):
                include = 1
            if include:
                append( (id, obj) )
        return result

    security.declarePublic('contentIds')
    def contentIds( self, spec=None, filter=None):
        """
            Provide a filtered view onto 'objectIds', allowing only
            PortalFolders and PortalContent-derivatives to show through.

            If 'kw' passed, use them to filter the results further,
            qua the standard Zope filter interface.
        """
        spec = self._morphSpec( spec )
        ids = self.objectIds( spec )

        if not filter:
            return ids

        return map( lambda item: item[0],
                    self._filteredItems( ids, filter ) )

    security.declarePublic('contentValues')
    def contentValues( self, spec=None, filter=None ):
        """
            Provide a filtered view onto 'objectValues', allowing only
            PortalFolders and PortalContent-derivatives to show through.
        """
        spec = self._morphSpec( spec )
        if not filter:
            return self.objectValues( spec )

        ids = self.objectIds( spec )
        return map( lambda item: item[1],
                    self._filteredItems( ids, filter ) )

    security.declarePublic('contentItems')
    def contentItems( self, spec=None, filter=None ):
        """
            Provide a filtered view onto 'objectItems', allowing only
            PortalFolders and PortalContent-derivatives to show through.
        """
        spec = self._morphSpec( spec )
        if not filter:
            return self.objectItems( spec )

        ids = self.objectIds( spec )
        return self._filteredItems( ids, filter )

    security.declareProtected(View, 'Title')
    def Title( self ):
        """
             Implement dublin core Title
        """
        return self.title

    security.declareProtected(View, 'Description')
    def Description( self ):
        """
             Implement dublin core Description
        """
        return self.description

    security.declareProtected(View, 'Type')
    def Type( self ):
        """
             Implement dublin core type
        """
        ti = self.getTypeInfo()
        if ti is not None:
            return ti.Type()
        return self.meta_type

    security.declarePublic('encodeFolderFilter')
    def encodeFolderFilter(self, REQUEST):
        """
            Parse cookie string for using variables in dtml.
        """
        filter = {}
        for key, value in REQUEST.items():
            if key[:10] == 'filter_by_':
                filter[key[10:]] = value
        encoded = string.strip(base64.encodestring( marshal.dumps( filter )))
        encoded = string.join(string.split(encoded, '\n'), '')
        return encoded

    security.declarePublic('decodeFolderFilter')
    def decodeFolderFilter(self, encoded):
        """
            Parse cookie string for using variables in dtml.
        """
        filter = {}
        if encoded:
            filter.update(marshal.loads(base64.decodestring(encoded)))
        return filter

    def content_type( self ):
        """
            WebDAV needs this to do the Right Thing (TM).
        """
        return None

    def PUT_factory( self, name, typ, body ):
        """
            Dispatcher for PUT requests to non-existent IDs.  Returns
            an object of the appropriate type (or None, if we don't
            know what to do).
        """
        registry = getToolByName( self, 'content_type_registry' )
        if registry is None:
            return None

        typeObjectName = registry.findTypeName( name, typ, body )
        if typeObjectName is None:
            return None
        
        self.invokeFactory( typeObjectName, name )

        # XXX: this is butt-ugly.
        obj = aq_base( self._getOb( name ) )
        self._delObject( name )
        return obj

    security.declareProtected(AddPortalContent, 'invokeFactory')
    def invokeFactory( self
                     , type_name
                     , id
                     , RESPONSE=None
                     , *args
                     , **kw
                     ):
        '''
        Invokes the portal_types tool.
        '''
        pt = getToolByName( self, 'portal_types' )
        apply( pt.constructContent
             , (type_name, self, id, RESPONSE) + args
             , kw
             )

    def _checkId(self, id, allow_dup=0):
        PortalFolder.inheritedAttribute('_checkId')(self, id, allow_dup)
        
        # This method prevents people other than the portal manager
        # from overriding skinned names.
        if not allow_dup:
            if not getSecurityManager().checkPermission(
                'Manage portal', self):
                ob = self
                while ob is not None and not getattr(ob, '_isPortalRoot', 0):
                    ob = aq_parent(aq_inner(ob))
                if ob is not None:
                    # If the portal root has an object by this name,
                    # don't allow an override.
                    # FIXME: needed to allow index_html for join code
                    if hasattr(ob, id) and id != 'index_html':
                        raise 'Bad Request', (
                            'The id "%s" is reserved.' % id)
                    # Otherwise we're ok.

    def _verifyObjectPaste(self, object, validate_src=1):
        # This assists the version in OFS.CopySupport.
        # It enables the clipboard to function correctly
        # with objects created by a multi-factory.
        if (hasattr(object, '__factory_meta_type__') and
            hasattr(self, 'all_meta_types')):
            mt = object.__factory_meta_type__
            method_name=None
            permission_name = None
            meta_types = self.all_meta_types
            if callable(meta_types): meta_types = meta_types()
            for d in meta_types:
                if d['name']==mt:
                    method_name=d['action']
                    permission_name = d.get('permission', None)
                    break

            if permission_name is not None:
                if getSecurityManager().checkPermission(permission_name,self):
                    if not validate_src:
                        # We don't want to check the object on the clipboard
                        return
                    try: parent = aq_parent(aq_inner(object))
                    except: parent = None
                    if getSecurityManager().validate(None, parent,
                                                     None, object):
                        # validation succeeded
                        return
                    raise 'Unauthorized', object.getId()
                else:
                    raise 'Unauthorized', permission_name
            #
            # Old validation for objects that may not have registered 
            # themselves in the proper fashion.
            #
            elif method_name is not None:
                meth=self.unrestrictedTraverse(method_name)
                if hasattr(meth, 'im_self'):
                    parent = meth.im_self
                else:
                    try:    parent = aq_parent(aq_inner(meth))
                    except: parent = None
                if getSecurityManager().validate(None, parent, None, meth):
                    # Ensure the user is allowed to access the object on the
                    # clipboard.
                    if not validate_src:
                        return
                    try: parent = aq_parent(aq_inner(object))
                    except: parent = None
                    if getSecurityManager().validate(None, parent,
                                                     None, object):
                        return
                    id = object.getId()
                    raise 'Unauthorized', id
                else:
                    raise 'Unauthorized', method_name
        PortalFolder.inheritedAttribute(
            '_verifyObjectPaste')(self, object, validate_src)

    security.setPermissionDefault(AddPortalContent, ('Owner','Manager'))
    security.setPermissionDefault(AddPortalFolders, ('Owner','Manager'))
    


class ContentFilter:
    """
        Represent a predicate against a content object's metadata.
    """
    MARKER = []
    filterSubject = filterType = []
    def __init__( self
                , Title=MARKER
                , Creator=MARKER
                , Subject=MARKER
                , Description=MARKER
                , created=MARKER
                , created_usage='range:min'
                , modified=MARKER
                , modified_usage='range:min'
                , Type=MARKER
                , **Ignored
                ):

        self.predicates = []

        if Title is not self.MARKER: 
            self.filterTitle = Title
            self.predicates.append( lambda x, pat=re( Title ):
                                      pat.search( x.Title() ) )

        if Creator is not self.MARKER: 
            self.predicates.append( lambda x, pat=re( Creator ):
                                      pat.search( x.Creator() ) )

        if Subject and Subject is not self.MARKER: 
            self.filterSubject = Subject
            self.predicates.append( self.hasSubject )

        if Description is not self.MARKER: 
            self.predicates.append( lambda x, pat=re( Description ):
                                      pat.search( x.Description() ) )

        if created is not self.MARKER: 
            if created_usage == 'range:min':
                self.predicates.append( lambda x, cd=created:
                                          cd <= x.created() )
            if created_usage == 'range:max':
                self.predicates.append( lambda x, cd=created:
                                          cd >= x.created() )

        if modified is not self.MARKER: 
            if modified_usage == 'range:min':
                self.predicates.append( lambda x, md=modified:
                                          md <= x.modified() )
            if modified_usage == 'range:max':
                self.predicates.append( lambda x, md=modified:
                                          md >= x.modified() )

        if Type:
            if type( Type ) == type( '' ):
                Type = [ Type ]
            self.filterType = Type
            self.predicates.append( lambda x, Type=Type:
                                      x.Type() in Type )

    def hasSubject( self, obj ):
        """
        Converts Subject string into a List for content filter view.
        """
        for sub in obj.Subject():
            if sub in self.filterSubject:
                return 1
        return 0

    def __call__( self, content ):

        for predicate in self.predicates:

            try:
                if not predicate( content ):
                    return 0
            except: # XXX
                return 0
        
        return 1

    def __str__( self ):
        """
        """
        return "Subject: %s; Type: %s" % ( self.filterSubject,
                                           self.filterType )

manage_addPortalFolder = PortalFolder.manage_addPortalFolder
manage_addPortalFolderForm = HTMLFile( 'folderAdd', globals() )

Globals.InitializeClass(PortalFolder)
