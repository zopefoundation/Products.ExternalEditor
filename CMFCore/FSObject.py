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
"""Customizable objects that come from the filesystem (base class)."""
__version__='$Revision$'[11:-2]

from string import split
from os import path, stat

import Acquisition, Globals
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import Item
from DateTime import DateTime

from DirectoryView import expandpath
import CMFCorePermissions

class FSObject(Acquisition.Implicit, Item):
    """FSObject is a base class for all filesystem based look-alikes.
    
    Subclasses of this class mimic ZODB based objects like Image and
    DTMLMethod, but are not directly modifiable from the management
    interface. They provide means to create a TTW editable copy, however.
    """

    # Always empty for FS based, non-editable objects.
    title = ''

    security = ClassSecurityInfo()
    security.declareObjectProtected(CMFCorePermissions.View)

    _file_mod_time = 0

    def __init__(self, id, filepath, fullname=None, properties=None):
        if properties:
            # Since props come from the filesystem, this should be
            # safe.
            self.__dict__.update(properties)

        self.id = id
        self._filepath = filepath
        fp = expandpath(self._filepath)
        
        try: self._file_mod_time = stat(fp)[8]
        except: pass
        self._readFile()

    security.declareProtected(CMFCorePermissions.ViewManagementScreens,
        'manage_doCustomize')
    def manage_doCustomize(self, folder_path, RESPONSE=None):
        """Makes a ZODB Based clone with the same data.

        Calls _createZODBClone for the actual work.
        """

        obj = self._createZODBClone()
        
        id = obj.getId()
        fpath = tuple(split(folder_path, '/'))
        folder = self.restrictedTraverse(fpath)
        folder._verifyObjectPaste(obj, validate_src=0)
        folder._setObject(id, obj)

        if RESPONSE is not None:
            RESPONSE.redirect('%s/%s/manage_main' % (
                folder.absolute_url(), id))

    def _createZODBClone(self):
        """Create a ZODB (editable) equivalent of this object."""
        raise NotImplemented, "This should be implemented in a subclass."

    def _readFile(self):
        """Read the data from the filesystem.
        
        Read the file (indicated by exandpath(self._filepath), and parse the
        data if necessary.
        """
        raise NotImplemented, "This should be implemented in a subclass."

    # Refresh our contents from the filesystem if that is newer and we are
    # running in debug mode.
    def _updateFromFS(self):
        if Globals.DevelopmentMode:
            fp = expandpath(self._filepath)
            try:    mtime=stat(fp)[8]
            except: mtime=0
            if mtime != self._file_mod_time:
                self._file_mod_time = mtime
                self._readFile()

    security.declareProtected(CMFCorePermissions.View, 'get_size')
    def get_size(self):
        """Get the size of the underlying file."""
        fp = expandpath(self._filepath)
        return path.getsize(fp)

    security.declareProtected(CMFCorePermissions.View, 'getModTime')
    def getModTime(self):
        """Return the last_modified date of the file we represent.

        Returns a DateTime instance.
        """
        self._updateFromFS()
        return DateTime(self._file_mod_time)

    security.declareProtected(CMFCorePermissions.ViewManagementScreens,
        'getObjectFSPath')
    def getObjectFSPath(self):
        """Return the path of the file we represent"""
        self._updateFromFS()
        return self._filepath

Globals.InitializeClass(FSObject)
