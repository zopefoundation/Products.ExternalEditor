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
""" Backward compatibility;  see Products.CMFCore.exceptions

$Id$
"""
from exceptions import *

from warnings import warn

warn( "The module, 'Products.CMFCore.CMFCoreExceptions' is a deprecated "
      "compatiblity alias for 'Products.CMFCore.exceptions';  please use "
      "the new module instead.", DeprecationWarning)
