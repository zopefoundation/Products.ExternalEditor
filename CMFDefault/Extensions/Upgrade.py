##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
    Utility functions for upgrading CMFDefault-based sites.
"""

from Acquisition import aq_inner


def upgrade_decor_skins( self ):
    """
        Upgrade old skin diretories loaded from 'CMFDecor' to load from
        'CMFDefault' (and zap the 'zpt_images' one).
    """
    log = []

    DELETED_SKINS = ( 'zpt_images' , )

    MOVED_SKINS = ( 'zpt_content'
                  , 'zpt_control'
                  , 'zpt_generic'
                  )

    skins_tool = aq_inner( self ).portal_skins # start from CMFSite!

    for deleted in DELETED_SKINS:

        try:

            skins_tool._delObject( deleted )

        except AttributeError:
            pass

        else:
            log.append( 'Deleted CMFDecor skin directory: %s' % deleted )

    for moved in MOVED_SKINS:

        skin_dir = getattr( skins_tool, moved, None )

        if skin_dir is not None:

            skin_dir.manage_properties(
                dirpath='Products/CMFDefault/skins/%s' % moved )
            log.append( 'Updated CMFDecor skin directory to CMFDefault: %s'
                      % moved )

    return '\n'.join(log)
