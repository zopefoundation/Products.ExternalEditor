##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" CMFDefault setup handlers.

$Id$
"""

from Products.CMFCore.utils import getToolByName

from Portal import PortalGenerator


def importVarious(context):
    """ Import various settings from PortalGenerator.

    This provisional handler will be removed again as soon as full handlers
    are implemented for these steps.
    """
    site = context.getSite()

    # try to install CMFUid without raising exceptions if not available
    try:
        addCMFUidTool = site.manage_addProduct['CMFUid'].manage_addTool
    except AttributeError:
        pass
    else:
        addCMFUidTool('Unique Id Annotation Tool', None)
        addCMFUidTool('Unique Id Generator Tool', None)
        addCMFUidTool('Unique Id Handler Tool', None)

    # add custom skin folder
    stool = getToolByName(site, 'portal_skins')
    stool.manage_addProduct['OFSP'].manage_addFolder(id='custom')

    gen = PortalGenerator()
    gen.setupMailHost(site)
    gen.setupUserFolder(site)
    gen.setupCookieAuth(site)
    gen.setupMembersFolder(site)
    gen.setupMimetypes(site)

    return 'Various settings from PortalGenerator imported.'
