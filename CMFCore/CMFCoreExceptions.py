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

from AccessControl import allow_class
from AccessControl import Unauthorized


class CMFError(Exception):
    """ The root of all CMF evil.
    """

allow_class(CMFError)


class CMFNotImplementedError(NotImplementedError, CMFError):
    """ NotImplementedError in CMF.
    """

allow_class(CMFNotImplementedError)


class CMFUnauthorizedError(Unauthorized, CMFError):
    """ Unauthorized error in CMF.
    """

allow_class(CMFUnauthorizedError)
