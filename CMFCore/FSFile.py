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
""" Customizable image objects that come from the filesystem.

$Id$
"""

import Globals
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from webdav.common import rfc1123_date
from OFS.Cache import Cacheable
from OFS.Image import File
from OFS.content_types import guess_content_type

from CMFCorePermissions import FTPAccess
from CMFCorePermissions import View
from CMFCorePermissions import ViewManagementScreens
from DirectoryView import registerFileExtension
from DirectoryView import registerMetaType
from FSObject import FSObject
from utils import _dtmldir
from utils import expandpath


class FSFile(FSObject):
    """FSFiles act like images but are not directly
    modifiable from the management interface."""
    # Note that OFS.Image.File is not a base class because it is mutable.

    meta_type = 'Filesystem File'

    manage_options=(
        {'label':'Customize', 'action':'manage_main'},
        ) + Cacheable.manage_options

    security = ClassSecurityInfo()
    security.declareObjectProtected(View)

    def __init__(self, id, filepath, fullname=None, properties=None):
        id = fullname or id # Use the whole filename.
        FSObject.__init__(self, id, filepath, fullname, properties)

    security.declareProtected(ViewManagementScreens, 'manage_main')
    manage_main = Globals.DTMLFile('custfile', _dtmldir)
    content_type = 'unknown/unknown'

    def _createZODBClone(self):
        return File(self.getId(), '', self._readFile(1))

    def _get_content_type(self, file, body, id, content_type=None):
        headers=getattr(file, 'headers', None)
        if headers and headers.has_key('content-type'):
            content_type=headers['content-type']
        else:
            if type(body) is not type(''): body=body.data
            content_type, enc=guess_content_type(
                getattr(file, 'filename',id), body, content_type)
        return content_type

    def _readFile(self, reparse):
        fp = expandpath(self._filepath)
        file = open(fp, 'rb')
        try: data = file.read()
        finally: file.close()
        if reparse or self.content_type == 'unknown/unknown':
            self.ZCacheable_invalidate()
            self.content_type=self._get_content_type(file, data, self.id)
        return data

    #### The following is mainly taken from OFS/File.py ###

    __str__ = File.__str__

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
            header = header.split(';')[0]
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

        self.ZCacheable_set(None)
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

Globals.InitializeClass(FSFile)

registerFileExtension('doc', FSFile)
registerFileExtension('pdf', FSFile)
registerFileExtension('swf', FSFile)
registerFileExtension('jar', FSFile)
registerFileExtension('cab', FSFile)
registerFileExtension('ico', FSFile)
registerFileExtension('js', FSFile)
registerFileExtension('css', FSFile)
registerMetaType('File', FSFile)
