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
""" Link instances represent explicit links-as-content.

$Id$
"""
__version__ = "$Revision$"[11:-2]

import string
import urlparse

from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.WorkflowCore import WorkflowAction
from Products.CMFCore.utils import keywordsplitter

from DublinCore import DefaultDublinCoreImpl
from utils import formatRFC822Headers, parseHeadersBody, _dtmldir

factory_type_information = ( { 'id'             : 'Link'
                             , 'meta_type'      : 'Link'
                             , 'description'    : """\
Link items are URLs that come with additional information."""
                             , 'icon'           : 'link_icon.gif'
                             , 'product'        : 'CMFDefault'
                             , 'factory'        : 'addLink'
                             , 'immediate_view' : 'metadata_edit_form'
                             , 'actions'        :
                                ( { 'id'            : 'view'
                                  , 'name'          : 'View'
                                  , 'action'        : 'link_view'
                                  , 'permissions'   : (
                                      CMFCorePermissions.View, )
                                  }
                                , { 'id'            : 'edit'
                                  , 'name'          : 'Edit'
                                  , 'action'        : 'link_edit_form'
                                  , 'permissions'   : (
                                      CMFCorePermissions.ModifyPortalContent, )
                                  }
                                , { 'id'            : 'metadata'
                                  , 'name'          : 'Metadata'
                                  , 'action'        : 'metadata_edit_form'
                                  , 'permissions'   : (
                                      CMFCorePermissions.ModifyPortalContent, )
                                  }
                                )
                             }
                           ,
                           )


def addLink( self
           , id
           , title=''
           , remote_url=''
           , description=''
           ):
    """
        Add a Link instance to 'self'.
    """
    o=Link( id, title, remote_url, description )
    self._setObject(id,o)


class Link( PortalContent
          , DefaultDublinCoreImpl
          ):
    """
        A Link
    """

    __implements__ = ( PortalContent.__implements__
                     , DefaultDublinCoreImpl.__implements__
                     )

    meta_type = 'Link'
    URL_FORMAT = format = 'text/url'
    effective_date = expiration_date = None
    _isDiscussable = 1

    security = ClassSecurityInfo()

    def __init__( self
                , id
                , title=''
                , remote_url=''
                , description=''
                ):
        DefaultDublinCoreImpl.__init__(self)
        self.id=id
        self.title=title
        self.remote_url=remote_url
        self.description=description

    security.declareProtected( CMFCorePermissions.ModifyPortalContent
                             , 'manage_edit' )
    manage_edit = DTMLFile( 'zmi_editLink', _dtmldir )

    security.declareProtected( CMFCorePermissions.ModifyPortalContent
                             , 'manage_editLink' )
    def manage_editLink( self, remote_url, REQUEST=None ):
        """
            Update the Link via the ZMI.
        """
        self._edit( remote_url )
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect( self.absolute_url()
                                        + '/manage_edit'
                                        + '?manage_tabs_message=Link+updated'
                                        )

    security.declarePrivate( '_edit' )
    def _edit( self, remote_url ):
        """
            Edit the Link
        """
        tokens = urlparse.urlparse( remote_url, 'http' )
        if tokens[0] and tokens[1]:
            self.remote_url = urlparse.urlunparse( tokens )
        else:
            self.remote_url = 'http://' + remote_url

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'edit' )
    edit = WorkflowAction( _edit )

    security.declareProtected( CMFCorePermissions.View, 'SearchableText' )
    def SearchableText(self):
        """
            text for indexing
        """
        return "%s %s" % (self.title, self.description)

    security.declareProtected( CMFCorePermissions.View, 'getRemoteUrl' )
    def getRemoteUrl(self):
        """
            returns the remote URL of the Link
        """
        return self.remote_url

    security.declarePrivate( '_writeFromPUT' )
    def _writeFromPUT( self, body ):

        headers = {}
        headers, body = parseHeadersBody(body, headers)
        lines = string.split( body, '\n' )
        self.edit( lines[0] )

        headers['Format'] = self.URL_FORMAT
        new_subject = keywordsplitter(headers)
        headers['Subject'] = new_subject or self.Subject()
        haveheader = headers.has_key
        for key, value in self.getMetadataHeaders():
            if key != 'Format' and not haveheader(key):
                headers[key] = value
        
        self.editMetadata(title=headers['Title'],
                          subject=headers['Subject'],
                          description=headers['Description'],
                          contributors=headers['Contributors'],
                          effective_date=headers['Effective_date'],
                          expiration_date=headers['Expiration_date'],
                          format=headers['Format'],
                          language=headers['Language'],
                          rights=headers['Rights'],
                          )
        
    ## FTP handlers
    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'PUT')
    def PUT(self, REQUEST, RESPONSE):
        """
            Handle HTTP / WebDAV / FTP PUT requests.
        """
        self.dav__init(REQUEST, RESPONSE)
        body = REQUEST.get('BODY', '')
        self._writeFromPUT( body )
        RESPONSE.setStatus(204)
        return RESPONSE

    security.declareProtected( CMFCorePermissions.View, 'manage_FTPget' )
    def manage_FTPget(self):
        """
            Get the link as text for WebDAV src / FTP download.
        """
        join = string.join
        lower = string.lower
        hdrlist = self.getMetadataHeaders()
        hdrtext = formatRFC822Headers( hdrlist )
        bodytext = '%s\n\n%s' % ( hdrtext, self.getRemoteUrl() )

        return bodytext

    security.declareProtected( CMFCorePermissions.View, 'get_size' )
    def get_size( self ):
        """
            Used for FTP and apparently the ZMI now too 
        """
        return len(self.manage_FTPget())

InitializeClass( Link )

