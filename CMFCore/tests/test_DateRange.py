from Products.DateComparisons import DateBound
DB = DateBound.DateBound
LB = DateBound.LowerDateBound
UB = DateBound.UpperDateBound

from Products.DateComparisons import DateRange
DR = DateRange.DateRange

import unittest

class TestCase( unittest.TestCase ):

    def setUp( self ):
        """
        """
        self.September_2000 = DR( '2000/09/01', '2000/09/30 23:59:59' )
        self.Y2K            = DR( '2000/01/01', '2000/12/31 23:59:59' )
    
    def tearDown( self ):
        """
        """
    
    def test_Intersection( self ):
        """
        """
        assert( self.September_2000.intersects( self.Y2K ) )
        assert( self.Y2K.intersects( self.September_2000 ) )
        assert( self.Y2K.intersects( DR( '1999/08/01'
                                       , '2001/07/31' ) ) )
        assert( not self.Y2K.intersects( DR( '1999/08/01'
                                           , '1999/12/31 23:59:59' ) ) )
        assert( self.Y2K.intersects( DR( '1999/08/01'
                                       , '2000/01/01' ) ) )
        assert( self.Y2K.intersects( DR( '2000/12/31 23:59:59'
                                       , '2001/02/01' ) ) )
        assert( self.Y2K.intersects( DateRange.ALWAYS ) )

    def test_Containment( self ):
        """
        """
        assert( self.Y2K.contains( self.September_2000 ) )
        assert( not self.September_2000.contains( self.Y2K ) )
        assert( self.Y2K.contains( DR( '2000/02/01', '2000/02/29' ) ) )
        assert( self.Y2K.contains( '2000/01/01' ) )
        assert( self.Y2K.contains( '2000/06/15' ) )
        assert( self.Y2K.contains( '2000/12/31 23:59:59' ) )
        assert( not self.September_2000.contains( '2000/01/01' ) )
        assert( not self.September_2000.contains( '2000/06/15' ) )
        assert( not self.September_2000.contains( '2000/12/31 23:59:59' ) )

        assert( self.Y2K.contains( DateRange.INSIDE_ANYTHING ) )

def suite():
    result = unittest.TestSuite()
    for key in TestCase.__dict__.keys():
        if key[ :5 ] == 'test_':
            result.addTest( TestCase( key ) )
    
    return result

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run( suite() )

