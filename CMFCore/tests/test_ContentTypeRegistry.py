import Zope
import unittest
from Products.CMFCore.ContentTypeRegistry import *

class MimeTypePredicateTests( unittest.TestCase ):

    def test_empty( self ):
        pred = MimeTypePredicate( 'empty' )
        assert pred.getPatternStr() == 'None'
        assert not pred( 'foo', 'text/plain', 'asdfljksadf' )

    def test_simple( self ):
        pred = MimeTypePredicate( 'plaintext' )
        pred.edit( 'text/plain' )
        assert pred.getPatternStr() == 'text/plain'
        assert pred( 'foo', 'text/plain', 'asdfljksadf' )
        assert not pred( 'foo', 'text/html', 'asdfljksadf' )

    def test_pattern( self ):
        pred = MimeTypePredicate( 'alltext' )
        pred.edit( 'text/*' )
        assert pred.getPatternStr() == 'text/*'
        assert pred( 'foo', 'text/plain', 'asdfljksadf' )
        assert pred( 'foo', 'text/html', 'asdfljksadf' )
        assert not pred( 'foo', 'image/png', 'asdfljksadf' )

class NamePredicateTests( unittest.TestCase ):

    def test_empty( self ):
        pred = NamePredicate( 'empty' )
        assert pred.getPatternStr() == 'None'
        assert not pred( 'foo', 'text/plain', 'asdfljksadf' )

    def test_simple( self ):
        pred = NamePredicate( 'onlyfoo' )
        pred.edit( 'foo' )
        assert pred.getPatternStr() == 'foo'
        assert pred( 'foo', 'text/plain', 'asdfljksadf' )
        assert not pred( 'fargo', 'text/plain', 'asdfljksadf' )
        assert not pred( 'bar', 'text/plain', 'asdfljksadf' )

    def test_pattern( self ):
        pred = NamePredicate( 'allfwords' )
        pred.edit( 'f.*' )
        assert pred.getPatternStr() == 'f.*'
        assert pred( 'foo', 'text/plain', 'asdfljksadf' )
        assert pred( 'fargo', 'text/plain', 'asdfljksadf' )
        assert not pred( 'bar', 'text/plain', 'asdfljksadf' )
        

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite( MimeTypePredicateTests ) )
    suite.addTest( unittest.makeSuite( NamePredicateTests ) )
    return suite

def run():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    run()
