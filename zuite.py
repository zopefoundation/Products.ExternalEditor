""" Classes:  Zuite

Zuite instances are collections of Zelenium test cases.

$Id$
"""
import os
from urllib import unquote
import zipfile
import StringIO

from AccessControl.SecurityInfo import ClassSecurityInfo
from App.special_dtml import DTMLFile
from DateTime.DateTime import DateTime
from Globals import package_home
from Globals import InitializeClass
from OFS.Folder import Folder
from OFS.Image import File
from OFS.OrderedFolder import OrderedFolder
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from permissions import ManageSeleniumTestCases
from permissions import View

_NOW = None   # set only for testing

def _getNow():
    if _NOW is not None:
        return _NOW

    return DateTime()

_WWW_DIR = os.path.join( package_home( globals() ), 'www' )

#
#   Selenium support files.
#
_SUPPORT_DIR = os.path.join( package_home( globals() ), 'selenium' )

# TODO:  generate this list dynamically from the selenium sources!
_SUPPORT_FILE_NAMES = [ 'html-xpath-patched.js'
                      , 'selenium-browserbot.js'
                      , 'selenium-api.js'
                      , 'selenium-commandhandlers.js'
                      , 'selenium-executionloop.js'
                      , 'selenium-executioncontext.js'
                      , 'selenium-fitrunner.js'
                      , 'selenium-logging.js'
                      , 'htmlutils.js'
                      , 'selenium-domviewer.js'
                      , 'selenium.css'
                      , 'domviewer.html'
                      , 'selenium-logo.png'
                      ]

def _makeFile(filename):
    path = os.path.join(_SUPPORT_DIR, filename)
    return File(id=filename, title='', file=open(path).read())

_SUPPORT_FILES = dict( [ ( x, _makeFile(x) )
                            for x in _SUPPORT_FILE_NAMES ] )

_MARKER = object()

class Zuite( OrderedFolder ):
    """ TTW-manageable browser test suite

    A Zuite instance is an ordered folder, whose 'index_html' provides the
    typical "TestRunner.html" view from Selenium.  It generates the
    "TestSuite.html" view from its 'objectItems' list (which allows the
    user to control ordering), selecting File and PageTemplate objects
    whose names start with 'test'.
    """
    meta_type = 'Zuite'

    manage_options = ( OrderedFolder.manage_options
                     + ( { 'label' : 'Zip', 'action' : 'manage_zipfile' },
                       )
                     )

    test_case_metatypes = ( 'File'
                          , 'Page Template'
                          )

    _properties = ( { 'id' : 'test_case_metatypes'
                    , 'type' : 'lines'
                    , 'mode' : 'w'
                    },
                  )

    security = ClassSecurityInfo()
    security.declareObjectProtected( View )

    security.declareProtected( ManageSeleniumTestCases, 'manage_main' )
    manage_main = DTMLFile( 'suiteMain', _WWW_DIR )

    security.declareProtected( View, 'index_html' )
    index_html = PageTemplateFile( 'suiteView', _WWW_DIR )

    security.declareProtected( View, 'test_suite_html' )
    test_suite_html = PageTemplateFile( 'suiteTests', _WWW_DIR )

    security.declareProtected( View, 'splash_html' )
    splash_html = PageTemplateFile( 'suiteSplash', _WWW_DIR )

    security.declareProtected( View, 'listTestCases' )
    def listTestCases( self, prefix=() ):
        """ Return a list of our contents which qualify as test cases.
        """
        result = []
        types = [ self.meta_type ]
        types.extend( self.test_case_metatypes )
        for tcid, test_case in self.objectItems( types ):
            if isinstance(test_case, self.__class__):
                result.extend( test_case.listTestCases(
                                        prefix=prefix + ( tcid, ) ) )
            else:
                path = '/'.join( prefix + ( tcid, ) )
                result.append( { 'id' : tcid
                               , 'title' : test_case.title_or_id()
                               , 'url' : path
                               , 'path' : path
                               , 'test_case' : test_case
                               } )
        return result


    def __getitem__( self, key, default=_MARKER ):

        if key in self.objectIds():
            return self._getOb( key )

        if key in _SUPPORT_FILE_NAMES:
            return _SUPPORT_FILES[ key ].__of__( self )

        if default is not _MARKER:
            return default

        raise KeyError, key


    security.declarePrivate('_listProductInfo')
    def _listProductInfo( self ):
        """ Return a list of strings of form '%(name)s %(version)s'.

        o Each line describes one product installed in the Control_Panel.
        """
        result = []
        cp = self.getPhysicalRoot().Control_Panel
        products = cp.Products.objectItems()
        products.sort()

        for product_name, product in products:
            version = product.version or 'unreleased'
            result.append( '%s %s' % ( product_name, version ) )

        return result

 
    security.declareProtected(ManageSeleniumTestCases, 'manage_zipfile')
    manage_zipfile = PageTemplateFile( 'suiteZipFile', _WWW_DIR )

    security.declareProtected(ManageSeleniumTestCases, 'getZipFileName')
    def getZipFileName(self):
        """ Generate a suitable name for the zip file.
        """
        now = _getNow()
        now_str = now.ISO()[:10]
        return '%s-%s.zip' % ( self.getId(), now_str )


    security.declareProtected(ManageSeleniumTestCases, 'manage_getZipFile')
    def manage_getZipFile(self, archive_name=None, RESPONSE=None):
        """ Export the test suite as a zip file.
        """
        if archive_name is None or archive_name.strip() == '':
            archive_name = self.getZipFileName()

        bits = self._getZipFile()

        if RESPONSE is None:
            return bits

        RESPONSE.setHeader('Content-type', 'application/zip')
        RESPONSE.setHeader('Content-length', str( len( bits ) ) )
        RESPONSE.setHeader('Content-disposition',
                            'inline;filename=%s' % archive_name )
        RESPONSE.write(bits)


    security.declareProtected(ManageSeleniumTestCases, 'manage_createSnapshot')
    def manage_createSnapshot(self, archive_name=None, RESPONSE=None):
        """ Save the test suite as a zip file *in the zuite*.
        """
        if archive_name is None or archive_name.strip() == '':
            archive_name = self.getZipFileName()

        archive = File( archive_name, title='', file=self._getZipFile() )
        self._setObject( archive_name, archive )

        if RESPONSE is not None:
            RESPONSE.redirect( '%s/manage_main?manage_tabs_message=%s'
                              % ( self.absolute_url()
                                , 'Snapshot+added'
                                ) )


    security.declarePrivate('_getFilename')
    def _getFilename(self, name):
        """ Convert 'name' to a suitable filename, if needed.
        """
        if '.' not in name:
            return '%s.html' % name

        return name


    security.declarePrivate('_getZipFile')
    def _getZipFile(self):
        """ Generate a zip file containing both tests and scaffolding.
        """
        stream = StringIO.StringIO()
        archive = zipfile.ZipFile( stream, 'w' )

        archive.writestr( 'index.html'
                        , self.index_html( suite_name='testSuite.html' ) )

        test_cases = self.listTestCases()

        # ensure suffixes
        for info in test_cases:
            info[ 'path' ] = self._getFilename( info[ 'path' ] )
            info[ 'url' ] = self._getFilename( info[ 'url' ] )

        archive.writestr( 'testSuite.html'
                        , self.test_suite_html( test_cases=test_cases ) )

        for k, v in _SUPPORT_FILES.items():
            archive.writestr( k, v.manage_FTPget() )

        for info in test_cases:
            test_case = info[ 'test_case' ]

            if getattr( test_case, '__call__', None ) is not None:
                body = test_case()  # XXX: DTML?
            else:
                body = test_case.manage_FTPget()

            archive.writestr( info[ 'path' ]
                            , body
                            )
        archive.close()
        return stream.getvalue()

    security.declarePublic('postResults')
    def postResults(self, REQUEST):
        """ Record the results of a test run.

        o Create a folder with properties representing the summary results,
          and files containing the suite and the individual test runs.

        o REQUEST will have the following form fields:

          result -- one of "failed" or "passed"

          totalTime -- time in floating point seconds for the run

          numTestPasses -- count of test runs which passed

          numTestFailures -- count of test runs which failed

          numCommandPasses -- count of commands which passed

          numCommandFailures -- count of commands which failed

          numCommandErrors -- count of commands raising non-assert errors

          suite -- Colorized HTML of the suite table

          testTable.<n> -- Colorized HTML of each test run
        """
        completed = DateTime()
        result_id = 'result_%s' % completed.strftime( '%Y%m%d_%H%M%S' )
        self._setObject( result_id, ZuiteResults( result_id ) )
        result = self._getOb( result_id )
        rfg = REQUEST.form.get
        reg = REQUEST.environ.get

        result._updateProperty( 'completed'
                              , completed
                              )

        result._updateProperty( 'passed'
                              , rfg( 'result' ).lower() == 'passed'
                              )

        result._updateProperty( 'time_secs'
                              , float( rfg( 'totalTime', 0 ) )
                              )

        result._updateProperty( 'tests_passed'
                              , int( rfg( 'numTestPasses', 0 ) )
                              )

        result._updateProperty( 'tests_failed'
                              , int( rfg( 'numTestFailures', 0 ) )
                              )

        result._updateProperty( 'commands_passed'
                              , int( rfg( 'numCommandPasses', 0 ) )
                              )

        result._updateProperty( 'commands_failed'
                              , int( rfg( 'numCommandFailures', 0 ) )
                              )

        result._updateProperty( 'commands_with_errors'
                              , int( rfg( 'numCommandErrors', 0 ) )
                              )

        result._updateProperty( 'user_agent'
                              , reg( 'HTTP_USER_AGENT', 'unknown' )
                              )

        result._updateProperty( 'remote_addr'
                              , reg( 'REMOTE_ADDR', 'unknown' )
                              )

        result._updateProperty( 'http_host'
                              , reg( 'HTTP_HOST', 'unknown' )
                              )

        result._updateProperty( 'server_software'
                              , reg( 'SERVER_SOFTWARE', 'unknown' )
                              )

        result._updateProperty( 'product_info'
                              , self._listProductInfo()
                              )

        result._setObject( 'suite.html'
                         , File( 'suite.html'
                               , 'Test Suite'
                               , unquote( rfg( 'suite' ) )
                               , 'text/html'
                               )
                         )

        test_ids = [ x for x in REQUEST.form.keys()
                        if x.startswith( 'testTable' ) ]
        test_ids.sort()

        for test_id in test_ids:
            result._setObject( test_id
                             , File( test_id
                                   , 'Test case: %s' % test_id
                                   , unquote( rfg( test_id ) )
                                   , 'text/html'
                                   ) )

InitializeClass( Zuite )


class ZuiteResults( Folder ):

    security = ClassSecurityInfo()
    meta_type = 'Zuite Results'

    _properties = ( { 'id' : 'test_case_metatypes'
                    , 'type' : 'lines'
                    , 'mode' : 'w'
                    },
                    { 'id' : 'completed'
                    , 'type' : 'date'
                    , 'mode' : 'w'
                    },
                    { 'id' : 'passed'
                    , 'type' : 'boolean'
                    , 'mode' : 'w'
                    },
                    { 'id' : 'time_secs'
                    , 'type' : 'float'
                    , 'mode' : 'w'
                    },
                    { 'id' : 'tests_passed'
                    , 'type' : 'int'
                    , 'mode' : 'w'
                    },
                    { 'id' : 'tests_failed'
                    , 'type' : 'int'
                    , 'mode' : 'w'
                    },
                    { 'id' : 'commands_passed'
                    , 'type' : 'int'
                    , 'mode' : 'w'
                    },
                    { 'id' : 'commands_failed'
                    , 'type' : 'int'
                    , 'mode' : 'w'
                    },
                    { 'id' : 'commands_with_errors'
                    , 'type' : 'int'
                    , 'mode' : 'w'
                    },
                    { 'id' : 'user_agent'
                    , 'type' : 'string'
                    , 'mode' : 'w'
                    },
                    { 'id' : 'remote_addr'
                    , 'type' : 'string'
                    , 'mode' : 'w'
                    },
                    { 'id' : 'http_host'
                    , 'type' : 'string'
                    , 'mode' : 'w'
                    },
                    { 'id' : 'server_software'
                    , 'type' : 'string'
                    , 'mode' : 'w'
                    },
                    { 'id' : 'product_info'
                    , 'type' : 'lines'
                    , 'mode' : 'w'
                    },
                  )

    security.declareObjectProtected( View )

    security.declarePublic( 'index_html' )
    index_html = PageTemplateFile( 'resultsView', _WWW_DIR )

InitializeClass( Zuite )

#
#   Factory methods
#
manage_addZuiteForm = PageTemplateFile( 'addZuite', _WWW_DIR )

def manage_addZuite(dispatcher, id, title='', REQUEST=None):
    """ Add a new Zuite to dispatcher's objects.
    """
    zuite = Zuite(id)
    zuite.title = title
    dispatcher._setObject(id, zuite)
    zuite = dispatcher._getOb(id)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect('%s/manage_main'
                                       % zuite.absolute_url() )
