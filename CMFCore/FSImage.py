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
"""Customizable image objects that come from the filesystem."""
__version__='$Revision$'[11:-2]

import Globals
from Globals import HTMLFile
from DateTime import DateTime
import string
from os import path, stat
import Acquisition
from OFS.SimpleItem import Item_w__name__
import DirectoryView
from string import split
from OFS.Image import Image
import struct
from cStringIO import StringIO
from DirectoryView import registerFileExtension, registerMetaType, expandpath
from webdav.common import rfc1123_date
from AccessControl import ClassSecurityInfo
from CMFCorePermissions import ViewManagementScreens, View
import CMFCorePermissions

def getImageInfo(data):
    # This function ought to be in OFS/Image.py or perhaps even
    # in the Python library, but alas it is not as of January 2001.
    data = str(data)
    size = len(data)
    height = -1
    width = -1
    content_type = ''

    # handle GIFs   
    if (size >= 10) and data[:6] in ('GIF87a', 'GIF89a'):
        # Check to see if content_type is correct
        content_type = 'image/gif'
        w, h = struct.unpack("<HH", data[6:10])
        width = int(w)
        height = int(h)

    # See PNG v1.2 spec (http://www.cdrom.com/pub/png/spec/)
    # Bytes 0-7 are below, 4-byte chunk length, then 'IHDR'
    # and finally the 4-byte width, height
    elif ((size >= 24) and (data[:8] == '\211PNG\r\n\032\n')
          and (data[12:16] == 'IHDR')):
        content_type = 'image/png'
        w, h = struct.unpack(">LL", data[16:24])
        width = int(w)
        height = int(h)
            
    # Maybe this is for an older PNG version.
    elif (size >= 16) and (data[:8] == '\211PNG\r\n\032\n'):
        # Check to see if we have the right content type
        content_type = 'image/png'
        w, h = struct.unpack(">LL", data[8:16])
        width = int(w)
        height = int(h)

    # handle JPEGs
    elif (size >= 2) and (data[:2] == '\377\330'):
        content_type = 'image/jpeg'
        jpeg = StringIO(data)
        jpeg.read(2)
        b = jpeg.read(1)
        try:
            while (b and ord(b) != 0xDA):
                while (ord(b) != 0xFF): b = jpeg.read(1)
                while (ord(b) == 0xFF): b = jpeg.read(1)
                if (ord(b) >= 0xC0 and ord(b) <= 0xC3):
                    jpeg.read(3)
                    h, w = struct.unpack(">HH", jpeg.read(4))
                    break
                else:
                    jpeg.read(int(struct.unpack(">H", jpeg.read(2))[0])-2)
                b = jpeg.read(1)
            width = int(w)
            height = int(h)
        except: pass

    return content_type, width, height


class FSImage (Acquisition.Implicit, Item_w__name__):
    """FSImages act like images but are not directly
    modifiable from the management interface."""
    # Note that OFS.Image.Image is not a base class because it is mutable.

    meta_type = 'Filesystem Image'
    title = ''

    manage_options=(
        {'label':'Customize', 'action':'manage_main'},
        #{'label':'View', 'action':'view_image_or_file'},
        )

    security = ClassSecurityInfo()
    security.declareObjectProtected(CMFCorePermissions.View)

    file_mod_time = 0

    def __init__(self, id, filepath, fullname=None, properties=None):
        if properties:
            # Since props come from the filesystem, this should be
            # safe.
            self.__dict__.update(properties)
        self.__name__ = fullname or id  # Use the whole filename.
        self.title = ''
        self._filepath = filepath
        fp = expandpath(self._filepath)
        try: self.file_mod_time = stat(fp)[8]
        except: pass
        self._readFile()

    security.declareProtected(ViewManagementScreens, 'manage_main')
    manage_main = HTMLFile('dtml/custimage', globals())

    security.declareProtected(ViewManagementScreens, 'manage_doCustomize')
    def manage_doCustomize(self, folder_path, data=None, RESPONSE=None):
        '''
        Makes an Image with the same data.
        '''
        custFolder = self.getCustomizableObject()
        fpath = tuple(split(folder_path, '/'))
        folder = self.restrictedTraverse(fpath)
        if data is None:
            data = self._readFile()
        id = self.id()
        obj = Image(id, '', data)
        folder._verifyObjectPaste(obj, validate_src=0)
        folder._setObject(id, obj)
        if RESPONSE is not None:
            RESPONSE.redirect('%s/%s/manage_main' % (
                folder.absolute_url(), id))

    security.declareProtected(View, 'getImageFSPath')
    def getImageFSPath(self):
        '''
        '''
        return self._filepath

    def _readFile(self):
        fp = expandpath(self._filepath)
        file = open(fp, 'rb')
        try: data = file.read()
        finally: file.close()
        (self.content_type, self.width, self.height) = getImageInfo(data)
        return data

    def _updateFromFS(self):
        if Globals.DevelopmentMode:
            fp = expandpath(self._filepath)
            try:    mtime=stat(fp)[8]
            except: mtime=0
            if mtime != self.file_mod_time:
                self.file_mod_time = mtime
                self._readFile()

    def getId(self):
        return self.__name__

    #### The following is mainly taken from OFS/Image.py ###
        
    def __str__(self):
        return self.tag()

    security.declareProtected(View, 'tag')
    def tag(self, height=None, width=None, alt=None,
            scale=0, xscale=0, yscale=0, **args):
        """
        Generate an HTML IMG tag for this image, with customization.
        Arguments to self.tag() can be any valid attributes of an IMG tag.
        'src' will always be an absolute pathname, to prevent redundant
        downloading of images. Defaults are applied intelligently for
        'height', 'width', and 'alt'. If specified, the 'scale', 'xscale',
        and 'yscale' keyword arguments will be used to automatically adjust
        the output height and width values of the image tag.
        """
        self._updateFromFS()
        if height is None: height=self.height
        if width is None:  width=self.width

        # Auto-scaling support
        xdelta = xscale or scale
        ydelta = yscale or scale

        if xdelta and width:
            width = str(int(width) * xdelta)
        if ydelta and height:
            height = str(int(height) * ydelta)

        result='<img src="%s"' % (self.absolute_url())

        if alt is None:
            alt=getattr(self, 'title', '')
        result = '%s alt="%s"' % (result, alt)

        if height:
            result = '%s height="%s"' % (result, height)

        if width:
            result = '%s width="%s"' % (result, width)

        if not 'border' in map(string.lower, args.keys()):
            result = '%s border="0"' % result

        for key in args.keys():
            value = args.get(key)
            result = '%s %s="%s"' % (result, key, value)

        return '%s />' % result

    def id(self):
        return self.__name__

    security.declareProtected(View, 'index_html')
    def index_html(self, REQUEST, RESPONSE):
        """
        The default view of the contents of a File or Image.

        Returns the contents of the file or image.  Also, sets the
        Content-Type HTTP header to the objects content type.
        """
        # HTTP If-Modified-Since header handling.
        data = self._readFile()
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
                last_mod = self.file_mod_time
                if last_mod > 0 and last_mod <= mod_since:
                    RESPONSE.setStatus(304)
                    return ''

        RESPONSE.setHeader('Last-Modified', rfc1123_date(self.file_mod_time))
        RESPONSE.setHeader('Content-Type', self.content_type)
        RESPONSE.setHeader('Content-Length', len(data))

        return data

    security.declareProtected(View, 'view_image_or_file')
    def view_image_or_file(self, URL1):
        """
        The default view of the contents of the File or Image.
        """
        raise 'Redirect', URL1

    security.declareProtected(View, 'get_size')
    def get_size(self):
        """Get the size of a file or image.

        Returns the size of the file or image.
        """
        fp = expandpath(self._filepath)
        return path.getsize(fp)

    security.declareProtected(View, 'getContentType')
    def getContentType(self):
        """Get the content type of a file or image.

        Returns the content type (MIME type) of a file or image.
        """
        self._updateFromFS()
        return self.content_type

    security.declareProtected(View, 'getModTime')
    def getModTime(self):
        '''
        '''
        self._updateFromFS()
        return DateTime(self.file_mod_time)

    security.declareProtected(View, 'manage_FTPget')
    manage_FTPget = index_html

Globals.InitializeClass(FSImage)

registerFileExtension('gif', FSImage)
registerFileExtension('jpg', FSImage)
registerFileExtension('jpeg', FSImage)
registerFileExtension('png', FSImage)
registerMetaType('Image', FSImage)
