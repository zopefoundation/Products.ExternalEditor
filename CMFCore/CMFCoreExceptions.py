##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
""" Declare Exceptions used throughout the CMF.

$Id$
"""

from AccessControl import ModuleSecurityInfo
from AccessControl import Unauthorized as AccessControl_Unauthorized
from OFS.CopySupport import CopyError
from webdav.Lockable import ResourceLockedError
from zExceptions import Unauthorized as zExceptions_Unauthorized


security = ModuleSecurityInfo('Products.CMFCore.CMFCoreExceptions')

# Use AccessControl_Unauthorized to raise Unauthorized errors and
# zExceptions_Unauthorized to catch them all.

security.declarePublic('AccessControl_Unauthorized')
security.declarePublic('CopyError')
security.declarePublic('ResourceLockedError')
security.declarePublic('zExceptions_Unauthorized')


security.declarePublic('IllegalHTML')
class IllegalHTML(ValueError):
    """ Illegal HTML error.
    """


security.declarePublic('EditingConflict')
class EditingConflict(Exception):
    """ Editing conflict error.
    """
