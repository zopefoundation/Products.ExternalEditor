""" CMFSetup product interfaces

$Id$
"""

from Interface import Interface

class IPseudoInterface( Interface ):

    """ API documentation;  not testable / enforceable.
    """

class ISetupContext( Interface ):

    """ Context used for export / import plugins.
    """
    def getSite():

        """ Return the site object being configured / dumped.
        """

class IImportContext( ISetupContext ):

    def getEncoding():

        """ Return the encoding used in data files.

        o Return None if the data should not be encoded.
        """

    def readDataFile( filename, subdir=None ):

        """ Search the current configuration for the requested file.

        o 'filename' is the name (without path elements) of the file.

        o 'subdir' is an optional subdirectory;  if not supplied, search
          only the "root" directory.

        o Return the file contents as a string, or None if the
          file cannot be found.
        """

    def getLastModified( path ):

        """ Return the modification timestamp of the item at 'path'.

        o Search profiles in the configuration in order.

        o If the context is filesystem based, return the 'stat' timestamp
          of the file / directory to which 'path' points.

        o If the context is ZODB-based, return the Zope modification time
          of the object to which 'path' points.

        o Return None if 'path' does not point to any object.
        """

    def isDirectory( path ):

        """ Test whether path points to a directory / folder.

        o If the context is filesystem based, check that 'path' points to
          a subdirectory within the "root" directory.

        o If the context is ZODB-based, check that 'path' points to a
          "container" under the context's tool.

        o Return None if 'path' does not resolve;  otherwise, return a
          bool.
        """

    def listDirectory( path, skip=('CVS',) ):

        """ List IDs of the contents of a  directory / folder.

        o Omit names in 'skip'.

        o If 'path' does not point to a directory / folder, return None.
        """

    def shouldPurge():

        """ When installing, should the existing setup be purged?
        """

class IImportPlugin( IPseudoInterface ):

    """ Signature for callables used to import portions of site configuration.
    """
    def __call__( context ):

        """ Perform the setup step.

        o Return a message describing the work done.

        o 'context' must implement IImportContext.
        """

class IExportContext( ISetupContext ):

    def writeDataFile( filename, text, content_type, subdir=None ):

        """ Write data into the specified location.

        o 'filename' is the unqualified name of the file.

        o 'text' is the content of the file.

        o 'content_type' is the MIMEtype of the file.

        o 'subdir', if passed, is a path to a subdirectory / folder in
          which to write the file;  if not passed, write the file to the
          "root" of the target.
        """

class IExportPlugin( IPseudoInterface ):

    """ Signature for callables used to export portions of site configuration.
    """
    def __call__( context ):

        """ Write export data for the site wrapped by context.

        o Return a message describing the work done.

        o 'context' must implement IExportContext.  The plugin will use
          its 'writeDataFile' method for each file to be exported.
        """

class IStepRegistry( Interface ):

    """ Base interface for step registries.
    """
    def listSteps():

        """ Return a sequence of IDs of registered steps.

        o Order is not significant.
        """

    def listStepMetadata():

        """ Return a sequence of mappings describing registered steps.

        o Mappings will be ordered alphabetically.
        """

    def getStepMetadata( key, default=None ):

        """ Return a mapping of metadata for the step identified by 'key'.

        o Return 'default' if no such step is registered.

        o The 'handler' metadata is available via 'getStep'.
        """

    def generateXML():

        """ Return a round-trippable XML representation of the registry.

        o 'handler' values are serialized using their dotted names.
        """

    def parseXML( text ):

        """ Parse 'text' into a clean registry.
        """

class IImportStepRegistry( IStepRegistry ):

    """ API for import step registry.
    """
    def sortSteps():

        """ Return a sequence of registered step IDs
        
        o Sequence is sorted topologically by dependency, with the dependent
          steps *after* the steps they depend on.
        """

    def checkComplete():

        """ Return a sequence of ( node, edge ) tuples for unsatisifed deps.
        """

    def getStep( key, default=None ):

        """ Return the IImportPlugin registered for 'key'.

        o Return 'default' if no such step is registered.
        """

    def registerStep( id
                    , version
                    , handler
                    , dependencies=()
                    , title=None
                    , description=None
                    ):
        """ Register a setup step.

        o 'id' is a unique name for this step,

        o 'version' is a string for comparing versions, it is preferred to
          be a yyyy/mm/dd-ii formatted string (date plus two-digit
          ordinal).  when comparing two version strings, the version with
          the lower sort order is considered the older version.
          
          - Newer versions of a step supplant older ones.

          - Attempting to register an older one after a newer one results
            in a KeyError.

        o 'handler' should implement IImportPlugin.

        o 'dependencies' is a tuple of step ids which have to run before
          this step in order to be able to run at all. Registration of
          steps that have unmet dependencies are deferred until the
          dependencies have been registered.

        o 'title' is a one-line UI description for this step.
          If None, the first line of the documentation string of the handler
          is used, or the id if no docstring can be found.

        o 'description' is a one-line UI description for this step.
          If None, the remaining line of the documentation string of
          the handler is used, or default to ''.
        """

class IExportStepRegistry( IStepRegistry ):

    """ API for export step registry.
    """
    def getStep( key, default=None ):

        """ Return the IExportPlugin registered for 'key'.

        o Return 'default' if no such step is registered.
        """

    def registerStep( id, handler, title=None, description=None ):

        """ Register an export step.

        o 'id' is the unique identifier for this step

        o 'handler' should implement IExportPlugin.

        o 'title' is a one-line UI description for this step.
          If None, the first line of the documentation string of the step
          is used, or the id if no docstring can be found.

        o 'description' is a one-line UI description for this step.
          If None, the remaining line of the documentation string of
          the step is used, or default to ''.
        """

class IToolsetRegistry( Interface ):

    """ API for toolset registry.
    """
    def listForbiddenTools():

        """ Return a list of IDs of tools which must be removed, if present.
        """

    def addForbiddenTool(tool_id ):

        """ Add 'tool_id' to the list of forbidden tools.

        o Raise KeyError if 'tool_id' is already in the list.

        o Raise ValueError if 'tool_id' is in the "required" list.
        """

    def listRequiredTools():

        """ Return a list of IDs of tools which must be present.
        """

    def getRequiredToolInfo( tool_id ):

        """ Return a mapping describing a partiuclar required tool.

        o Keys include:

          'id' -- the ID of the tool

          'class' -- a dotted path to its class

        o Raise KeyError if 'tool_id' id not a known tool.
        """

    def listRequiredToolInfo():

        """ Return a list of IDs of tools which must be present.
        """

    def addRequiredTool( tool_id, dotted_name ):

        """ Add a tool to our "required" list.

        o 'tool_id' is the tool's ID.

        o 'dotted_name' is a dotted (importable) name of the tool's class.

        o Raise KeyError if we have already registered a class for 'tool_id'.

        o Raise ValueError if 'tool_id' is in the "forbidden" list.
        """

class IProfileRegistry( Interface ):

    """ API for profile registry.
    """
    def getProfileInfo( profile_id ):

        """ Return a mapping describing a registered filesystem profile.

        o Keys include:

          'id' -- the ID of the profile

          'title' -- its title

          'description' -- a textual description of the profile

          'path' -- a path to the profile on the filesystem.
        """

    def listProfiles():

        """ Return a list of IDs for registered profiles.
        """

    def listProfileInfo():

        """ Return a list of mappings describing registered profiles.

        o See 'getProfileInfo' for a description of the mappings' keys.
        """

    def registerProfile( profile_id
                       , title
                       , description
                       , path
                       ):
        """ Add a new profile to tne registry.

        o If an existing profile is already registered for 'profile_id',
          raise KeyError.
        """

class ISetupTool( Interface ):

    """ API for SetupTool.
    """

    def getProfileProduct():

        """ Return the name of the product defining our current profile.

        o Return None if the current profile is not relative to a product.
        """

    def getProfileDirectory( relative_to_product=False ):

        """ Return the path to the directory containing profile information.

        o If 'relative_to_product', return it relative to the root directory
          of our profile product.
        """

    def setProfileDirectory( path, product_name=None ):

        """ Set the path to the directory containing profile information.

        o If 'product_name' is not None, compute the fully-qualified path
          relative to the product's root directory.

        o Update the import and export step registries from that directory.
        """

    def getImportStepRegistry():

        """ Return the IImportStepRegistry for the tool.
        """

    def getExportStepRegistry():

        """ Return the IExportStepRegistry for the tool.
        """

    def getToolsetRegistry():

        """ Return the IToolsetRegistry for the tool.
        """

    def runImportStep( step_id, purge_old=True, run_dependencies=True ):

        """ Execute a given setup step
        
        o 'step_id' is the ID of the step to run.

        o If 'purge_old' is True, then run the step after purging any
          "old" setup first (this is the responsibility of the step,
          which must check the context we supply).

        o If 'run_dependencies' is True, then run any out-of-date
          dependency steps first.

        o Return a mapping, with keys:

          'steps' -- a sequence of IDs of the steps run.

          'messages' -- a dictionary holding messages returned from each
            step
        """

    def runAllImportSteps( purge_old=True ):

        """ Run all setup steps in dependency order.

        o If 'purge_old' is True, then run each step after purging any
          "old" setup first (this is the responsibility of the step,
          which must check the context we supply).

        o Return a mapping, with keys:

          'steps' -- a sequence of IDs of the steps run.

          'messages' -- a dictionary holding messages returned from each
            step
        """

    def runExportStep( step_id ):

        """ Generate a tarball containing artifacts from one export step.

        o 'step_id' identifies the export step.

        o Return a mapping, with keys:

          'steps' -- a sequence of IDs of the steps run.

          'messages' -- a dictionary holding messages returned from each
            step

          'tarball' -- the stringified tar-gz data.
        """

    def runAllExportSteps():

        """ Generate a tarball containing artifacts from all export steps.

        o Return a mapping, with keys:

          'steps' -- a sequence of IDs of the steps run.

          'messages' -- a dictionary holding messages returned from each
            step

          'tarball' -- the stringified tar-gz data.
        """

    def createSnapshot( snapshot_id ):

        """ Create a snapshot folder using all steps.

        o 'snapshot_id' is the ID of the new folder.
        """

    def compareConfigurations( lhs_id
                             , rhs_id
                             , missing_as_empty=False
                             , ignore_whitespace=False
                             ):
        """ Compare two configurations.

        o 'lhs_id' and 'rhs_id', if None, refer to the "default" filesystem
          configuration.

        o Otherwise, 'lhs_id' and 'rhs_id' refer to snapshots.

        o If 'missing_as_empty', then compare files not present as though
          they were zero-length;  otherwise, omit such files.

        o If 'ignore_whitespace', then suppress diffs due only to whitespace
          (c.f:  'diff -wbB')
        """
