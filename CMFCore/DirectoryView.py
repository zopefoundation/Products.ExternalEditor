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
from zLOG import LOG, ERROR
from sys import exc_info
from types import StringType

_dtmldir = os.path.join( package_home( globals() ), 'dtml' )

__reload_module__ = 0

# Ignore version control subdirectories
# and special names.
def _filter(name):
    return name not in ('CVS', 'SVN', '.', '..')

def _filtered_listdir(path):
    n = filter(_filter,
               listdir(path))
    return n

def _walker (listdir, dirname, names):
    names[:]=filter(_filter,names)
    listdir.extend(names)

class DirectoryInformation:
    data = None
    _v_last_read = 0
    _v_last_filelist = [] # Only used on Win32

    def __init__(self, expanded_fp, minimal_fp):
        self.filepath = minimal_fp
        subdirs = []
        for entry in _filtered_listdir(expanded_fp):
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


    def _readProperties(self, fp):
        """Reads the properties file next to an object.
        """
        try:
            f = open(fp, 'rt')
        except IOError:
            return None
        else:
            lines = f.readlines()
            f.close()
            props = {}
            for line in lines:
                try: key, value = split(line, '=')
                except: pass
                else:
                    props[strip(key)] = strip(value)
            return props


    if Globals.DevelopmentMode and os.name=='nt':

        def _changed(self):
            mtime=0
            filelist=[]
            try:
                fp = expandpath(self.filepath)
                mtime = stat(fp)[8]
                # some Windows directories don't change mtime 
                # when a file in them changes :-(
                # So keep a list of files as well, and see if that
                # changes
                path.walk(fp,_walker,filelist)
                filelist.sort()
            except: 
                from zLOG import LOG, ERROR
                import sys
                LOG('DirectoryView',
                    ERROR,
                    'Error checking for directory modification',
                    error=sys.exc_info())
                
            if mtime != self._v_last_read or filelist != self._v_last_filelist:
                self._v_last_read = mtime
                self._v_last_filelist = filelist
                
                return 1

            return 0
        
    elif Globals.DevelopmentMode:
        
        def _changed(self):
            try: mtime = stat(expandpath(self.filepath))[8]
            except: mtime = 0
            if mtime != self._v_last_read:
                self._v_last_read = mtime
                return 1
            return 0
        
    else:

        def _changed(self):
            return 0
        
    def getContents(self, registry):
        changed = self._changed()
        if self.data is None or changed:
            try:
                self.data, self.objects = self.prepareContents(registry,
                    register_subdirs=changed)
            except:
                LOG('DirectoryView',
                    ERROR,
                    'Error during prepareContents:',
                    error=exc_info())
                self.data = {}
                self.objects = ()
                    
        return self.data, self.objects

    def prepareContents(self, registry, register_subdirs=0):
        # Creates objects for each file.
        fp = expandpath(self.filepath)
        data = {}
        objects = []
        types = self._readTypesFile()
        for entry in _filtered_listdir(fp):
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
                    properties = self._readProperties(
                        e_fp + '.properties')
                    try:
                        ob = t(name, e_filepath, fullname=entry,
                               properties=properties)
                    except:
                        import traceback
                        typ, val, tb = exc_info()
                        try:
                            exc_lines = traceback.format_exception( typ,
                                                                    val,
                                                                    tb )
                            LOG( 'DirectoryView',
                                 ERROR,
                                 join( exc_lines, '\n' ) )
                            
                            ob = BadFile( name,
                                          e_filepath,
                                          exc_str=join( exc_lines, '\r\n' ),
                                          fullname=entry )
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

    def registerDirectory(self, name, _prefix, subdirs=1):
        if not isinstance(_prefix, StringType):
            _prefix = package_home(_prefix)
        filepath = path.join(_prefix, name)
        self.registerDirectoryByPath(filepath, subdirs)

    def registerDirectoryByPath(self, filepath, subdirs=1):
        fp = minimalpath(filepath)
        normfilepath = path.normpath(filepath)
        self._directories[fp] = di = DirectoryInformation(normfilepath, fp)
        if subdirs:
            for entry in di.getSubdirs():
                e_filepath = path.join(normfilepath, entry)
                self.registerDirectoryByPath(e_filepath, subdirs)

    def reloadDirectory(self, filepath):
        info = self.getDirectoryInfo(filepath)
        if info is not None:
            info.reload()

    def getDirectoryInfo(self, filepath):
        # Can return None.
        return self._directories.get(os.path.normpath(filepath), None)

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
    def manage_properties( self, dirpath, REQUEST=None ):
        """
            Update the directory path of the DV.
        """
        self.__dict__['_real']._dirpath = dirpath
        if REQUEST is not None:
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

def addDirectoryViews(ob, name, _prefix):
    '''
    Adds a directory view for every subdirectory of the
    given directory.
    '''
    # Meant to be called by filesystem-based code.
    # Note that registerDirectory() still needs to be called
    # by product initialization code to satisfy
    # persistence demands.
    if not isinstance(_prefix, StringType):
        _prefix = package_home(_prefix)
    fp = path.join(_prefix, name)
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

