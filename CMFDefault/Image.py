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
 
"""
This module implements a portal-managed Image class.  It is based on
Zope's built-in Image object.
"""

ADD_CONTENT_PERMISSION = 'Add portal content'


from Globals import HTMLFile, HTML
from Products.CMFCore.PortalContent import PortalContent
import Globals
from DublinCore import DefaultDublinCoreImpl

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.WorkflowCore import WorkflowAction

factory_type_information = ( { 'id'             : 'Image'
                             , 'meta_type'      : 'Portal Image'
                             , 'description'    : """\
Image objects can be embedded in Portal documents."""
                             , 'icon'           : 'image_icon.gif'
                             , 'product'        : 'CMFDefault'
                             , 'factory'        : 'addImage'
                             , 'immediate_view' : 'metadata_edit_form'
                             , 'actions'        :
                                ( { 'name'          : 'View'
                                  , 'action'        : 'image_view'
                                  , 'permissions'   : (
                                      CMFCorePermissions.View, )
                                  }
                                , { 'name'          : 'Edit'
                                  , 'action'        : 'image_edit_form'
                                  , 'permissions'   : (
                                      CMFCorePermissions.ModifyPortalContent, )
                                  }
                                , { 'name'          : 'Metadata'
                                  , 'action'        : 'metadata_edit_form'
                                  , 'permissions'   : (
                                      CMFCorePermissions.ModifyPortalContent, )
                                  }
                                )
                             }
                           ,
                           )

import OFS.Image

def addImage( self
            , id
            , title=''
            , file=''
            , content_type=''
            , precondition=''
            , subject=()
            , description=''
            , contributors=()
            , effective_date=None
            , expiration_date=None
            , format='image/png'
            , language=''
            , rights=''
            ):
    """
        Add an Image
    """

    # cookId sets the id and title if they are not explicity specified
    id, title = OFS.Image.cookId(id, title, file)

    self=self.this()

    # Instantiate the object and set its description.
    iobj = Image( id, title, '', content_type, precondition, subject
                , description, contributors, effective_date, expiration_date
                , format, language, rights
                )
    
    # Add the Image instance to self
    self._setObject(id, iobj)

    # 'Upload' the image.  This is done now rather than in the
    # constructor because it's faster (see File.py.)
    self._getOb(id).manage_upload(file)


class Image( OFS.Image.Image
           , PortalContent
           , DefaultDublinCoreImpl
           ):
    """
        A Portal-managed Image
    """

    # The order of base classes is very significant in this case.
    # Image.Image does not store it's id in it's 'id' attribute.
    # Rather, it has an 'id' method which returns the contents of the
    # instnace's __name__ attribute.  Inheriting in the other order
    # obscures this method, resulting in much pulling of hair and
    # gnashing of teeth and fraying of nerves.  Don't do it.
    #
    # Really.
    # 
    # Note that if you use getId() to retrieve an object's ID, you will avoid
    # this problem altogether. getId is the new way, accessing .id is
    # deprecated.

    __implements__ = ( PortalContent.__implements__
                     , DefaultDublinCoreImpl.__implements__
                     )
    
    meta_type='Portal Image'
    effective_date = expiration_date = None
    _isDiscussable = 1
    icon = PortalContent.icon

    __ac_permissions__ = (
        (CMFCorePermissions.ModifyPortalContent, ('edit',)),
        )
    
    def __init__( self
                , id
                , title=''
                , file=''
                , content_type=''
                , precondition=''
                , subject=()
                , description=''
                , contributors=()
                , effective_date=None
                , expiration_date=None
                , format='image/png'
                , language='en-US'
                , rights=''
                ):
        OFS.Image.File.__init__( self, id, title, file
                               , content_type, precondition )
        DefaultDublinCoreImpl.__init__( self, title, subject, description
                               , contributors, effective_date, expiration_date
                               , format, language, rights )
    
    def SearchableText(self):
        """
            SeachableText is used for full text seraches of a portal.
            It should return a concatanation of all useful text.
        """
        return "%s %s" % (self.title, self.description)

    def manage_afterAdd(self, item, container):
        """Both of my parents have an afterAdd method"""
        OFS.Image.Image.manage_afterAdd(self, item, container)
        PortalContent.manage_afterAdd(self, item, container)

    def manage_beforeDelete(self, item, container):
        """Both of my parents have a beforeDelete method"""
        PortalContent.manage_beforeDelete(self, item, container)
        OFS.Image.Image.manage_beforeDelete(self, item, container)
        
    def _isNotEmpty(self, file):
        """ Do various checks on 'file' to try to determine non emptiness. """
        if not file:
            return 0                    # Catches None, Missing.Value, ''
        elif file and (type(file) is type('')):
            return 1
        elif getattr(file, 'filename', None):
            return 1
        elif not hasattr(file, 'read'):
            return 0
        else:
            file.seek(0,2)              # 0 bytes back from end of file
            t = file.tell()             # Report the location
            file.seek(0)                # and return pointer back to 0
            if t: return 1
            else: return 0

    def edit(self, precondition='', file=''):
        """ Update image. """
        if precondition: self.precondition = precondition
        elif self.precondition: del self.precondition

        if self._isNotEmpty(file):
            self.manage_upload(file)

        self.setFormat(self.content_type)
    edit = WorkflowAction(edit)

    def index_html(self, REQUEST, RESPONSE):
        """
        Display the image, with or without standard_html_[header|footer],
        as appropriate.
        """
        #if REQUEST['PATH_INFO'][-10:] == 'index_html':
        #    return self.view(self, REQUEST)
        return OFS.Image.Image.index_html(self, REQUEST, RESPONSE)

Globals.default__class_init__(Image)


