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

"""register: register portal content types with the CMF.
$Id$
"""
__version__='$Revision$'[11:-2]

import urllib
import OFS, Globals
from PortalFolder import PortalFolder
from AccessControl.PermissionRole import PermissionRole


def registerPortalContent(instance_class,
                          meta_type='',
                          constructors=(),
                          action='',
                          permission="Add portal content",
                          icon=None,
                          productGlobals=None,
                          ):
    """
    instance_class is the PortalContent-derived class to register
    
    meta_type is it's plain-language name

    contructors is a sequence of constructor functions.  The first is
    placed as a method on PortalFolder.

    action is the relative URL of the add form or wizard

    permission is the name of the permission required to instantiate
    this class

    icon is the name of an image file to use as the document's icon
    """
    return

if 0:
    meta_type = meta_type or getattr(instance_class, 'meta_type', '')
    
    if constructors:
        pr = PermissionRole(permission)
        for c in constructors:
            name = c.__name__
            setattr(PortalFolder, name, c)
            setattr(PortalFolder, '%s__roles__' % name, pr)
    
    PortalFolder.content_meta_types=PortalFolder.content_meta_types+(
        {'name': meta_type,
         'action': action,
         'permission': permission},
        )

    if icon:
        path = 'misc_/CMF/%s' % urllib.quote(meta_type)
        instance_class.icon = path
        if not hasattr(OFS.misc_.misc_, 'CMF'):
            OFS.misc_.misc_.CMF = OFS.misc_.Misc_('CMF', {})
        if type(icon) == type(''):
            try:
                if productGlobals is None:
                    productGlobals = globals()
                OFS.misc_.misc_.CMF[meta_type] = Globals.ImageFile(
                    icon, productGlobals)
            except IOError:
                pass
        else:
            OFS.misc_.misc_.CMF[meta_type] = icon
