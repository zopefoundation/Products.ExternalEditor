""" Classes:  ImportContext, ExportContext

Wrappers representing the state of an import / export operation.

$Id$
"""
import os
import time
from tarfile import TarFile
from tarfile import TarInfo
from StringIO import StringIO

from AccessControl import ClassSecurityInfo
from Acquisition import Implicit
from Acquisition import aq_inner
from Acquisition import aq_parent
from Globals import InitializeClass
from OFS.DTMLDocument import DTMLDocument
from OFS.Folder import Folder
from OFS.Image import File
from OFS.Image import Image
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PythonScripts.PythonScript import PythonScript

from permissions import ManagePortal
from interfaces import IImportContext
from interfaces import IExportContext

class ImportContext( Implicit ):

    __implements__ = ( IImportContext, )

    security = ClassSecurityInfo()

    def __init__( self
                , tool
                , profile_path
                , should_purge=False
                , encoding=None
                ):

        self._site = aq_parent( aq_inner( tool ) )
        self._profile_path = profile_path
        self._should_purge = bool( should_purge )
        self._encoding = encoding

    security.declareProtected( ManagePortal, 'getSite' )
    def getSite( self ):

        """ See ISetupContext.
        """
        return self._site

    def getEncoding( self ):

        """ Return the encoding used in data files.

        o Return None if the data should not be encoded.
        """
        return self._encoding

    security.declareProtected( ManagePortal, 'readDataFile' )
    def readDataFile( self, filename, subdir=None ):

        """ See IImportContext.
        """
        if subdir is None:
            full_path = os.path.join( self._profile_path, filename )
        else:
            full_path = os.path.join( self._profile_path, subdir, filename )

        if not os.path.exists( full_path ):
            return None

        file = open( full_path, 'rb' )
        result = file.read()
        file.close()

        return result

    security.declareProtected( ManagePortal, 'getLastModified' )
    def getLastModified( self, path ):

        """ See IImportContext.
        """
        full_path = os.path.join( self._profile_path, path )

        if not os.path.exists( full_path ):
            return None

        return os.path.getmtime( full_path )

    security.declareProtected( ManagePortal, 'isDirectory' )
    def isDirectory( self, path ):

        """ See IImportContext.
        """
        full_path = os.path.join( self._profile_path, path )

        if not os.path.exists( full_path ):
            return None

        return os.path.isdir( full_path )

    security.declareProtected( ManagePortal, 'listDirectory' )
    def listDirectory( self, path, skip=('CVS',) ):

        """ See IImportContext.
        """
        full_path = os.path.join( self._profile_path, path )

        if not os.path.exists( full_path ) or not os.path.isdir( full_path ):
            return None

        names = os.listdir( full_path )

        return [ name for name in names if name not in skip ]

    security.declareProtected( ManagePortal, 'shouldPurge' )
    def shouldPurge( self ):

        """ See IImportContext.
        """
        return self._should_purge

InitializeClass( ImportContext )

class ExportContext( Implicit ):

    __implements__ = ( IExportContext, )

    security = ClassSecurityInfo()

    def __init__( self, tool, profile_path ):

        self._site = aq_parent( aq_inner( tool ) )
        self._profile_path = profile_path

    security.declareProtected( ManagePortal, 'getSite' )
    def getSite( self ):

        """ See ISetupContext.
        """
        return self._site

    security.declareProtected( ManagePortal, 'writeDataFile' )
    def writeDataFile( self, filename, text, content_type, subdir=None ):

        """ See IExportContext.
        """
        if subdir is None:
            prefix = self._profile_path
        else:
            prefix = os.path.join( self._profile_path, subdir )

        full_path = os.path.join( prefix, filename )

        if not os.path.exists( prefix ):
            os.makedirs( prefix )

        mode = content_type.startswith( 'text/' ) and 'w' or 'wb'

        file = open( full_path, mode )
        file.write( text )
        file.close()

InitializeClass( ExportContext )

class TarballExportContext( Implicit ):

    __implements__ = ( IExportContext, )

    security = ClassSecurityInfo()

    def __init__( self, tool ):

        self._site = aq_parent( aq_inner( tool ) )
        timestamp = time.gmtime()
        archive_name = ( 'portal_setup-%4d%02d%02d%02d%02d%02d.tar.gz'
                       % timestamp[:6] )

        self._archive_stream = StringIO()
        self._archive_filename = archive_name
        self._archive = TarFile.open( archive_name, 'w:gz'
                                    , self._archive_stream )

    security.declareProtected( ManagePortal, 'getSite' )
    def getSite( self ):

        """ See ISetupContext.
        """
        return self._site

    security.declareProtected( ManagePortal, 'writeDataFile' )
    def writeDataFile( self, filename, text, content_type, subdir=None ):

        """ See IExportContext.
        """
        if subdir is not None:
            filename = os.path.join( subdir, filename )

        stream = StringIO( text )
        info = TarInfo( filename )
        info.size = len( text )
        self._archive.addfile( info, stream )

    security.declareProtected( ManagePortal, 'getArchive' )
    def getArchive( self ):

        """ Close the archive, and return it as a big string.
        """
        self._archive.close()
        return self._archive_stream.getvalue()

    security.declareProtected( ManagePortal, 'getArchiveFilename' )
    def getArchiveFilename( self ):

        """ Close the archive, and return it as a big string.
        """
        return self._archive_filename

InitializeClass( TarballExportContext )

class SnapshotExportContext( Implicit ):

    __implements__ = ( IExportContext, )

    security = ClassSecurityInfo()

    def __init__( self, tool, snapshot_id ):

        self._tool = tool = aq_inner( tool )
        self._site = aq_parent( tool )
        self._snapshot_id = snapshot_id

    security.declareProtected( ManagePortal, 'getSite' )
    def getSite( self ):

        """ See ISetupContext.
        """
        return self._site

    security.declareProtected( ManagePortal, 'writeDataFile' )
    def writeDataFile( self, filename, text, content_type, subdir=None ):

        """ See IExportContext.
        """
        folder = self._ensureSnapshotsFolder( subdir )

        # TODO: switch on content_type
        ob = self._createObjectByType( filename, text, content_type )
        folder._setObject( filename, ob )

    security.declareProtected( ManagePortal, 'getSnapshotURL' )
    def getSnapshotURL( self ):

        """ See IExportContext.
        """
        return '%s/%s' % ( self._tool.absolute_url(), self._snapshot_id )

    security.declareProtected( ManagePortal, 'getSnapshotFolder' )
    def getSnapshotFolder( self ):

        """ See IExportContext.
        """
        return self._ensureSnapshotsFolder()

    #
    #   Helper methods
    #
    security.declarePrivate( '_createObjectByType' )
    def _createObjectByType( self, name, body, content_type ):

        if name.endswith('.py'):

            ob = PythonScript( name )
            ob.write( body )

        elif name.endswith('.dtml'):

            ob = DTMLDocument( '', __name__=name )
            ob.munge( body )

        elif content_type in ('text/html', 'text/xml' ):

            ob = ZopePageTemplate( name, str( body )
                                 , content_type=content_type )

        elif content_type[:6]=='image/':

            ob=Image( name, '', body, content_type=content_type )

        else:
            ob=File( name, '', body, content_type=content_type )

        return ob

    security.declarePrivate( '_ensureSnapshotsFolder' )
    def _ensureSnapshotsFolder( self, subdir=None ):

        """ Ensure that the appropriate snapshot folder exists.
        """
        path = [ 'snapshots', self._snapshot_id ]

        if subdir is not None:
            path.extend( subdir.split( '/' ) )

        current = self._tool

        for element in path:

            if element not in current.objectIds():
                current._setObject( element, Folder( element ) )

            current = current._getOb( element )

        return current


InitializeClass( SnapshotExportContext )
