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
"""Customizable image objects that come from the filesystem."""
__version__='$Revision$'[11:-2]

import string, os

import Globals
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from webdav.common import rfc1123_date
from OFS.Image import Image, getImageInfo

from utils import _dtmldir
from CMFCorePermissions import ViewManagementScreens, View, FTPAccess
from FSObject import FSObject
from DirectoryView import registerFileExtension, registerMetaType, expandpath

class FSImage(FSObject):
    """FSImages act like images but are not directly
    modifiable from the management interface."""
    # Note that OFS.Image.Image is not a base class because it is mutable.

    meta_type = 'Filesystem Image'

    manage_options=(
        {'label':'Customize', 'action':'manage_main'},
        )

    security = ClassSecurityInfo()
    security.declareObjectProtected(View)

    def __init__(self, id, filepath, fullname=None, properties=None):
        id = fullname or id # Use the whole filename.
        FSObject.__init__(self, id, filepath, fullname, properties)

    security.declareProtected(ViewManagementScreens, 'manage_main')
    manage_main = Globals.DTMLFile('custimage', _dtmldir)
    content_type = 'unknown/unknown'

    def _createZODBClone(self):
        return Image(self.getId(), '', self._readFile(1))

    def _readFile(self, reparse):
        fp = expandpath(self._filepath)
        file = open(fp, 'rb')
        try: data = file.read()
        finally: file.close()
        if reparse or self.content_type == 'unknown/unknown':
            ct, width, height = getImageInfo( data )
            self.content_type = ct
            self.width = width
            self.height = height
        return data

    #### The following is mainly taken from OFS/Image.py ###
        
    __str__ = Image.__str__

    _image_tag = Image.tag
    security.declareProtected(View, 'tag')
    def tag(self, *args, **kw):
        # Hook into an opportunity to reload metadata.
        self._updateFromFS()
        return apply(self._image_tag, args, kw)

    security.declareProtected(View, 'index_html')
    def index_html(self, REQUEST, RESPONSE):
        """
        The default view of the contents of a File or Image.

        Returns the contents of the file or image.  Also, sets the
        Content-Type HTTP header to the objects content type.
        """
        self._updateFromFS()
        data = self._readFile(0)
        # HTTP If-Modified-Since header handling.
        header=REQUEST.get_header('If-Modified-Since', None)
        if header is not None:
            header=string.split(header, ';')[0]
            # Some proxies seem to send invalid date strings for this
            # header. If the date string is not valid, we ignore it
            # rather than raise an error to be generally consistent
            # with common servers such as Apache (which can usually
            # understand the screwy date string as a lucky side effect
            # of the way they parse it).
            try:    mod_since=long(DateTime(header).timeTime())
            except: mod_since=None
            if mod_since is not None:
                last_mod = self._file_mod_time
                if last_mod > 0 and last_mod <= mod_since:
                    # Set header values since apache caching will return
                    # Content-Length of 0 in response if size is not set here
                    RESPONSE.setHeader('Last-Modified', rfc1123_date(last_mod))
                    RESPONSE.setHeader('Content-Type', self.content_type)
                    RESPONSE.setHeader('Content-Length', self.get_size())
                    RESPONSE.setStatus(304)
                    return ''

        RESPONSE.setHeader('Last-Modified', rfc1123_date(self._file_mod_time))
        RESPONSE.setHeader('Content-Type', self.content_type)
        RESPONSE.setHeader('Content-Length', len(data))

        return data

    security.declareProtected(View, 'getContentType')
    def getContentType(self):
        """Get the content type of a file or image.

        Returns the content type (MIME type) of a file or image.
        """
        self._updateFromFS()
        return self.content_type

    security.declareProtected(FTPAccess, 'manage_FTPget')
    manage_FTPget = index_html

Globals.InitializeClass(FSImage)

registerFileExtension('gif', FSImage)
registerFileExtension('jpg', FSImage)
registerFileExtension('jpeg', FSImage)
registerFileExtension('png', FSImage)
registerMetaType('Image', FSImage)
