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

"""Base class for objects that supply skins.
$Id$
"""
__version__='$Revision$'[11:-2]

from string import split, join, strip
from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class SkinPathError (Exception):
    'Invalid skin path'
    pass


class SkinsContainer:
    security = ClassSecurityInfo()

    security.declarePublic('getSkinPath')
    def getSkinPath(self, name):
        '''
        Converts a skin name to a skin path.
        '''
        raise 'Not implemented'

    security.declarePublic('getDefaultSkin')
    def getDefaultSkin(self):
        '''
        Returns the default skin name.
        '''
        raise 'Not implemented'

    security.declarePublic('getRequestVarname')
    def getRequestVarname(self):
        '''
        Returns the variable name to look for in the REQUEST.
        '''
        raise 'Not implemented'

    security.declarePrivate('getSkinByPath')
    def getSkinByPath(self, path, raise_exc=0):
        '''
        Returns a skin at the given path.  A skin path is of the format:
        "some/path, some/other/path, ..."  The first part has precedence.
        '''
        baseself = aq_base(self)
        skinob = baseself
        parts = list(split(path, ','))
        parts.reverse()
        for part_path in parts:
            partob = baseself
            for name in split(strip(part_path), '/'):
                if name == '':
                    continue
                if name[:1] == '_':
                    # Not allowed.
                    partob = None
                    if raise_exc:
                        raise SkinPathError('Underscores are not allowed')
                    break
                # Allow acquisition tricks.
                partob = getattr(partob, name, None)
                if partob is None:
                    # Not found.  Cancel the search.
                    if raise_exc:
                        raise SkinPathError('Name not found: %s' % part_path)
                    break
            if partob is not None:
                # Now partob has containment and context.
                # Build the final skinob by creating an object
                # that puts the former skinob in the context
                # of the new skinob.
                skinob = partob.__of__(skinob)
        return skinob
        
    security.declarePrivate('getSkinByName')
    def getSkinByName(self, name):
        path = self.getSkinPath(name)
        if path is None:
            return None
        return self.getSkinByPath(path)

    security.declarePrivate('getSkin')
    def getSkin(self, request):
        '''
        Returns the requested skin.
        '''
        varname = self.getRequestVarname()
        name = request.get(varname, None)
        skinob = None
        if name is not None:
            skinob = self.getSkinByName(name)
        if skinob is None:
            skinob = self.getSkinByName(self.getDefaultSkin())
            if skinob is None:
                skinob = self.getSkinByPath('')
        return skinob


InitializeClass( SkinsContainer )
