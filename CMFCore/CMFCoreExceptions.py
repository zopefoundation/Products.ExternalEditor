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
from AccessControl import Unauthorized
from OFS.CopySupport import CopyError
from webdav.Lockable import ResourceLockedError


security = ModuleSecurityInfo('Products.CMFCore.CMFCoreExceptions')
security.declarePublic('CopyError')
security.declarePublic('Unauthorized')


security.declarePublic('CMFError')
class CMFError(Exception):
    """ The root of all CMF evil.
    """


security.declarePublic('CMFNotImplementedError')
class CMFNotImplementedError(NotImplementedError, CMFError):
    """ NotImplementedError in CMF.
    """


security.declarePublic('CMFResourceLockedError')
class CMFResourceLockedError(ResourceLockedError, CMFError):
    """ ResourceLockedError in CMF.
    """


security.declarePublic('CMFUnauthorizedError')
class CMFUnauthorizedError(Unauthorized, CMFError):
    """ Unauthorized error in CMF.
    """


security.declarePublic('IllegalHTML')
class IllegalHTML(ValueError, CMFError):
    """ Illegal HTML error.
    """
