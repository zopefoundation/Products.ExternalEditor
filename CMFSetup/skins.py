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
""" Skin path configuration management

Setup step and export script

$Id$
"""

import re

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import minimalpath
from Products.CMFCore.DirectoryView import createDirectoryView
from Products.CMFCore.DirectoryView import DirectoryView

from permissions import ManagePortal
from utils import _xmldir
from utils import ConfiguratorBase
from utils import CONVERTER, DEFAULT, KEY


#
#   Entry points
#
_FILENAME = 'skins.xml'

def importSkinsTool( context ):

    """ Import skins tool FSDirViews and skin paths from an XML file

    o 'context' must implement IImportContext.

    o Register via Python:

      registry = site.portal_setup.getImportStepRegistry()
      registry.registerStep( 'importSkinsTool'
                           , '20040518-01'
                           , Products.CMFSetup.skins.importSkinsTool
                           , ()
                           , 'Skins Tool import'
                           , 'Import skins tool FSDVs and skin paths.'
                           )

    o Register via XML:

      <setup-step id="importSkinsTool"
                  version="20040524-01"
                  handler="Products.CMFSetup.skins.importSkinsTool"
                  title="Skins Tool import"
      >Import skins tool FSDVs and skin paths.</setup-step>

    """
    site = context.getSite()
    encoding = context.getEncoding()

    stool = getToolByName(site, 'portal_skins')

    if context.shouldPurge():

        stool.request_varname = 'portal_skin'
        stool.allow_any = 0
        stool.cookie_persistence = 0

        stool._getSelections().clear()

        for id in stool.objectIds(DirectoryView.meta_type):
            stool._delObject(id)

    text = context.readDataFile( _FILENAME )

    if text is not None:

        stc = SkinsToolConfigurator( site, encoding )
        tool_info = stc.parseXML( text )

        if 'default_skin' in tool_info:
            stool.default_skin = str(tool_info['default_skin'])
        if 'request_varname' in tool_info:
            stool.request_varname = str(tool_info['request_varname'])
        if 'allow_any' in tool_info:
            stool.allow_any = tool_info['allow_any'] and 1 or 0
        if 'cookie_persistence' in tool_info:
            stool.cookie_persistence = \
                                    tool_info['cookie_persistence'] and 1 or 0

        for dir_info in tool_info['skin_dirs']:
            dir_id = dir_info['id']
            if dir_id in stool.objectIds(DirectoryView.meta_type):
                stool._delObject(dir_id)
            createDirectoryView(stool, dir_info['directory'], dir_id)

        for path_info in tool_info['skin_paths']:
            path_id = path_info['id']
            if path_id == '*':
                for path_id, path in stool._getSelections().items():
                    path = _updatePath(path, path_info['layers'])
                    stool.addSkinSelection(path_id, path)
            else:
                if stool._getSelections().has_key(path_id):
                    path = stool._getSelections()[path_id]
                else:
                    path = ''
                path = _updatePath(path, path_info['layers'])
                stool.addSkinSelection(path_id, path)

    #
    #   Purge and rebuild the skin path, now that we have added our stuff.
    #   Don't bother if no REQUEST is present, e.g. when running unit tests
    #
    request = getattr(site, 'REQUEST', None)
    if request is not None:
        site.clearCurrentSkin()
        site.setupCurrentSkin(request)

    return 'Skins tool imported'

def _updatePath(path, layer_infos):
    path = [ name.strip() for name in path.split(',') if name.strip() ]

    for layer in layer_infos:
        if layer['name'] in path:
            path.remove(layer['name'])
        if 'insert-before' in layer:
            try:
                index = path.index(layer['insert-before'])
                path.insert(index, layer['name'])
                continue
            except ValueError:
                pass
        if 'insert-after' in layer:
            try:
                index = path.index(layer['insert-after'])
                path.insert(index+1, layer['name'])
                continue
            except ValueError:
                pass
        path.append(layer['name'])

    return str( ','.join(path) )

def exportSkinsTool( context ):

    """ Export skins tool FSDVs and skin paths as an XML file

    o 'context' must implement IExportContext.

    o Register via Python:

      registry = site.portal_setup.getExportStepRegistry()
      registry.registerStep( 'exportSkinsTool'
                           , Products.CMFSetup.skins.exportSkinsTool
                           , 'Skins Tool export'
                           , 'Export skins tool FSDVs and skin paths.'
                           )

    o Register via XML:

      <export-script id="exportSkinsTool"
                     version="20040518-01"
                     handler="Products.CMFSetup.skins.exportSkinsTool"
                     title="Skins Tool export"
      >Export skins tool FSDVs and skin paths.</export-script>

    """
    site = context.getSite()
    stc = SkinsToolConfigurator( site ).__of__( site )
    text = stc.generateXML()

    context.writeDataFile( _FILENAME, text, 'text/xml' )

    return 'Skins tool exported.'


class SkinsToolConfigurator(ConfiguratorBase):

    security = ClassSecurityInfo()

    _COMMA_SPLITTER = re.compile( r',[ ]*' )

    security.declareProtected(ManagePortal, 'getToolInfo' )
    def getToolInfo( self ):

        """ Return the tool's settings.
        """
        stool = getToolByName(self._site, 'portal_skins')

        return { 'default_skin': stool.default_skin,
                 'request_varname': stool.request_varname,
                 'allow_any': stool.allow_any,
                 'cookie_persistence': stool.cookie_persistence }

    security.declareProtected(ManagePortal, 'listSkinPaths' )
    def listSkinPaths( self ):

        """ Return a sequence of mappings for each skin path in the tool.

        o Keys include:

          'id' -- folder ID

          'path' -- sequence of layer IDs
        """
        stool = getToolByName(self._site, 'portal_skins')

        return [ { 'id' : k
                 , 'path' : self._COMMA_SPLITTER.split( v )
                 } for k, v in stool.getSkinPaths() ]

    security.declareProtected(ManagePortal, 'listFSDirectoryViews' )
    def listFSDirectoryViews( self ):

        """ Return a sequence of mappings for each FSDV.

        o Keys include:

          'id' -- FSDV ID

          'directory' -- filesystem path of the FSDV.
        """
        result = []
        stool = getToolByName(self._site, 'portal_skins')

        fsdvs = stool.objectItems( DirectoryView.meta_type )
        fsdvs.sort()

        for id, fsdv in fsdvs:

            dirpath = fsdv._dirpath

            if dirpath.startswith( '/' ):
                dirpath = minimalpath( fsdv._dirpath )

            result.append( { 'id' : id
                           , 'directory' : dirpath
                           } )

        return result

    def _getExportTemplate(self):

        return PageTemplateFile('stcExport.xml', _xmldir)

    def _getImportMapping(self):

        return {
          'skins-tool':
            { 'default_skin':       {},
              'request_varname':    {},
              'allow_any':          {CONVERTER: self._convertToBoolean},
              'cookie_persistence': {CONVERTER: self._convertToBoolean},
              'skin-directory':     {KEY: 'skin_dirs', DEFAULT: ()},
              'skin-path':          {KEY: 'skin_paths', DEFAULT: ()} },
          'skin-directory':
            { 'id':                 {},
              'directory':          {} },
          'skin-path':
            { 'id':                 {},
              'layer':              {KEY: 'layers', DEFAULT: ()} },
          'layer':
            { 'name':               {},
              'insert-after' :      {},
              'insert-before':      {} } }

InitializeClass(SkinsToolConfigurator)
