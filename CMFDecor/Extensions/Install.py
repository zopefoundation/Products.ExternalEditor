##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
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

def install(self):
    " Register the ZPT Skins with portal_skins and friends "
    out = StringIO()
    skinstool = getToolByName(self, 'portal_skins')

    addDirectoryViews( skinstool, 'skins', cmfdecor_globals )
    out.write( "Added CMFDecor directory views to portal_skins\n" )

    # Setup the skins
    # This is borrowed from CMFDefault/scripts/addImagesToSkinPaths.pys
    for skin_dir in ( 'zpt_content'
                    , 'zpt_control'
                    , 'zpt_generic'
                    , 'zpt_images'
                    ):

        # Go through the skin configurations and insert each skin directory
        # into the configurations.  Preferably, this should be right before
        # where 'content' is placed.  Otherwise, we append it to the end.
        names = skinstool.getSkinSelections()
        for name in names:
            path = skinstool.getSkinPath(name)
            path = map(string.strip, string.split(path,','))
            if skin_dir not in path:
                try: path.insert( path.index('content'), skin_dir )
                except ValueError:
                    path.append( skin_dir )
                    
                path = string.join(path, ', ')
                # addSkinSelection will replace exissting skins as well.
                skinstool.addSkinSelection( name, path )
                out.write("Added %s to %s skin\n" % ( skin_dir, name ) )
            else:
                out.write("Skipping %s skin, %s is already set up\n" % (
                    name, skin_dir))

    return out.getvalue()

