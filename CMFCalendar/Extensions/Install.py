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
This file is an installation script for CMFCalendar (Events).  It's meant to be
used as an External Method.  To use, add an external method to the
root of the CMF Site that you want CMF Event registered in with the
configuration:

 id: install_events
 title: Install Events *optional*
 module name: CMFCalendar.Install
 function name: install

Then go to the management screen for the newly added external method
and click the 'Try it' tab.  The install function will execute and give
information about the steps it took to register and install the
CMF Events into the CMF Site instance. 
"""
from Products.CMFCore.TypesTool import ContentFactoryMetadata
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.CMFCore.utils import getToolByName, ToolInit
from Products.CMFCalendar import Event, event_globals
from Acquisition import aq_base
from cStringIO import StringIO
import string


def install(self):
    " Register the CMF Event with portal_types and friends "
    out = StringIO()
    typestool = getToolByName(self, 'portal_types')
    skinstool = getToolByName(self, 'portal_skins')
    metadatatool = getToolByName(self, 'portal_metadata')
    catalog = getToolByName(self, 'portal_catalog')
    portal_url = getToolByName(self, 'portal_url')

    # Due to differences in the API's for adding indexes between
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
    try:
        addIndex('start', 'FieldIndex')
    except: pass
    try:
        addIndex('end', 'FieldIndex')
    except: pass
    try:
        addColumn('start')
    except: pass
    try:
        addColumn('end')
    except: pass
    out.write('Added "start" and "end" field indexes and columns to '\
              'the portal_catalog\n')

    # Borrowed from CMFDefault.Portal.PortalGenerator.setupTypes()
    # We loop through anything defined in the factory type information
    # and configure it in the types tool if it doesn't already exist
    for t in Event.factory_type_information:
        if t['id'] not in typestool.objectIds():
            cfm = apply(ContentFactoryMetadata, (), t)
            typestool._setObject(t['id'], cfm)
            out.write('Registered with the types tool\n')
        else:
            out.write('Object "%s" already existed in the types tool\n' % (
                t['id']))

    # Setup a MetadataTool Element Policy for Events
    try:
        metadatatool.addElementPolicy(
            element='Subject',
            content_type='Event',
            is_required=0,
            supply_default=0,
            default_value='',
            enforce_vocabulary=0,
            allowed_vocabulary=('Appointment', 'Convention', 'Meeting',
                                'Social Event', 'Work'),
            REQUEST=None,
            )
    except: pass
    out.write('Event added to Metadata element Policies\n')
    
    # Add the CMFCalendar tool to the site's root
    p = portal_url.getPortalObject()
    x = p.manage_addProduct['CMFCalendar'].manage_addTool(type="CMF Calendar Tool")
    
    # Setup the skins
    # This is borrowed from CMFDefault/scripts/addImagesToSkinPaths.pys
    if 'calendar' not in skinstool.objectIds():
        # We need to add Filesystem Directory Views for any directories
        # in our skins/ directory.  These directories should already be
        # configured.
        addDirectoryViews(skinstool, 'skins', event_globals)
        out.write("Added 'calendar' directory view to portal_skins\n")

    # Now we need to go through the skin configurations and insert
    # 'calendar' into the configurations.  Preferably, this should be
    # right before where 'content' is placed.  Otherwise, we append
    # it to the end.
    skins = skinstool.getSkinSelections()
    for skin in skins:
        path = skinstool.getSkinPath(skin)
        path = map(string.strip, string.split(path,','))
        if 'calendar' not in path:
            try: path.insert(path.index('content'), 'calendar')
            except ValueError:
                path.append('calendar')
                
            try: path.insert(path.index('zpt_content'), 'zpt_calendar')
            except ValueError:
                pass
            
            path = string.join(path, ', ')
            # addSkinSelection will replace exissting skins as well.
            skinstool.addSkinSelection(skin, path)
            out.write("Added 'calendar' to %s skin\n" % skin)
        else:
            out.write("Skipping %s skin, 'calendar' is already set up\n" % (
                skin))

    return out.getvalue()

