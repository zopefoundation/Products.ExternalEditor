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
"""
These functions are contained in the PTKBase.register module.  They
are used to register the existance of new PortalContent classes.
"""

def registerPortalContent(instance_class,
                          meta_type='',
                          constructors=(),
                          action='',
                          permission="Add portal content",
                          icon=None,
                          ):
    """
    
    This function is used to register a new PortalContent class with
    the PTK.  It will install a constructor and an icon, and register
    the class in PortalFolder's meta_types.

    For an example of use, see the end of PTKBase/Document.py.

    'instance_class' is the PortalContent-derived class to register.
    
    'meta_type' is it's plain-language name.  If not explicitly given,
    the meta_type will be taken from the instance_class.

    'contructors' is a sequence of constructor functions.  The first
    is placed as a method on PortalFolder.  The rest are presently
    discarded.

    'action' is the relative URL of the add form or wizard.

    'permission' is the name of the permission required to instantiate
    this class.

    'icon' is the name of an image file to use as the document's icon.
    """
