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
"""\
This file is an installation script for CMFDecor (ZPT skins).  It's meant
to be used as an External Method.  To use, add an external method to the
root of the CMF Site that you want ZPT skins registered in with the
configuration:

 id: install_decor
 title: Install Decor Skins *optional*
 module name: CMFDecor.Install
 function name: install

Then go to the management screen for the newly added external method
and click the 'Try it' tab.  The install function will execute and give
information about the steps it took to register and install the
ZPT skins into the CMF Site instance. 
"""
from Products.CMFCore.TypesTool import ContentFactoryMetadata
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.CMFCore.utils import getToolByName
from Products.CMFDecor import cmfdecor_globals

from Acquisition import aq_base
from cStringIO import StringIO
import string

ZPT_SKINS_DIRS = ( 'zpt_content', 'zpt_control', 'zpt_generic', 'zpt_images' )

def install(self):
    " Register the ZPT Skins with portal_skins and friends "
    out = StringIO()
    skinstool = getToolByName(self, 'portal_skins')

    for dir_view in ZPT_SKINS_DIRS:
        if dir_view in skinstool.objectIds():
            skinstool._delObject( dir_view )

    try:
        addDirectoryViews( skinstool, 'skins', cmfdecor_globals )
    except:
        pass
    out.write( "Added CMFDecor directory views to portal_skins\n" )

    #
    #   Add a new skin, 'ZPT', copying 'Basic', if it exists, and then
    #   add our directories only to it.
    #
    if skinstool.getSkinPath( 'ZPT' ) is None:

        path = skinstool.getSkinPath( skinstool.getDefaultSkin() )
        path = map( string.strip, string.split( path,',' ) )
        insertion_point = path.index( 'custom' ) + 1
        for zptdir in ( 'zpt_topic', ) + ZPT_SKINS_DIRS:
            try:
                path.insert( insertion_point, zptdir )
            except ValueError:
                path.append( zptdir )
                    
        path = string.join( path, ', ' )
        skinstool.addSkinSelection( 'ZPT', path )
        out.write( "Added ZPT skin\n" )
    
    else:
        out.write( "ZPT skin already exists\n" )

    return out.getvalue()
