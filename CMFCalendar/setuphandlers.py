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
""" CMFCalendar setup handlers.

$Id$
"""

from Products.CMFCore.utils import getToolByName

from exceptions import CatalogError
from exceptions import MetadataError


def importVarious(context):
    """ Import various settings for CMF Calendar.

    This provisional handler will be removed again as soon as full handlers
    are implemented for these steps.
    """
    site = context.getSite()
    ctool = getToolByName(site, 'portal_catalog')
    mdtool = getToolByName(site, 'portal_metadata')

    # Set up a catalog indexes and metadata
    try:
        ctool.addIndex('start', 'DateIndex')
    except CatalogError:
        pass
    try:
        ctool.addIndex('end', 'DateIndex')
    except CatalogError:
        pass
    try:
        ctool.addColumn('start')
    except CatalogError:
        pass
    try:
        ctool.addColumn('end')
    except CatalogError:
        pass

    # Set up a MetadataTool element policy for events
    try:
        mdtool.addElementPolicy(
            element='Subject',
            content_type='Event',
            is_required=0,
            supply_default=0,
            default_value='',
            enforce_vocabulary=0,
            allowed_vocabulary=('Appointment', 'Convention', 'Meeting',
                                'Social Event', 'Work'),
            REQUEST=None)
    except MetadataError:
        pass

    return 'Various settings for CMF Calendar imported.'
