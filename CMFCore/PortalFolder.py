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
"""PortalFolder: CMF-enabled Folder objects.
$Id$
"""

__version__='$Revision$'[11:-2]

ADD_FOLDERS_PERMISSION = 'Add portal folders'
ADD_CONTENT_PERMISSION = 'Add portal content'

import sys
import Globals, re, base64, marshal, string
import CMFCorePermissions

from CMFCorePermissions import View, ManageProperties, ListFolderContents
from CMFCorePermissions import AddPortalFolders, AddPortalContent
from OFS.Folder import Folder
from OFS.ObjectManager import REPLACEABLE
from Globals import DTMLFile
from AccessControl import getSecurityManager, ClassSecurityInfo
from Acquisition import aq_parent, aq_inner, aq_base
from DynamicType import DynamicType
from utils import getToolByName, _checkPermission

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
                                ( { 'id'            : 'view'
                                  , 'name'          : 'View'
                                  , 'action'        : ''
                                  , 'permissions'   : (View,)
                                  , 'category'      : 'folder'
                                  }
                                , { 'id'            : 'edit'
                                  , 'name'          : 'Edit'
                                  , 'action'        : 'folder_edit_form'
                                  , 'permissions'   : (ManageProperties,)
                                  , 'category'      : 'folder'
                                  }
                                , { 'id'            : 'localroles'
                                  , 'name'          : 'Local Roles'
                                  , 'action'        : 'folder_localrole_form'
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

    security.declareProtected( CMFCorePermissions.ManageProperties
                             , 'setTitle')
    def setTitle( self, title ):
        """
            Edit the folder title.
        """
        self.title = title

    security.declareProtected( CMFCorePermissions.ManageProperties
                             , 'setDescription')
    def setDescription( self, description ):
        """
            Edit the folder description.
        """
        self.description = description

    security.declareProtected(CMFCorePermissions.ManageProperties, 'edit')
    def edit(self, title='', description=''):
        """
        Edit the folder title (and possibly other attributes later)
        """
        self.setTitle( title )
        self.setDescription( description )

    security.declarePublic('allowedContentTypes')
    def allowedContentTypes( self ):
        """
            List type info objects for types which can be added in
            this folder.
        """
        result = []
        portal_types = getToolByName(self, 'portal_types')
        myType = portal_types.getTypeInfo(self)

        if myType is not None:
            for contentType in portal_types.listTypeInfo(self):
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
            return self.folder_contents( # XXX: ick!
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
        types = types_tool.listContentTypes( by_metatype=1 )
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
        for id in ids:
            obj = get( id )
            include = 0
            if query(obj):
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

    security.declareProtected( ListFolderContents
                             , 'listFolderContents' )
    def listFolderContents( self, spec=None, contentFilter=None ): # XXX
        """
            Hook around 'contentValues' to let 'folder_contents'
            be protected.  Duplicating skip_unauthorized behavior of dtml-in.
        """
        items = self.contentValues(filter=contentFilter)
        l = []
        for obj in items:
            id = obj.getId()
            v = obj
            try: 
                if getSecurityManager().validate(self, self, id, v):
                    l.append(obj)
            except "Unauthorized":
                pass
        return l


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
        portal_types = getToolByName(self, 'portal_types')
        ti = portal_types.getTypeInfo(self)
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

    security.declareProtected(AddPortalContent, 'checkIdAvailable')
    def checkIdAvailable(self, id):
        try:
            self._checkId(id)
        except:
            if sys.exc_info()[0] == 'Bad Request':
                return 0
            raise  # Some other exception.
        else:
            return 1

    def MKCOL_handler(self,id,REQUEST=None,RESPONSE=None):
        """
            Handle WebDAV MKCOL.
        """
        self.manage_addFolder( id=id, title='' )

    def _checkId(self, id, allow_dup=0):
        PortalFolder.inheritedAttribute('_checkId')(self, id, allow_dup)
        
        # This method prevents people other than the portal manager
        # from overriding skinned names.
        if not allow_dup:
            if not _checkPermission( 'Manage portal', self):
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
                if _checkPermission(permission_name,self):
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

    def manage_addFolder( self
                        , id
                        , title=''
                        , REQUEST=None
                        ):
        """
            Add a new folder-like object with id *id*.  IF present,
            use the parent object's 'mkdir' action;  otherwise, just
            add a PortalFolder.
            to take control of the process by checking for a 'mkdir'
            action.
        """
        try:
            action = self.getTypeInfo().getActionById( 'mkdir' )
        except TypeError:
            self.invokeFactory( type_name='Folder', id=id )
        else:
            # call it
            getattr( self, action )( id=id )

        ob = self._getOb( id )
        ob.setTitle( title )
        try:
            ob.reindexObject()
        except AttributeError:
            pass

        if REQUEST is not None:
            return self.manage_main(self, REQUEST, update_menu=1)

Globals.InitializeClass(PortalFolder)
    


class ContentFilter:
    """
        Represent a predicate against a content object's metadata.
    """
    MARKER = []
    filterSubject = []
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
        self.description = []

        if Title is not self.MARKER: 
            self.filterTitle = Title
            self.predicates.append( lambda x, pat=re.compile( Title ):
                                      pat.search( x.Title() ) )
            self.description.append( 'Title: %s' % Title )

        if Creator is not self.MARKER: 
            self.predicates.append( lambda x, pat=re.compile( Creator ):
                                      pat.search( x.Creator() ) )
            self.description.append( 'Creator: %s' % Creator )

        if Subject and Subject is not self.MARKER: 
            self.filterSubject = Subject
            self.predicates.append( self.hasSubject )
            self.description.append( 'Subject: %s'
                                   % string.join( Subject, ', ' ) )

        if Description is not self.MARKER: 
            self.predicates.append( lambda x, pat=re.compile( Description ):
                                      pat.search( x.Description() ) )
            self.description.append( 'Description: %s' % Description )

        if created is not self.MARKER: 
            if created_usage == 'range:min':
                self.predicates.append( lambda x, cd=created:
                                          cd <= x.created() )
                self.description.append( 'Created since: %s' % created )
            if created_usage == 'range:max':
                self.predicates.append( lambda x, cd=created:
                                          cd >= x.created() )
                self.description.append( 'Created before: %s' % created )

        if modified is not self.MARKER: 
            if modified_usage == 'range:min':
                self.predicates.append( lambda x, md=modified:
                                          md <= x.modified() )
                self.description.append( 'Modified since: %s' % modified )
            if modified_usage == 'range:max':
                self.predicates.append( lambda x, md=modified:
                                          md >= x.modified() )
                self.description.append( 'Modified before: %s' % modified )

        if Type:
            if type( Type ) == type( '' ):
                Type = [ Type ]
            self.predicates.append( lambda x, Type=Type:
                                      x.Type() in Type )
            self.description.append( 'Type: %s'
                                   % string.join( Type, ', ' ) )

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
            except: # predicates are *not* allowed to throw exceptions
                return 0
        
        return 1

    def __str__( self ):
        """
            Return a stringified description of the filter.
        """
        return string.join( self.description, '; ' )

manage_addPortalFolder = PortalFolder.manage_addPortalFolder
manage_addPortalFolderForm = DTMLFile( 'folderAdd', globals() )
