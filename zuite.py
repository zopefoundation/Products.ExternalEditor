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

_WWW_DIR = os.path.join( package_home( globals() ), 'www' )

#
#   Selenium support files.
#
_SUPPORT_DIR = os.path.join( package_home( globals() ), 'selenium' )

# TODO:  generate this list dynamically from the selenium sources!
_SUPPORT_FILE_NAMES = [ 'htmlutils.js'
                      , 'html-xpath-patched.js'
                      , 'jsUnitCore.js'
                      , 'selenium.css'
                      , 'selenium-api.js'
                      , 'selenium-browserbot.js'
                      , 'selenium-commandhandlers.js'
                      , 'selenium-executionloop.js'
                      , 'selenium-fitrunner.js'
                      ]

_RESULT_HTML = """\
<html>
<head>
<title tal:content="context/completed/ISO"
>Test result: YYYY-MM-DDTHH:MM:SS</title>
</head>
<body>

<h1> Test Result: <tal:x replace="context/completed/ISO" /></h1>

<h2> Test Summary </h2>

<table border="1" cellpadding="2">

 <tr>
  <th align="left">Status</th>
  <td>
    <span style="color: green"
          tal:condition="context/passed">PASSED</span>
    <span style="color: red"
          tal:condition="not: context/passed">FAILED</span>
  </td>
 </tr>

 <tr>
  <th align="left">Elapsed time (sec)</th>
  <td align="right"
      tal:content="context/time_secs">20</td>
 </tr>

 <tr>
  <th align="left">Tests passed</th>
  <td align="right" style="color: green"
      tal:content="context/tests_passed">20</td>
 </tr>

 <tr>
  <th align="left">Tests failed</th>
  <td align="right" style="color: red"
      tal:content="context/tests_failed">20</td>
 </tr>

 <tr>
  <th align="left">Commands passed</th>
  <td align="right" style="color: green"
      tal:content="context/commands_passed">20</td>
 </tr>

 <tr>
  <th align="left">Commands failed</th>
  <td align="right" style="color: red"
      tal:content="context/commands_failed">20</td>
 </tr>

 <tr>
  <th align="left">Commands with errors</th>
  <td align="right" style="color: orange"
      tal:content="context/commands_with_errors">20</td>
 </tr>

</table>
 
<h2> Test Cases </h2>

<div style="padding-top: 10px;"
     tal:repeat="item python:context.objectItems(['File'])">

 <div tal:condition="python: item[0].startswith('testTable')"
      tal:replace="structure python: item[1]" />
</div>

<h2> Remote Client Data </h2>

<table border="1" cellpadding="2">

 <tr>
  <th align="left">User agent</th>
  <td tal:content="context/user_agent">lynx/2.8</td>
 </tr>

 <tr>
  <th align="left">Remote address</th>
  <td tal:content="context/remote_addr">127.0.0.1</td>
 </tr>

 <tr>
  <th align="left">HTTP Host</th>
  <td tal:content="context/http_host">localhost</td>
 </tr>

</table>

<h2> Software Under Test </h2>

<table border="1" cellpadding="2">

 <tr>
  <th align="left">Server Software</th>
  <td tal:content="context/server_software">localhost</td>
 </tr>

 <tbody tal:repeat="product_line context/product_info">
  <tr tal:define="tokens product_line/split;
                  product_name python:tokens[0];
                  product_version python:tokens[1];
                 ">
   <th align="left"
       tal:content="string:Product: ${product_name}">PRODUCT_NAME</th>
   <td tal:content="product_version">PRODUCT_VERSION</td>
  </tr>
 </tbody>

</table>

</body>
</html>
"""

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


    security.declareProtected( View, 'listTestCases' )
    def listTestCases( self ):
        """ Return a list of our contents which qualify as test cases.
        """
        return [ { 'id' : x[ 0 ], 'title' : x[ 1 ].title_or_id() }
                 for x in self.objectItems( self.test_case_metatypes )
                      if x[ 0 ].startswith('test') ]


    def __getitem__( self, key, default=_MARKER ):

        if key in self.objectIds():
            return self._getOb( key )

        if key in _SUPPORT_FILE_NAMES:
            return _SUPPORT_FILES[ key ].__of__( self )

        if default is not _MARKER:
            return default

        raise KeyError, key


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
        self._setObject( result_id, Folder( 'result_id' ) )
        result = self._getOb( result_id )
        rfg = REQUEST.form.get
        reg = REQUEST.environ.get

        result._setProperty( 'completed'
                           , completed
                           , 'date'
                           )

        result._setProperty( 'passed'
                           , rfg( 'result' ).lower() == 'passed'
                           , 'boolean'
                           )

        result._setProperty( 'time_secs'
                           , float( rfg( 'totalTime', 0 ) )
                           , 'float'
                           )

        result._setProperty( 'tests_passed'
                           , int( rfg( 'numTestPasses', 0 ) )
                           , 'int'
                           )

        result._setProperty( 'tests_failed'
                           , int( rfg( 'numTestFailures', 0 ) )
                           , 'int'
                           )

        result._setProperty( 'commands_passed'
                           , int( rfg( 'numCommandPasses', 0 ) )
                           , 'int'
                           )

        result._setProperty( 'commands_failed'
                           , int( rfg( 'numCommandFailures', 0 ) )
                           , 'int'
                           )

        result._setProperty( 'commands_with_errors'
                           , int( rfg( 'numCommandErrors', 0 ) )
                           , 'int'
                           )

        result._setProperty( 'user_agent'
                           , reg( 'HTTP_USER_AGENT', 'unknown' )
                           , 'string'
                           )

        result._setProperty( 'remote_addr'
                           , reg( 'REMOTE_ADDR', 'unknown' )
                           , 'string'
                           )

        result._setProperty( 'http_host'
                           , reg( 'HTTP_HOST', 'unknown' )
                           , 'string'
                           )

        result._setProperty( 'server_software'
                           , reg( 'SERVER_SOFTWARE', 'unknown' )
                           , 'string'
                           )

        result._setProperty( 'product_info'
                           , self._listProductInfo()
                           , 'lines'
                           )

        result._setObject( 'index_html'
                         , ZopePageTemplate('index_html'
                                           , _RESULT_HTML
                                           , 'text/html'
                                           )
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
        now = self.ZopeTime()
        now_str = now.strftime( '%Y-%m-%d' )
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

        test_cases = [ { 'id' :  self._getFilename( k )
                       , 'title' : v.title_or_id()
                       , 'data' : v.manage_FTPget()
                       } for ( k, v ) in self.objectItems( [ 'File'
                                                           , 'Page Template'
                                                           ] ) ]

        archive.writestr( 'testSuite.html'
                        , self.test_suite_html( test_cases=test_cases ) )

        for k, v in _SUPPORT_FILES.items():
            archive.writestr( k, v.manage_FTPget() )

        for test_case in test_cases:
            archive.writestr( test_case[ 'id' ]
                            , test_case[ 'data' ] )

        archive.close()
        return stream.getvalue()


InitializeClass(Zuite)

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
