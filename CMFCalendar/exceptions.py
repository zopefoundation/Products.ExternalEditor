##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" CMFCalendar product exceptions.

$Id$
"""

from AccessControl import ModuleSecurityInfo
security = ModuleSecurityInfo('Products.CMFCalendar.exceptions')

security.declarePublic('CatalogError')
from Products.ZCatalog.Catalog import CatalogError

security.declarePublic('MetadataError')
from Products.CMFDefault.exceptions import MetadataError

security.declarePublic('ResourceLockedError')
from Products.CMFCore.exceptions import ResourceLockedError
