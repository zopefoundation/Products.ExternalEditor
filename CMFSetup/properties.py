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
""" Site properties setup handlers.

$Id$
"""

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from permissions import ManagePortal
from utils import _xmldir
from utils import ConfiguratorBase
from utils import DEFAULT, KEY


#
#   Configurator entry points
#
_FILENAME = 'properties.xml'

def importSiteProperties(context):
    """ Import site properties from an XML file.
    """
    site = context.getSite()
    encoding = context.getEncoding()

    if context.shouldPurge():

        for prop_map in site._propertyMap():
            prop_id = prop_map['id']
            if 'd' in prop_map.get('mode', 'wd') and \
                    prop_id not in ('title', 'description'):
                site._delProperty(prop_id)
            else:
                if prop_map.get('type') == 'multiple selection':
                    prop_value = ()
                else:
                    prop_value = ''
                site._updateProperty(prop_id, prop_value)

    xml = context.readDataFile(_FILENAME)
    if xml is None:
        return 'Site properties: Nothing to import.'

    spc = SitePropertiesConfigurator(site, encoding)
    site_info = spc.parseXML(xml)

    for prop_info in site_info['properties']:
        spc.initProperty(site, prop_info)

    return 'Site properties imported.'

def exportSiteProperties(context):
    """ Export site properties as an XML file.
    """
    site = context.getSite()
    spc = SitePropertiesConfigurator(site).__of__(site)

    xml = spc.generateXML()
    context.writeDataFile(_FILENAME, xml, 'text/xml')

    return 'Site properties exported.'


class SitePropertiesConfigurator(ConfiguratorBase):
    """ Synthesize XML description of site's properties.
    """
    security = ClassSecurityInfo()

    security.declareProtected(ManagePortal, 'listSiteInfos')
    def listSiteInfos(self):
        """ Get a sequence of mappings for site properties.
        """
        return tuple( [ self._extractProperty(self._site, prop_map)
                        for prop_map in self._site._propertyMap() ] )

    def _getExportTemplate(self):

        return PageTemplateFile('spcExport.xml', _xmldir)

    def _getImportMapping(self):

        return { 'site': { 'property': {KEY: 'properties', DEFAULT: () } } }

InitializeClass(SitePropertiesConfigurator)
