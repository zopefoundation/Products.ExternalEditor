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

import string, os

import Globals
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from webdav.common import rfc1123_date
from OFS.Image import Image, getImageInfo

from CMFCorePermissions import ViewManagementScreens, View
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
    manage_main = Globals.HTMLFile('dtml/custimage', globals())

    def _createZODBClone(self):
        return Image(self.getId(), '', self.read())

    def _readFile(self):
        fp = expandpath(self._filepath)
        file = open(fp, 'rb')
        try: data = file.read()
        finally: file.close()

        # Only parse out image info if the file was changed, because this file
        # is read every time the image is requested.
        try:    mtime=os.stat(fp)[8]
        except: mtime=-1
        if mtime != self._file_mod_time:
            self._file_mod_time = mtime
            (self.content_type, self.width, self.height) = getImageInfo(data)

        return data

    #### The following is mainly taken from OFS/Image.py ###
        
    __str__ = Image.__str__

    _image_tag = Image.tag
    security.declareProtected(View, 'tag')
    def tag(self, height=None, width=None, alt=None,
            scale=0, xscale=0, yscale=0, **args):
        # Hook into an oppertunity to reload metadata.
        self._readFile()
        return apply(self._image_tag, (height, width, alt, scale, xscale, 
            yscale), args)

    security.declareProtected(View, 'index_html')
    def index_html(self, REQUEST, RESPONSE):
        """
        The default view of the contents of a File or Image.

        Returns the contents of the file or image.  Also, sets the
        Content-Type HTTP header to the objects content type.
        """
        data = self._readFile()
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
        self._readFile()
        return self.content_type

Globals.InitializeClass(FSImage)

registerFileExtension('gif', FSImage)
registerFileExtension('jpg', FSImage)
registerFileExtension('jpeg', FSImage)
registerFileExtension('png', FSImage)
registerMetaType('Image', FSImage)
