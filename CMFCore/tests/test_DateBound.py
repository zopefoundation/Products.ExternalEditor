from Products.DateComparisons import DateBound
DB = DateBound.DateBound
from DateTime import DateTime
import unittest

class TestCase( unittest.TestCase ):

    def setUp( self ):
        """
        """
        self.Highball   = DB()
        self.Lowball    = DB( default_high = 0 )
        self.Sep30_2000 = DB( '2000/09/30' )
        self.Oct01_2000 = DB( '2000/10/01' )
    
    def tearDown( self ):
        """
        """
    
    def test_Comparisons( self ):
        """
        """
        assert( self.Highball == self.Highball )
        assert( self.Highball >  self.Lowball )
        assert( self.Highball >  self.Sep30_2000 )
        assert( self.Highball >  self.Oct01_2000 )

        assert( self.Lowball <  self.Highball )
        assert( self.Lowball == self.Lowball )
        assert( self.Lowball <  self.Sep30_2000 )
        assert( self.Lowball <  self.Oct01_2000 )

        assert( self.Oct01_2000 <  self.Highball )
        assert( self.Oct01_2000 >  self.Lowball )
        assert( self.Oct01_2000 >  self.Sep30_2000 )
        assert( self.Oct01_2000 == self.Oct01_2000 )

        assert( self.Sep30_2000 <  self.Highball )
        assert( self.Sep30_2000 >  self.Lowball )
        assert( self.Sep30_2000 == self.Sep30_2000 )
        assert( self.Sep30_2000 <  self.Oct01_2000 )

    def test_StringConversions( self ):
        assert( self.Sep30_2000 <  '' )
        assert( '' > self.Sep30_2000 )
        assert( self.Sep30_2000 <  '2000/10/01' )
        assert( '2000/09/01' < self.Sep30_2000 )
    
    def test_DateTimeConversions( self ):
        now         = DateTime()
        now_db      = DB( now )
        today       = now.earliestTime()
        tomorrow    = today + 1
        yesterday   = today - 1

        assert( now <  self.Highball )
        assert( now >  self.Lowball )
        assert( now_db == now )
        assert( now == now_db )
        assert( yesterday < now_db < tomorrow )
    
    def test_LowerDateBound( self ):
        """
        """
        lb = DateBound.LowerDateBound()
        assert( lb <  self.Highball )
        assert( lb == self.Lowball )
        assert( lb <  self.Sep30_2000 )
        assert( lb <  self.Oct01_2000 )
        assert( lb < '' )
    
    def test_UpperDateBound( self ):
        """
        """
        ub = DateBound.UpperDateBound()
        assert( ub == self.Highball )
        assert( ub >  self.Lowball )
        assert( ub >  self.Sep30_2000 )
        assert( ub >  self.Oct01_2000 )
        assert( ub == '' )

    def test_TimeStrings( self ):
        """
        """
        t1 = DB( '2000/09/30 12:00:00' )
        assert( t1 > self.Sep30_2000 )
        assert( t1 < self.Oct01_2000 )


def suite():
    result = unittest.TestSuite()
    for key in TestCase.__dict__.keys():
        if key[ :5 ] == 'test_':
            result.addTest( TestCase( key ) )
    
    return result

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run( suite() )

