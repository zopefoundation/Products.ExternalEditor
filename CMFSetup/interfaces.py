""" CMFSetup product interfaces

$Id$
"""

from Interface import Interface

class ISetupContext( Interface ):

    """ Context used for export / import plugins.
    """
    def getSite():

        """ Return the site object being configured / dumped.
        """

class IImportContext( ISetupContext ):

    def readDatafile( filename, subdir=None ):

        """ Search the current configuration for the requested file.

        o Search each profile in the configuration in order.

        o 'filename' is the name (without path elements) of the file.

        o 'subdir' is an optional subdirectory;  if not supplied, search
          only the "root" directory of each configured profile.

        o Return the file contents as a string, or None if the
          file cannot be found.
        """

    def getLastModified( path ):

        """ Return the modification timestamp of the item at 'path'.

        o Search profiles in the configuration in order.

        o If the profile is filesystem based, return the 'stat' timestamp
          of the file / directory to which 'path' points.

        o If the profile is ZODB-based, return the Zopd modification time
          of the object to which 'path' points.

        o Return None if 'path' does not point to any object in any profile.
        """

    def isDirectory( path ):

        """ Test whether path points to a directory / folder in a profile

        o If the profile is filesystem based, check that 'path' points to
          a subdirectory within the "root" directory of the profile.

        o If the profile is ZODB-based, check that 'path' points to a
          "container" under the profile.
        """

    def listDirectory( path, skip=('CVS',) ):

        """ List IDs of the contents of a profile directory / folder.

        o Omit names in 'skip'.
        """

    def shouldPurge():

        """ When installing, should the existing setup be purged?
        """

def IExportContext( ISetupContext ):

    def writeDataFile( filename, text, content_type, subdir=None ):

        """ Write data into the specified location.

        o 'filename' is the unqualified name of the file.

        o 'text' is the content of the file.

        o 'content_type' is the MIMEtype of the file.

        o 'subdir', if passed, is a path to a subdirectory / folder in
          which to write the file;  if not passed, write the file to the
          "root" of the target.
        """


class IPseudoInterface( Interface ):

    """ API documentation;  not testable / enforceable.
    """


class IImportPlugin( IPseudoInterface ):

    """ API for initializing / configuring a site from a profile.

    o 'context' must implement IImportContext.
    """
    def __call__( context ):

        """ Use data from 'context' to do initialization / configuration.
        """

class IExportPlugin( IPseudoInterface ):

    """ API for exporting a site to a serialization.
    """
    def __call__( context ):

        """ Use data from 'context' to do initialization / configuration.

        o 'context' must implement IExportContext.
        """
