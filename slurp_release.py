#! /usr/bin/env python2.1
""" Make a CMF release.
"""

import sys
import os
import httplib
import getopt
import base64

CVSROOT = ':pserver:anonymous@cvs.zope.org:/cvs-repository'

class ReleasePackage:

    _release_tag = _version_id = _userid = _password = None

    def __init__( self, args ):

        self._parseArgs( args )
        
    #
    #   Packaging API
    #
    def exportReleaseFiles( self ):

        """ Do the CVS export of CMF for a given release.
        """
        os.system( 'rm -rf %s' % self._version_id )
        command = ( '/usr/bin/cvs -d %s export -r %s -d %s CMF'
                % ( CVSROOT, self._release_tag, self._version_id ) )

        os.system( command )

    def makeArchives( self ):

        """ Create tarball and zipfile for release.
        """
        tar_command = ( '/bin/tar czf %s.tar.gz %s'
                      % ( self._version_id, self._version_id ) )

        zip_command = ( '/usr/bin/zip -r %s.zip %s'
                      % ( self._version_id, self._version_id ) )

        try:
            os.remove( '%s.tar.gz' % self._version_id )
        except OSError:
            pass

        try:
            os.remove( '%s.zip' % self._version_id )
        except OSError:
            pass

        os.system( tar_command )
        os.system( zip_command )

    def uploadArchives( self ):

        """ Upload the tarball / zipfile for the release to the dogbowl.
        """
        tarball  = '%s.tar.gz' % ( self._version_id )
        self._uploadFile( tarball )

        zipfile = '%s.zip' % ( self._version_id )
        self._uploadFile( zipfile )

    def uploadDocs( self ):

        """ Upload the text files for the release to the dogbowl.
        """
        curdir = os.getcwd()
        os.chdir( self._version_id )
        try:
            self._uploadFile( 'CHANGES.txt' )
            self._uploadFile( 'HISTORY.txt' )
            self._uploadFile( 'INSTALL.txt' )
            self._uploadFile( 'LICENSE.txt' )
            self._uploadFile( 'README.txt' )
        finally:
            os.chdir( curdir )

    def doWholeEnchilada( self ):

        """ Run the whole enchilada.
        """
        self.exportReleaseFiles()
        self.makeArchives()
        self.uploadArchives()
        self.uploadDocs()

    def run( self ):
        self._runCommand()
    
    #
    #   Helper methods
    #
    def _usage( self ):

        """ How are we used?
        """
        USAGE = """\
slurp_release [options] release_tag version_id

options:

    -?, -h, --help      Print this usage message

    -x, --execute       Select a particular step (def. 'doWholeEnchilada')
    
    -a, --auth          Use authentication pair, in fmt 'userid:password'
"""
        values = {}
        print USAGE % values
        sys.exit( 2 )

    def _parseArgs( self, args ):

        """ Figure out which release, who, etc?
        """
        command = 'doWholeEnchilada'
        try:
            opts, args = getopt.getopt( args
                                      , '?hx:a:'
                                      , [ 'help'
                                        , 'execute='
                                        , 'auth='
                                        ]
                                      )
        except getopt.GetOptError:
            self._usage()

        for k, v in opts:

            if k == '-?' or k == '-h' or k == '--help':
                self._usage()

            if k == '-x' or k == '--execute':
                command = v

            if k == '-a' or k == '--auth':
                self._userid, self._password = v.split( ':' )

        self._command = command

        if len( args ) != 2:
            self._usage()

        self._release_tag, self._version_id = args

    def _runCommand( self ):

        """ Do the specified command.
        """
        getattr( self, self._command )()

    def _getAuthHeaders( self ):

        """ Return the HTTP headers.
        """
        headers = {}
        if self._userid:
            auth = base64.encodestring( '%s:%s'
                                    % ( self._userid, self._password ) )
            headers[ 'Authorization' ] = 'Basic %s' % auth
        return headers

    def _uploadFile( self, filename ):

        """ Upload the zipfile for the release to the dogbowl.
        """
        URL = ( '/download/%s/%s' % ( self._version_id, filename ) )
        body = open( filename ).read()

        conn = httplib.HTTPConnection( 'cmf.zope.org' )
        print 'PUTting file, %s, to URL, %s' % ( filename, URL )
        conn.request( 'PUT', URL, body, self._getAuthHeaders() )
        response = conn.getresponse()
        if int( response.status ) not in ( 200, 201, 204, 302 ):
            raise ValueError, 'Failed: %s (%s)' % ( response.status
                                                  , response.reason )


if __name__ == '__main__':

    import sys

    pkg = ReleasePackage( sys.argv[1:] )

    pkg.run()
