import unittest

class DummyRecord:

    def __init__( self, key, value ):
        self.key = key
        self.value = value

class CollectorSubsetTests( unittest.TestCase ):

    def _makeOne( self, id='subset', *args, **kw ):

        from Products.CMFCollector.CollectorSubset import CollectorSubset
        return CollectorSubset( id=id, *args, **kw )

    def test_listParameterTypes( self ):

        subset = self._makeOne()

        parm_types = subset.listParameterTypes()

        self.failUnless( 'review_state' in parm_types )
        self.failUnless( 'submitter_id' in parm_types )
        self.failUnless( 'supporters:list' in parm_types )

        self.failUnless( 'topics:list' in parm_types )
        self.failUnless( 'classifications:list' in parm_types )
        self.failUnless( 'importances:list' in parm_types )

    def test_empty( self ):

        subset = self._makeOne()

        self.assertEqual( len( subset.listParameters() ), 0 )
        self.assertEqual( subset._buildQueryString(), '' )

        self.assertEqual( subset.getParameterValue( 'review_state' ), '' )
        self.assertEqual( subset.getParameterValue( 'submitter_id' ), '' )
        self.assertEqual( subset.getParameterValue( 'supporters:list' ), '' )
        self.assertEqual( subset.getParameterValue( 'topics:list' ), '' )
        self.assertEqual( subset.getParameterValue( 'classifications:list' )
                        , '' )
        self.assertEqual( subset.getParameterValue( 'importances:list' ), '' )

    def test_getParameterValue_badParm( self ):

        subset = self._makeOne()
        self.assertRaises( ValueError, subset.getParameterValue, 'importaince' )

    def test_setParameter_badParm( self ):

        subset = self._makeOne()

        self.assertRaises( ValueError, subset.setParameter
                         , 'wonders_about', 'fred' )

    def test_setParameter_oneParm( self ):

        subset = self._makeOne()

        subset.setParameter( 'supporters:list', 'fred' )

        self.assertEqual( len( subset.listParameters() ), 1 )
        self.assertEqual( subset._buildQueryString(), 'supporters%3Alist=fred' )

        self.assertEqual( subset.getParameterValue( 'review_state' ), '' )
        self.assertEqual( subset.getParameterValue( 'submitter_id' ), '' )
        self.assertEqual( subset.getParameterValue( 'supporters:list' )
                                                  , 'fred' )
        self.assertEqual( subset.getParameterValue( 'topics:list' ), '' )
        self.assertEqual( subset.getParameterValue( 'classifications:list' )
                        , '' )
        self.assertEqual( subset.getParameterValue( 'importances:list' ), '' )

    def test_clearParameters( self ):

        subset = self._makeOne()

        subset.setParameter( 'supporters:list', 'fred' )
        subset.clearParameters()

        self.assertEqual( len( subset.listParameters() ), 0 )
        self.assertEqual( subset._buildQueryString(), '' )

        parm_types = subset.listParameterTypes()

        self.failUnless( 'review_state' in parm_types )
        self.failUnless( 'submitter_id' in parm_types )
        self.failUnless( 'supporters:list' in parm_types )

        self.failUnless( 'topics:list' in parm_types )
        self.failUnless( 'classifications:list' in parm_types )
        self.failUnless( 'importances:list' in parm_types )

        self.assertEqual( subset.getParameterValue( 'review_state' ), '' )
        self.assertEqual( subset.getParameterValue( 'submitter_id' ), '' )
        self.assertEqual( subset.getParameterValue( 'supporters:list' ), '' )
        self.assertEqual( subset.getParameterValue( 'topics:list' ), '' )
        self.assertEqual( subset.getParameterValue( 'classifications:list' )
                        , '' )
        self.assertEqual( subset.getParameterValue( 'importances:list' ), '' )

    def test_setParameters_twoParms( self ):

        subset = self._makeOne()

        subset.setParameter( 'supporters:list', 'fred' )
        subset.setParameter( 'topics:list', 'bug' )

        self.assertEqual( len( subset.listParameters() ), 2 )
        qs = subset._buildQueryString()
        terms = qs.split( '&' )
        terms.sort()
        self.assertEqual( terms[0], 'supporters%3Alist=fred' )
        self.assertEqual( terms[1], 'topics%3Alist=bug' )

        self.assertEqual( subset.getParameterValue( 'review_state' ), '' )
        self.assertEqual( subset.getParameterValue( 'submitter_id' ), '' )
        self.assertEqual( subset.getParameterValue( 'supporters:list' )
                                                  , 'fred' )
        self.assertEqual( subset.getParameterValue( 'topics:list' ), 'bug' )
        self.assertEqual( subset.getParameterValue( 'classifications:list' )
                        , '' )
        self.assertEqual( subset.getParameterValue( 'importances:list' ), '' )

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite( CollectorSubsetTests ) )
    return suite

if __name__ == '__main__':
    unittest.main( defaultTest='test_suite' )

