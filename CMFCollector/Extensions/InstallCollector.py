##############################################################################
# Copyright (c) 2001 Zope Corporation.  All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 1.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE.
##############################################################################
"""This file is an installation script (External method) for the CMF Collector.

To use, add an external method to the root of the CMF Site that you want CMF
Event registered in with the configuration:

 id: install_collector
 title (optional): Install Collector 
 module name: CMFCollector.InstallCollector
 function name: install_collector

Then go to the management screen for the newly added external method
and click the 'Try it' tab.  The install function will execute and give
information about the steps it took to register and install the
CMF Events into the CMF Site instance. 
"""
from Products.CMFCore.TypesTool import ContentFactoryMetadata
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.CMFCore.utils import getToolByName
from Products import CMFCollector
from cStringIO import StringIO
from Acquisition import aq_base
import string

INVISIBLE_TYPES = ('Collector Issue', 'Collector Issue Transcript')

def install_collector(self):
    " Register the Collector with portal_types and friends "
    out = StringIO()
    types_tool = getToolByName(self, 'portal_types')
    skins_tool = getToolByName(self, 'portal_skins')
    metadata_tool = getToolByName(self, 'portal_metadata')
    catalog = getToolByName(self, 'portal_catalog')

    # Due to differences in the APIs for adding indexes between
    # Zope 2.3 and 2.4, we have to catch them here before we can add
    # our new ones.
    base = aq_base(catalog)
    if hasattr(base, 'addIndex'):
        # Zope 2.4
        addIndex = catalog.addIndex
    else:
        # Zope 2.3 and below
        addIndex = catalog._catalog.addIndex
    if hasattr(base, 'addColumn'):
        # Zope 2.4
        addColumn = catalog.addColumn
    else:
        # Zope 2.3 and below
        addColumn = catalog._catalog.addColumn
    # *** Example demonstrating catalog field additions.
##    addIndex('start', 'FieldIndex')
##    addIndex('end', 'FieldIndex')
##    addColumn('start')
##    addColumn('end')
##    out.write('Added "start" and "end" field indexes and columns to '
##              'the portal_catalog\n')

    # Borrowed from CMFDefault.Portal.PortalGenerator.setupTypes()
    # We loop through anything defined in the factory type information
    # and configure it in the types tool if it doesn't already exist
    for t in CMFCollector.factory_type_information:
        if t['id'] not in types_tool.objectIds():
            cfm = apply(ContentFactoryMetadata, (), t)
            types_tool._setObject(t['id'], cfm)
            out.write('Registered %s with the types tool\n' % t['id'])
        else:
            out.write('Skipping "%s" - already in types tool\n' % t['id'])

    # Setup a Metadata_tool Element Policy for Events
    # XXX Just trying this, doesn't mean submitter_name is actually required.
##    metadata_tool.addElementPolicy(
##        element='submitter_name',
##        content_type='CollectorIssue',
##        is_required=1,
##        supply_default=0,
##        default_value='',
##        enforce_vocabulary=0,
##        allowed_vocabulary=('Appointment', 'Convention', 'Meeting',
##                            'Social Event', 'Work'),
##        REQUEST=None,
##        )
##    out.write('CollectorIssue added to Metdata element Policies\n')
    
    

    # Setup the skins
    # This is borrowed from CMFDefault/scripts/addImagesToSkinPaths.pys
    if 'collector' not in skins_tool.objectIds():
        # We need to add Filesystem Directory Views for any directories
        # in our skins/ directory.  These directories should already be
        # configured.
        addDirectoryViews(skins_tool, 'skins', CMFCollector.collector_globals)
        out.write("Added collector skin directory view to portal_skins\n")

    # Now we need to go through the skin configurations and insert
    # 'collector' into the configurations.  Preferably, this should be
    # right before where 'content' is placed.  Otherwise, we append
    # it to the end.
    skins = skins_tool.getSkinSelections()
    for skin in skins:
        path = skins_tool.getSkinPath(skin)
        path = map(string.strip, string.split(path,','))
        if 'collector' not in path:
            try: path.insert(path.index('content'), 'collector')
            except ValueError:
                path.append('collector')
                
            path = string.join(path, ', ')
            # addSkinSelection will replace exissting skins as well.
            skins_tool.addSkinSelection(skin, path)
            out.write("Added 'collector' to %s skin\n" % skin)
        else:
            out.write("Skipping %s skin, 'collector' is already set up\n" % (
                skin))

    return out.getvalue()

