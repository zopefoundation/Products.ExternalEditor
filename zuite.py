""" Classes:  Zuite

$Id$
"""
import os
import zipfile
import StringIO

from AccessControl.SecurityInfo import ClassSecurityInfo
from Globals import package_home
from Globals import InitializeClass
from OFS.Image import File
from OFS.OrderedFolder import OrderedFolder
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

    security = ClassSecurityInfo()
    security.declareObjectProtected(View)

    security.declareProtected(View, 'index_html')
    index_html = PageTemplateFile( 'suiteView', _WWW_DIR )

    security.declareProtected(View, 'test_suite_html')
    test_suite_html = PageTemplateFile( 'suiteTests', _WWW_DIR )

    security.declareProtected(View, 'listTestCases')
    def listTestCases( self ):
        """ Return a list of our contents which qualify as test cases.
        """
        return [ { 'id' : x[ 0 ], 'title' : x[ 1 ].title_or_id() }
                 for x in self.objectItems( [ 'File', 'Page Template' ] )
                      if x[ 0 ].startswith('test') ]

    def __getitem__( self, key, default=_MARKER ):

        if key in self.objectIds():
            return self._getOb( key )

        if key in _SUPPORT_FILE_NAMES:
            return _SUPPORT_FILES[ key ].__of__( self )

        if default is not _MARKER:
            return default

        raise KeyError, key

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
