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
from Globals import HTMLFile, Persistent
import os
from os import path
from os import listdir
from Acquisition import aq_inner, aq_parent, aq_base
from string import split, rfind, strip
from App.Common import package_home
from OFS.ObjectManager import bad_id
from OFS.Folder import Folder
from AccessControl import ClassSecurityInfo
from CMFCorePermissions import AccessContentsInformation
import CMFCorePermissions

__reload_module__ = 0

normalize = path.normcase

normINSTANCE_HOME = normalize(INSTANCE_HOME)
normSOFTWARE_HOME = normalize(SOFTWARE_HOME)

separators = (os.sep, os.altsep)

def expandpath(p):
    # Converts a minimal path to an absolute path.
    if path.isabs(p):
        return p
    abs = path.join(INSTANCE_HOME, p)
    if path.exists(abs):
        return abs
    return path.join(SOFTWARE_HOME, p)

def minimalpath(p):
    # Trims INSTANCE_HOME or SOFTWARE_HOME from a path.
    p = path.abspath(p)
    abs = normalize(p)
    l = len(normINSTANCE_HOME)
    if abs[:l] != normINSTANCE_HOME:
        l = len(normSOFTWARE_HOME)
        if abs[:l] != normSOFTWARE_HOME:
            # Can't minimize.
            return p
    p = p[l:]
    while p[:1] in separators:
        p = p[1:]
    return p


class DirectoryInformation:
    data = None

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
        data = self.data
        if data is not None:
            return data
        try:
            self.data = data = self.prepareContents(registry)
        except:
            # DEBUG
            import traceback
            traceback.print_exc()

            self.data = data = {}
        return data

    def prepareContents(self, registry):
        # Creates objects for each file.
        fp = expandpath(self.filepath)
        data = {}
        l = listdir(fp)
        types = self._readTypesFile()
        for entry in l:
            if not self._isAllowableFilename(entry):
                continue
            e_filepath = path.join(self.filepath, entry)
            e_fp = expandpath(e_filepath)
            if path.isdir(e_fp):
                # Add a subdirectory only if it was
                # previously registered.
                info = registry.getDirectoryInfo(e_filepath)
                if info is not None:
                    mt = types.get(entry)
                    t = None
                    if mt is not None:
                        t = registry.getTypeByMetaType(mt)
                    if t is None:
                        t = DirectoryView
                    ob = t(entry, e_filepath)
                    data[ob.getId()] = ob
            else:
                pos = rfind(entry, '.')
                if pos >= 0:
                    name = entry[:pos]
                    ext = normalize(entry[pos + 1:])
                else:
                    name = entry
                    ext = ''
                if not name or bad_id(entry) != -1 or name == 'REQUEST':
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
                    ob = t(name, e_filepath, fullname=entry)
                    data[ob.getId()] = ob
        return data


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
                subpath = path + '/' + subob.id
            else:
                subpath = subob.id
            title = getattr(subob, 'title', None)
            if title:
                name = '%s (%s)' % (subpath, title)
            else:
                name = subpath
            rval.append((subpath, name))
            listFolderHierarchy(subob, subpath, rval, adding_meta_type)


try: superFolderGetattr = Folder.__getattr__
except:
    try: superFolderGetattr = Folder.inheritedAttribute('__getattr__')
    except:
        def superFolderGetattr(self, name):
            raise AttributeError, name


class DirectoryView (Folder):
    '''
    '''

    security = ClassSecurityInfo()

    meta_type = 'Filesystem Directory View'
    all_meta_types = ()
    _isDirectoryView = 1

    _dirpath = None

    def __init__(self, id, dirpath, fullname=None):
        self.id = id
        self._dirpath = dirpath

    def _getFSObjects(self):
        info = _dirreg.getDirectoryInfo(self._dirpath)
        if info is not None:
            return info.getContents(_dirreg)
        else:
            return None

    def __getattr__(self, name, superget=superFolderGetattr):
        obs = self._getFSObjects()
        if obs is not None and obs.has_key(name):
            return obs[name]
        return superget(self, name)

    security.declareProtected(AccessContentsInformation,'getCustomizableObject')
    def getCustomizableObject(self):
        ob = aq_parent(aq_inner(self))
        while getattr(ob, '_isDirectoryView', 0):
            ob = aq_parent(aq_inner(ob))
        return ob

    security.declareProtected(AccessContentsInformation, 'listCustFolderPaths')
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

    security.declarePublic('getid')
    def getId(self):
        return self.id

    # Override some methods to make the non-persistent
    # objects visible.

    def objectIds(self, spec=None):
        # Returns a list of subobject ids of the current object.
        # If 'spec' is specified, returns objects whose meta_type
        # matches 'spec'.
        fsobs = self._getFSObjects()
        if spec is not None:
            if type(spec)==type('s'):
                spec=[spec]
            set=[]
            for ob in self._objects:
                if ob['meta_type'] in spec:
                    set.append(ob['id'])
            if fsobs is not None:
                for key, value in fsobs.items():
                    if not key in set and value.meta_type in spec:
                        set.append(key)
            return set
        
        set = list(map(lambda i: i['id'], self._objects))
        if fsobs is not None:
            for key in fsobs.keys():
                if not key in set:
                    set.append(key)
        return set

    def objectMap(self):
        # Return a tuple of mappings containing subobject meta-data.
        objs = []
        fsobs = self._getFSObjects()
        if fsobs is not None:
            for key, value in fsobs.items():
                objs.append({'id':key, 'meta_type':value.meta_type})
        for info in self._objects:
            objs.append(info.copy())
        return tuple(objs)

    def objectMap_d(self,t=None):
        if hasattr(self, '_reserved_names'): n=self._reserved_names
        else: n=()
        if not n: return self.objectMap()
        r=[]
        a=r.append
        for d in self.objectMap():
            if d['id'] not in n: a(d)
        return r

    def tpValues(self):
        # Return a list of subobjects, used by tree tag.
        r=[]
        if hasattr(aq_base(self), 'tree_ids'):
            for id in self.tree_ids:
                if hasattr(self, id):
                    r.append(self._getOb(id))
        else:
            for id in self.objectIds():
                o = self._getOb(id)
                try:
                    if o.isPrincipiaFolderish: r.append(o)
                except: pass

        return r

Globals.InitializeClass(DirectoryView)


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

