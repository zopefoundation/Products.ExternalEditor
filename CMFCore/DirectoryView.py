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
"""Views of filesystem directories as folders."""
__version__='$Revision$'[11:-2]


import Globals
from Globals import HTMLFile, Persistent, package_home, DTMLFile
import os
from os import path, listdir, stat
from Acquisition import aq_inner, aq_parent, aq_base
from string import split, rfind, strip, join
from App.Common import package_home
from OFS.ObjectManager import bad_id
from OFS.Folder import Folder
from AccessControl import ClassSecurityInfo
from CMFCorePermissions import AccessContentsInformation, ManagePortal
import CMFCorePermissions
from FSObject import BadFile
from utils import expandpath, minimalpath

_dtmldir = os.path.join( package_home( globals() ), 'dtml' )

__reload_module__ = 0

class DirectoryInformation:
    data = None
    _v_last_read = 0

    def __init__(self, expanded_fp, minimal_fp):
        self.filepath = minimal_fp
        l = listdir(expanded_fp)
        subdirs = []
        for entry in l:
            if entry in ('CVS', 'SVN', '.', '..'):
                # Ignore version control subdirectories
                # and special names.
                continue
            e_fp = path.join(expanded_fp, entry)
            if path.isdir(e_fp):
                subdirs.append(entry)
        self.subdirs = tuple(subdirs)

    def getSubdirs(self):
        return self.subdirs

    def _isAllowableFilename(self, entry):
        if entry[-1:] == '~':
            return 0
        if entry[:1] in ('_', '#'):
            return 0
        return 1

    def reload(self):
        self.data = None

    def _readTypesFile(self):
        '''
        Reads the .objects file produced by FSDump.
        '''
        types = {}
        fp = expandpath(self.filepath)
        try: f = open(path.join(fp, '.objects'), 'rt')
        except: pass
        else:
            lines = f.readlines()
            f.close()
            for line in lines:
                try: obname, meta_type = split(line, ':')
                except: pass
                else:
                    types[strip(obname)] = strip(meta_type)
        return types

    def getContents(self, registry):
        changed = 0
        if Globals.DevelopmentMode:
            try: mtime = stat(expandpath(self.filepath))[8]
            except: mtime = 0
            if mtime != self._v_last_read:
                self._v_last_read = mtime
                changed = 1

        if self.data is None or changed:
            try:
                self.data, self.objects = self.prepareContents(registry,
                    register_subdirs=changed)
            except:
                from zLOG import LOG, ERROR
                import sys, traceback
                type,value,tb = sys.exc_info()
                try:
                    LOG( 'DirectoryView'
                    , ERROR
                    , 'Error during prepareContents:'
                    , traceback.format_exception( type, value, tb )
                    )
                finally:
                    tb = None       # Avoid leaking frame
                self.data = {}
                self.objects = ()
                    
        return self.data, self.objects

    def prepareContents(self, registry, register_subdirs=0):
        # Creates objects for each file.
        fp = expandpath(self.filepath)
        data = {}
        objects = []
        l = listdir(fp)
        types = self._readTypesFile()
        for entry in l:
            if not self._isAllowableFilename(entry):
                continue
            e_filepath = path.join(self.filepath, entry)
            e_fp = expandpath(e_filepath)
            if path.isdir(e_fp):
                # Add a subdirectory only if it was previously registered,
                # unless register_subdirs is set.
                info = registry.getDirectoryInfo(e_filepath)
                if info is None and register_subdirs:
                    # Register unknown subdirs
                    if entry not in ('CVS', 'SVN', '.', '..'):
                        registry.registerDirectoryByPath(e_fp)
                        info = registry.getDirectoryInfo(e_filepath)
                if info is not None:
                    mt = types.get(entry)
                    t = None
                    if mt is not None:
                        t = registry.getTypeByMetaType(mt)
                    if t is None:
                        t = DirectoryView
                    ob = t(entry, e_filepath)
                    ob_id = ob.getId()
                    data[ob_id] = ob
                    objects.append({'id': ob_id, 'meta_type': ob.meta_type})
            else:
                pos = rfind(entry, '.')
                if pos >= 0:
                    name = entry[:pos]
                    ext = path.normcase(entry[pos + 1:])
                else:
                    name = entry
                    ext = ''
                if not name or name == 'REQUEST':
                    # Not an allowable id.
                    continue
                mo = bad_id(name)
                if mo is not None and mo != -1:  # Both re and regex formats
                    # Not an allowable id.
                    continue
                t = None
                mt = types.get(entry, None)
                if mt is None:
                    mt = types.get(name, None)
                if mt is not None:
                    t = registry.getTypeByMetaType(mt)
                if t is None:
                    t = registry.getTypeByExtension(ext)
                if t is not None:
                    try:
                        ob = t(name, e_filepath, fullname=entry)
                    except:
                        from zLOG import LOG, ERROR
                        import sys, traceback
                        typ, val, tb = sys.exc_info()
                        try:
                            exc_lines = traceback.format_exception( typ
                                                                  , val
                                                                  , tb )
                            LOG( 'DirectoryView', ERROR
                               , join( exc_lines, '\n' ) )
                            ob = BadFile( name
                                        , e_filepath
                                        , exc_str=join( exc_lines, '\r\n' )
                                        , fullname=entry
                                        )
                        finally:
                            tb = None   # Avoid leaking frame!
                    ob_id = ob.getId()
                    data[ob_id] = ob
                    objects.append({'id': ob_id, 'meta_type': ob.meta_type})
        return data, tuple(objects)


class DirectoryRegistry:

    def __init__(self):
        self._meta_types = {}
        self._object_types = {}
        self._directories = {}
    
    def registerFileExtension(self, ext, klass):
        self._object_types[ext] = klass

    def registerMetaType(self, mt, klass):
        self._meta_types[mt] = klass

    def getTypeByExtension(self, ext):
        return self._object_types.get(ext, None)

    def getTypeByMetaType(self, mt):
        return self._meta_types.get(mt, None)

    def registerDirectory(self, name, parent_globals, subdirs=1):
        filepath = path.join(package_home(parent_globals), name)
        self.registerDirectoryByPath(filepath, subdirs)

    def registerDirectoryByPath(self, filepath, subdirs=1):
        fp = minimalpath(filepath)
        self._directories[fp] = di = DirectoryInformation(filepath, fp)
        if subdirs:
            for entry in di.getSubdirs():
                e_filepath = path.join(filepath, entry)
                self.registerDirectoryByPath(e_filepath, subdirs)

    def reloadDirectory(self, filepath):
        info = self.getDirectoryInfo(filepath)
        if info is not None:
            info.reload()

    def getDirectoryInfo(self, filepath):
        # Can return None.
        return self._directories.get(filepath, None)

    def listDirectories(self):
        dirs = self._directories.keys()
        dirs.sort()
        return dirs
        

_dirreg = DirectoryRegistry()
registerDirectory = _dirreg.registerDirectory
registerFileExtension = _dirreg.registerFileExtension
registerMetaType = _dirreg.registerMetaType


def listFolderHierarchy(ob, path, rval, adding_meta_type=None):
    if not hasattr(ob, 'objectValues'):
        return
    values = ob.objectValues()
    for subob in ob.objectValues():
        base = getattr(subob, 'aq_base', subob)
        if getattr(base, 'isPrincipiaFolderish', 0):

            if adding_meta_type is not None and hasattr(
                base, 'filtered_meta_types'):
                # Include only if the user is allowed to
                # add the given meta type in this location.
                meta_types = subob.filtered_meta_types()
                found = 0
                for mt in meta_types:
                    if mt['name'] == adding_meta_type:
                        found = 1
                        break
                if not found:
                    continue

            if path:
                subpath = path + '/' + subob.getId()
            else:
                subpath = subob.getId()
            title = getattr(subob, 'title', None)
            if title:
                name = '%s (%s)' % (subpath, title)
            else:
                name = subpath
            rval.append((subpath, name))
            listFolderHierarchy(subob, subpath, rval, adding_meta_type)


class DirectoryView (Persistent):
    '''
    '''
    meta_type = 'Filesystem Directory View'
    _dirpath = None
    _objects = ()

    def __init__(self, id, dirpath, fullname=None):
        self.id = id
        self._dirpath = dirpath

    def __of__(self, parent):
        info = _dirreg.getDirectoryInfo(self._dirpath)
        if info is not None:
            info = info.getContents(_dirreg)
        if info is None:
            data = {}
            objects = ()
        else:
            data, objects = info
        s = DirectoryViewSurrogate(self, data, objects)
        res = s.__of__(parent)
        return res

    def getId(self):
        return self.id

Globals.InitializeClass(DirectoryView)


class DirectoryViewSurrogate (Folder):

    meta_type = 'Filesystem Directory View'
    all_meta_types = ()
    _isDirectoryView = 1

    security = ClassSecurityInfo()

    def __init__(self, real, data, objects):
        d = self.__dict__
        d.update(data)
        d.update(real.__dict__)
        d['_real'] = real
        d['_objects'] = objects

    def __setattr__(self, name, value):
        d = self.__dict__
        d[name] = value
        setattr(d['_real'], name, value)

    security.declareProtected(ManagePortal,
                              'manage_propertiesForm')
    manage_propertiesForm = DTMLFile( 'dirview_properties', _dtmldir )

    security.declareProtected(ManagePortal,
                              'manage_properties')
    def manage_properties( self, dirpath, REQUEST ):
        """
            Update the directory path of the DV.
        """
        self.__dict__['_real']._dirpath = dirpath
        REQUEST['RESPONSE'].redirect( '%s/manage_propertiesForm'
                                    % self.absolute_url() )
    
    security.declareProtected(AccessContentsInformation,
                              'getCustomizableObject')
    def getCustomizableObject(self):
        ob = aq_parent(aq_inner(self))
        while getattr(ob, '_isDirectoryView', 0):
            ob = aq_parent(aq_inner(ob))
        return ob

    security.declareProtected(AccessContentsInformation,
                              'listCustFolderPaths')
    def listCustFolderPaths(self, adding_meta_type=None):
        '''
        Returns a list of possible customization folders
        as key, value pairs.
        '''
        rval = []
        ob = self.getCustomizableObject()
        listFolderHierarchy(ob, '', rval, adding_meta_type)
        rval.sort()
        return rval

    security.declareProtected(AccessContentsInformation,
                             'getDirPath')
    def getDirPath(self):
        return self.__dict__['_real']._dirpath

    security.declarePublic('getId')
    def getId(self):
        return self.id
    
Globals.InitializeClass(DirectoryViewSurrogate)


manage_addDirectoryViewForm = HTMLFile('dtml/addFSDirView', globals())

def createDirectoryView(parent, filepath, id=None):
    '''
    Adds either a DirectoryView or a derivative object.
    '''
    info = _dirreg.getDirectoryInfo(filepath)
    if dir is None:
        raise ValueError('Not a registered directory: %s' % filepath)
    if not id:
        id = path.split(filepath)[-1]
    else:
        id = str(id)
    ob = DirectoryView(id, filepath)
    parent._setObject(id, ob)

def addDirectoryViews(ob, name, parent_globals):
    '''
    Adds a directory view for every subdirectory of the
    given directory.
    '''
    # Meant to be called by filesystem-based code.
    # Note that registerDirectory() still needs to be called
    # by product initialization code to satisfy
    # persistence demands.
    fp = path.join(package_home(parent_globals), name)
    filepath = minimalpath(fp)
    info = _dirreg.getDirectoryInfo(filepath)
    if info is None:
        raise ValueError('Not a registered directory: %s' % filepath)
    for entry in info.getSubdirs():
        filepath2 = path.join(filepath, entry)
        createDirectoryView(ob, filepath2, entry)

def manage_addDirectoryView(self, filepath, id=None, REQUEST=None):
    '''
    Adds either a DirectoryView or a derivative object.
    '''
    createDirectoryView(self, filepath, id)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)

def manage_listAvailableDirectories(*args):
    '''
    '''
    return list(_dirreg.listDirectories())

