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
""" CMFActionIcons Installer

This file is an installation script for CMFActionIcons.  It's meant to be
used as an External Method.  To use, add an external method to the
root of the CMF Site that you want CMFActoinIcons registered in with the
configuration:

 id: install_actionicons
 title: Install Action Icons *optional*
 module name: CMFActionIcons.Install
 function name: install

Then go to the management screen for the newly added external method
and click the 'Try it' tab.  The install function will execute and give
information about the steps it took to register and install the
CMFActionIcons into the CMF Site instance. 
"""
import string
from cStringIO import StringIO

from Acquisition import aq_base

from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.CMFCore.utils import getToolByName

from Products.CMFActionIcons import actionicons_globals
from Products.CMFActionIcons.standard_mappings import installActionIconMappings


def install( self, install_standard_mappings=1 ):
    """ Register the CMF ActionIcons tool and skins.
    """
    out = StringIO()
    skinstool = getToolByName( self, 'portal_skins' )
    portal_url = getToolByName( self, 'portal_url' )

    # Add the CMFActionIcons tool to the site's root
    p = portal_url.getPortalObject()
    x = p.manage_addProduct[ 'CMFActionIcons' ].manage_addTool(
                                        type='Action Icons Tool')


    out.write( "Added 'portal_actionicons' tool to site." )

    if install_standard_mappings:
        tool = getToolByName( p, 'portal_actionicons' )
        installActionIconMappings( tool )
        out.write( "Added standard mappings to the tool." )
    
    # Setup the skins
    if 'actionicons' not in skinstool.objectIds():
        # We need to add Filesystem Directory Views for any directories
        # in our skins/ directory.  These directories should already be
        # configured.
        addDirectoryViews( skinstool, 'skins', actionicons_globals )
        out.write( "Added 'actionicons' directory view to portal_skins\n" )

    # Now we need to go through the skin configurations and insert
    # 'actionicons' into the configurations.  Preferably, this should be
    # right after where 'custom' is placed.  Otherwise, we append
    # it to the end.
    skins = skinstool.getSkinSelections()
    for skin in skins:
        path = skinstool.getSkinPath( skin )
        path = [ x.strip() for x in path.split( ',' ) ]
        if 'actionicons' not in path:
            try:
                path.insert( path.index( 'custom' ) + 1, 'actionicons' )
            except ValueError:
                path.append( 'actionicons' )
                
            path = string.join( path, ', ' )
            # addSkinSelection will replace exissting skins as well.
            skinstool.addSkinSelection( skin, path )
            out.write( "Added 'actionicons' to %s skin\n" % skin )
        else:
            out.write( "Skipping %s skin, 'actionicons' is already set up\n"
                     % skin )

    return out.getvalue()

