import Zope
import unittest
import re
from Products.CMFCore.ContentTypeRegistry import *

class MajorMinorPredicateTests( unittest.TestCase ):

    def test_empty( self ):
        pred = MajorMinorPredicate( 'empty' )
        assert pred.getMajorType() == 'None'
        assert pred.getMinorType() == 'None'
        assert not pred( 'foo', 'text/plain', 'asdfljksadf' )

    def test_simple( self ):
        pred = MajorMinorPredicate( 'plaintext' )
        pred.edit( 'text', 'plain' )
        assert pred.getMajorType() == 'text'
        assert pred.getMinorType() == 'plain'
        assert pred( 'foo', 'text/plain', 'asdfljksadf' )
        assert not pred( 'foo', 'text/html', 'asdfljksadf' )

    def test_wildcard( self ):
        pred = MajorMinorPredicate( 'alltext' )
        pred.edit( 'text', '' )
        assert pred.getMajorType() == 'text'
        assert pred.getMinorType() == ''
        assert pred( 'foo', 'text/plain', 'asdfljksadf' )
        assert pred( 'foo', 'text/html', 'asdfljksadf' )
        assert not pred( 'foo', 'image/png', 'asdfljksadf' )

        pred.edit( '', 'html' )
        assert pred.getMajorType() == ''
        assert pred.getMinorType() == 'html'
        assert not pred( 'foo', 'text/plain', 'asdfljksadf' )
        assert pred( 'foo', 'text/html', 'asdfljksadf' )
        assert not pred( 'foo', 'image/png', 'asdfljksadf' )

class ExtensionPredicateTests( unittest.TestCase ):

    def test_empty( self ):
        pred = ExtensionPredicate( 'empty' )
        assert pred.getExtensions() == 'None'
        assert not pred( 'foo', 'text/plain', 'asdfljksadf' )
        assert not pred( 'foo.txt', 'text/plain', 'asdfljksadf' )
        assert not pred( 'foo.bar', 'text/html', 'asdfljksadf' )

    def test_simple( self ):
        pred = ExtensionPredicate( 'stardottext' )
        pred.edit( 'txt' )
        assert pred.getExtensions() == 'txt'
        assert not pred( 'foo', 'text/plain', 'asdfljksadf' )
        assert pred( 'foo.txt', 'text/plain', 'asdfljksadf' )
        assert not pred( 'foo.bar', 'text/html', 'asdfljksadf' )

    def test_multi( self ):
        pred = ExtensionPredicate( 'stardottext' )
        pred.edit( 'txt text html htm' )
        assert pred.getExtensions() == 'txt text html htm'
        assert not pred( 'foo', 'text/plain', 'asdfljksadf' )
        assert pred( 'foo.txt', 'text/plain', 'asdfljksadf' )
        assert pred( 'foo.text', 'text/plain', 'asdfljksadf' )
        assert pred( 'foo.html', 'text/plain', 'asdfljksadf' )
        assert pred( 'foo.htm', 'text/plain', 'asdfljksadf' )
        assert not pred( 'foo.bar', 'text/html', 'asdfljksadf' )

class MimeTypeRegexPredicateTests( unittest.TestCase ):

    def test_empty( self ):
        pred = MimeTypeRegexPredicate( 'empty' )
        assert pred.getPatternStr() == 'None'
        assert not pred( 'foo', 'text/plain', 'asdfljksadf' )

    def test_simple( self ):
        pred = MimeTypeRegexPredicate( 'plaintext' )
        pred.edit( 'text/plain' )
        assert pred.getPatternStr() == 'text/plain'
        assert pred( 'foo', 'text/plain', 'asdfljksadf' )
        assert not pred( 'foo', 'text/html', 'asdfljksadf' )

    def test_pattern( self ):
        pred = MimeTypeRegexPredicate( 'alltext' )
        pred.edit( 'text/*' )
        assert pred.getPatternStr() == 'text/*'
        assert pred( 'foo', 'text/plain', 'asdfljksadf' )
        assert pred( 'foo', 'text/html', 'asdfljksadf' )
        assert not pred( 'foo', 'image/png', 'asdfljksadf' )
    
class NameRegexPredicateTests( unittest.TestCase ):

    def test_empty( self ):
        pred = NameRegexPredicate( 'empty' )
        assert pred.getPatternStr() == 'None'
        assert not pred( 'foo', 'text/plain', 'asdfljksadf' )

    def test_simple( self ):
        pred = NameRegexPredicate( 'onlyfoo' )
        pred.edit( 'foo' )
        assert pred.getPatternStr() == 'foo'
        assert pred( 'foo', 'text/plain', 'asdfljksadf' )
        assert not pred( 'fargo', 'text/plain', 'asdfljksadf' )
        assert not pred( 'bar', 'text/plain', 'asdfljksadf' )

    def test_pattern( self ):
        pred = NameRegexPredicate( 'allfwords' )
        pred.edit( 'f.*' )
        assert pred.getPatternStr() == 'f.*'
        assert pred( 'foo', 'text/plain', 'asdfljksadf' )
        assert pred( 'fargo', 'text/plain', 'asdfljksadf' )
        assert not pred( 'bar', 'text/plain', 'asdfljksadf' )
    
class ContentTypeRegistryTests( unittest.TestCase ):

    def test_empty( self ):
        reg = ContentTypeRegistry()
        assert reg.findTypeName( 'foo', 'text/plain', 'asdfljksadf' ) is None
        assert reg.findTypeName( 'fargo', 'text/plain', 'asdfljksadf' ) is None
        assert reg.findTypeName( 'bar', 'text/plain', 'asdfljksadf' ) is None
        assert not reg.listPredicates()
        self.assertRaises( KeyError, reg.removePredicate, 'xyzzy' )
    
    def test_reorder( self ):
        reg = ContentTypeRegistry()
        predIDs = ( 'foo', 'bar', 'baz', 'qux' )
        for predID in predIDs:
            reg.addPredicate( predID, 'name' )
        ids = tuple( map( lambda x: x[0], reg.listPredicates() ) )
        assert ids == predIDs
        reg.reorderPredicate( 'bar', 3 )
        ids = tuple( map( lambda x: x[0], reg.listPredicates() ) )
        assert ids == ( 'foo', 'baz', 'qux', 'bar' )

    def test_lookup( self ):
        reg = ContentTypeRegistry()
        reg.addPredicate( 'onlyfoo', 'name' )
        reg.getPredicate( 'onlyfoo' ).edit( 'foo' )
        reg.assignTypeName( 'onlyfoo', 'Foo' )
        assert reg.findTypeName( 'foo', 'text/plain', 'asdfljksadf' ) == 'Foo'
        assert not reg.findTypeName( 'fargo', 'text/plain', 'asdfljksadf' )
        assert not reg.findTypeName( 'bar', 'text/plain', 'asdfljksadf' )

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite( MajorMinorPredicateTests ) )
    suite.addTest( unittest.makeSuite( ExtensionPredicateTests ) )
    suite.addTest( unittest.makeSuite( MimeTypeRegexPredicateTests ) )
    suite.addTest( unittest.makeSuite( NameRegexPredicateTests ) )
    suite.addTest( unittest.makeSuite( ContentTypeRegistryTests ) )
    return suite

def run():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    run()
