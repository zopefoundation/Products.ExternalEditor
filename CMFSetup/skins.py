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

    skins_tool = getToolByName( site, 'portal_skins' )

    if context.shouldPurge():

        skins_tool._getSelections().clear()

        for id in skins_tool.objectIds( DirectoryView.meta_type ):
            skins_tool._delObject(id)

    text = context.readDataFile( _FILENAME )

    if text is not None:

        stc = SkinsToolConfigurator( site, encoding )
        tool_info = stc.parseXML( text )

        tool = getToolByName( site, 'portal_skins' )

        tool.default_skin = str( tool_info[ 'default_skin' ] )
        tool.request_varname = str( tool_info[ 'request_var' ] )
        tool.allow_any =  tool_info[ 'allow_arbitrary' ] and 1 or 0
        tool.cookie_persistence =  tool_info[ 'persist_cookie' ] and 1 or 0

        for dir_info in tool_info[ 'skin_dirs' ]:

            createDirectoryView( tool, dir_info[ 'directory' ],
                                 dir_info[ 'id' ] )

        for path_info in tool_info[ 'skin_paths' ]:
            tool.addSkinSelection( path_info[ 'id' ],
                                   ', '.join( path_info[ 'layers' ] ) )

    #
    #   Purge and rebuild the skin path, now that we have added our stuff.
    #
    site._v_skindata = None
    skins_tool.setupCurrentSkin( site.REQUEST )

    return 'Skins tool imported'


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
              'request_varname':    {KEY: 'request_var'},
              'allow_any':          {KEY: 'allow_arbitrary', DEFAULT: False,
                                     CONVERTER: self._convertToBoolean},
              'cookie_persistence': {KEY: 'persist_cookie', DEFAULT: False,
                                     CONVERTER: self._convertToBoolean},
              'skin-directory':     {KEY: 'skin_dirs', DEFAULT: ()},
              'skin-path':          {KEY: 'skin_paths', DEFAULT: ()} },
          'skin-directory':
            { 'id':                 {},
              'directory':          {} },
          'skin-path':
            { 'id':                 {},
              'layer':              {KEY: 'layers'} },
          'layer':
            { 'name':               {KEY: None} } }

InitializeClass(SkinsToolConfigurator)
