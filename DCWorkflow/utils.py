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
'''
Some common utilities.
$Id$
'''
__version__='$Revision$'[11:-2]

import os
from App.Common import package_home

_dtmldir = os.path.join( package_home( globals() ), 'dtml' )

from AccessControl.Role import gather_permissions
from AccessControl.Permission import Permission

def ac_inherited_permissions(ob, all=0):
    # Get all permissions not defined in ourself that are inherited
    # This will be a sequence of tuples with a name as the first item and
    # an empty tuple as the second.
    d = {}
    perms = getattr(ob, '__ac_permissions__', ())
    for p in perms: d[p[0]] = None
    r = gather_permissions(ob.__class__, [], d)
    if all:
       if hasattr(ob, '_subobject_permissions'):
           for p in ob._subobject_permissions():
               pname=p[0]
               if not d.has_key(pname):
                   d[pname]=1
                   r.append(p)
       r = list(perms) + r
    return r

def modifyRolesForPermission(ob, pname, roles):
    '''
    Modifies multiple role to permission mappings.  roles is a list to
    acquire, a tuple to not acquire.
    '''
    # This mimics what AccessControl/Role.py does.
    data = ()
    for perm in ac_inherited_permissions(ob, 1):
        name, value = perm[:2]
        if name == pname:
            data = value
            break
    p = Permission(pname, data, ob)
    if p.getRoles() != roles:
        p.setRoles(roles)
        return 1
    return 0
