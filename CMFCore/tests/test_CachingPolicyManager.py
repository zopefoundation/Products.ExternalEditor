import Zope
from App.Common import rfc1123_date
import unittest

from DateTime.DateTime import DateTime

ACCLARK = DateTime( '2001/01/01' )

class DummyContent:

    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, modified ):
        self.modified = modified 

    def Type( self ):
        return 'Dummy'

    def modified( self ):
        return self.modified 


class CachingPolicyTests( unittest.TestCase ):

    def setUp(self):
        self._epoch = DateTime( '1970/01/01' )

    def _makePolicy( self, policy_id, **kw ):

        from Products.CMFCore.CachingPolicyManager import CachingPolicy
        return CachingPolicy( policy_id, **kw )

    def _makeContext( self, **kw ):

        from Products.CMFCore.CachingPolicyManager import createCPContext
        from Products.CMFCore.CachingPolicyManager import createCPContext
        return createCPContext( DummyContent(self._epoch)
                              , 'foo_view', kw, self._epoch )
        
    def test_interface( self ):
        from Products.CMFCore.interfaces.CachingPolicyManager \
            import CachingPolicyManager as ICachingPolicyManager
        from Products.CMFCore.CachingPolicyManager import CachingPolicyManager
        from Interface import verify_class_implementation

        verify_class_implementation( ICachingPolicyManager
                                   , CachingPolicyManager )

    def test_empty( self ):

        policy = self._makePolicy( 'empty' )
        context = self._makeContext()
        headers = policy.getHeaders( context )

        self.assertEqual( len( headers ), 1 )
        self.assertEqual( headers[0][0], 'Last-modified' )
        self.assertEqual( headers[0][1]
                        , rfc1123_date(self._epoch.timeTime()) )

    def test_noPassPredicate( self ):

        policy = self._makePolicy( 'noPassPredicate', predicate='nothing' )
        context = self._makeContext()
        headers = policy.getHeaders( context )

        self.assertEqual( len( headers ), 0 )

    def test_typePredicate( self ):

        policy = self._makePolicy( 'typePredicate'
                           , predicate='python:content.Type() == "Dummy"' )
        context = self._makeContext()
        headers = policy.getHeaders( context )

        self.assertEqual( len( headers ), 1 )
        self.assertEqual( headers[0][0] , 'Last-modified' )
        self.assertEqual( headers[0][1] , rfc1123_date(self._epoch.timeTime()) )

    def test_typePredicateMiss( self ):

        policy = self._makePolicy( 'typePredicate'
                        , predicate='python:content.Type() == "Foolish"' )
        context = self._makeContext()
        headers = policy.getHeaders( context )

        self.assertEqual( len( headers ), 0 )

    def test_viewPredicate( self ):

        policy = self._makePolicy( 'viewPredicate'
                                 , predicate='python:view == "foo_view"' )
        context = self._makeContext()
        headers = policy.getHeaders( context )

        self.assertEqual( len( headers ), 1 )
        self.assertEqual( headers[0][0], 'Last-modified' )
        self.assertEqual( headers[0][1]
                        , rfc1123_date(self._epoch.timeTime()) )

    def test_viewPredicateMiss( self ):

        policy = self._makePolicy( 'viewPredicateMiss'
                           , predicate='python:view == "bar_view"' )
        context = self._makeContext()
        headers = policy.getHeaders( context )

        self.assertEqual( len( headers ), 0 )

    def test_kwPredicate( self ):

        policy = self._makePolicy( 'kwPredicate'
                                 , predicate='python:"foo" in keywords.keys()' )
        context = self._makeContext( foo=1 )
        headers = policy.getHeaders( context )

        self.assertEqual( len( headers ), 1 )
        self.assertEqual( headers[0][0], 'Last-modified' )
        self.assertEqual( headers[0][1]
                        , rfc1123_date(self._epoch.timeTime()) )

    def test_kwPredicateMiss( self ):

        policy = self._makePolicy( 'kwPredicateMiss'
                                 , predicate='python:"foo" in keywords.keys()' )
        context = self._makeContext( bar=1 )
        headers = policy.getHeaders( context )

        self.assertEqual( len( headers ), 0 )

        context = self._makeContext()
        headers = policy.getHeaders( context )

        self.assertEqual( len( headers ), 0 )
        
    def test_mtimeFunc( self ):

        policy = self._makePolicy( 'mtimeFunc'
                                 , mtime_func='string:2001/01/01' )
        context = self._makeContext()
        headers = policy.getHeaders( context )

        self.assertEqual( len( headers ), 1 )
        self.assertEqual( headers[0][0], 'Last-modified' )
        self.assertEqual( headers[0][1]
                        , rfc1123_date(ACCLARK.timeTime()) )
        
    def test_mtimeFuncNone( self ):

        policy = self._makePolicy( 'mtimeFuncNone'
                                 , mtime_func='nothing' )
        context = self._makeContext()
        headers = policy.getHeaders( context )

        self.assertEqual( len( headers ), 0 )
        
    def test_maxAge( self ):

        policy = self._makePolicy( 'aged', max_age_secs=86400 )
        context = self._makeContext()
        headers = policy.getHeaders( context )

        self.assertEqual( len( headers ), 3 )
        self.assertEqual( headers[0][0].lower() , 'last-modified' )
        self.assertEqual( headers[0][1]
                        , rfc1123_date(self._epoch.timeTime()) )
        self.assertEqual( headers[1][0].lower() , 'expires' )
        self.assertEqual( headers[1][1]
                        , rfc1123_date((self._epoch+1).timeTime()) )
        self.assertEqual( headers[2][0].lower() , 'cache-control' )
        self.assertEqual( headers[2][1] , 'max-age=86400' )
        
    def test_noCache( self ):

        policy = self._makePolicy( 'noCache', no_cache=1 )
        context = self._makeContext()
        headers = policy.getHeaders( context )

        self.assertEqual( len( headers ), 2 )
        self.assertEqual( headers[0][0].lower() , 'last-modified' )
        self.assertEqual( headers[0][1]
                        , rfc1123_date(self._epoch.timeTime()) )
        self.assertEqual( headers[1][0].lower() , 'cache-control' )
        self.assertEqual( headers[1][1] , 'no-cache' )
        
    def test_noStore( self ):

        policy = self._makePolicy( 'noStore', no_store=1 )
        context = self._makeContext()
        headers = policy.getHeaders( context )

        self.assertEqual( len( headers ), 2 )
        self.assertEqual( headers[0][0].lower() , 'last-modified' )
        self.assertEqual( headers[0][1]
                        , rfc1123_date(self._epoch.timeTime()) )
        self.assertEqual( headers[1][0].lower() , 'cache-control' )
        self.assertEqual( headers[1][1] , 'no-store' )
        
    def test_mustRevalidate( self ):

        policy = self._makePolicy( 'mustRevalidate', must_revalidate=1 )
        context = self._makeContext()
        headers = policy.getHeaders( context )

        self.assertEqual( len( headers ), 2 )
        self.assertEqual( headers[0][0].lower() , 'last-modified' )
        self.assertEqual( headers[0][1]
                        , rfc1123_date(self._epoch.timeTime()) )
        self.assertEqual( headers[1][0].lower() , 'cache-control' )
        self.assertEqual( headers[1][1] , 'must-revalidate' )
        
    def test_combined( self ):

        policy = self._makePolicy( 'noStore', no_cache=1, no_store=1 )
        context = self._makeContext()
        headers = policy.getHeaders( context )

        self.assertEqual( len( headers ), 2 )
        self.assertEqual( headers[0][0].lower() , 'last-modified' )
        self.assertEqual( headers[0][1]
                        , rfc1123_date(self._epoch.timeTime()) )
        self.assertEqual( headers[1][0].lower() , 'cache-control' )
        self.assertEqual( headers[1][1] , 'no-cache, no-store' )


class CachingPolicyManagerTests( unittest.TestCase ):

    def setUp(self):

        self._epoch = DateTime()

    def _makeOne( self ):
        from Products.CMFCore.CachingPolicyManager import CachingPolicyManager
        return CachingPolicyManager()

    def assertEqualDelta( self, lhs, rhs, delta ):
        self.failUnless( abs( lhs - rhs ) <= delta )

    def test_interface( self ):
        from Products.CMFCore.CachingPolicyManager import CachingPolicyManager
        from Products.CMFCore.interfaces.CachingPolicyManager \
                import CachingPolicyManager as ICachingPolicyManager

        from Interface import verify_class_implementation

        verify_class_implementation( ICachingPolicyManager
                                   , CachingPolicyManager )

    def test_empty( self ):

        mgr = self._makeOne()

        self.assertEqual( len( mgr.listPolicies() ), 0 )
        headers = mgr.getHTTPCachingHeaders( content=DummyContent(self._epoch)
                                           , view_method='foo_view'
                                           , keywords={}
                                           )
        self.assertEqual( len( headers ), 0 )

        self.assertRaises( KeyError, mgr._updatePolicy
                         , 'xyzzy', None, None, None, None, None, None )
        self.assertRaises( KeyError, mgr._removePolicy, 'xyzzy' )
        self.assertRaises( KeyError, mgr._reorderPolicy, 'xyzzy', -1 )
    
    def test_addPolicy( self ):

        mgr = self._makeOne()
        mgr._addPolicy( 'first', 'python:1', None, 0, 0, 0, 0 )
        headers = mgr.getHTTPCachingHeaders( content=DummyContent(self._epoch)
                                           , view_method='foo_view'
                                           , keywords={}
                                           )
        self.assertEqual( len( headers ), 3 )
        self.assertEqual( headers[0][0].lower() , 'last-modified' )
        self.assertEqual( headers[0][1]
                        , rfc1123_date(self._epoch.timeTime()) )
        self.assertEqual( headers[1][0].lower() , 'expires' )
        self.assertEqual( headers[1][1]
                        , rfc1123_date(self._epoch.timeTime()) )
        self.assertEqual( headers[2][0].lower() , 'cache-control' )
        self.assertEqual( headers[2][1], 'max-age=0' )

    def test_reorder( self ):

        mgr = self._makeOne()

        policy_ids = ( 'foo', 'bar', 'baz', 'qux' )

        for policy_id in policy_ids:
            mgr._addPolicy( policy_id
                          , 'python:"%s" in keywords.keys()' % policy_id
                          , None, 0, 0, 0, 0 )

        ids = tuple( map( lambda x: x[0], mgr.listPolicies() ) )
        self.assertEqual( ids, policy_ids )

        mgr._reorderPolicy( 'bar', 3 )

        ids = tuple( map( lambda x: x[0], mgr.listPolicies() ) )
        self.assertEqual( ids, ( 'foo', 'baz', 'qux', 'bar' ) )

    def _makeOneWithPolicies( self ):

        mgr = self._makeOne()

        policy_tuples = ( ( 'foo', None  )
                        , ( 'bar', 0     )
                        , ( 'baz', 3600  )
                        , ( 'qux', 86400 )
                        )

        for policy_id, max_age_secs in policy_tuples:
            mgr._addPolicy( policy_id
                          , 'python:"%s" in keywords.keys()' % policy_id
                          , None, max_age_secs, 0, 0, 0 )

        return mgr

    def test_lookupNoMatch( self ):

        mgr = self._makeOneWithPolicies()
        headers = mgr.getHTTPCachingHeaders( content=DummyContent(self._epoch)
                                           , view_method='foo_view'
                                           , keywords={}
                                           )
        self.assertEqual( len( headers ), 0 )

    def test_lookupMatchFoo( self ):

        mgr = self._makeOneWithPolicies()
        headers = mgr.getHTTPCachingHeaders( content=DummyContent(self._epoch)
                                           , view_method='foo_view'
                                           , keywords={ 'foo' : 1 }
                                           )
        self.assertEqual( len( headers ), 1 )
        self.assertEqual( headers[0][0].lower(), 'last-modified' )
        self.assertEqual( headers[0][1]
                        , rfc1123_date(self._epoch.timeTime()) )


    def test_lookupMatchBar( self ):

        mgr = self._makeOneWithPolicies()
        headers = mgr.getHTTPCachingHeaders( content=DummyContent(self._epoch)
                                           , view_method='foo_view'
                                           , keywords={ 'bar' : 1 }
                                           )
        self.assertEqual( len( headers ), 3 )
        self.assertEqual( headers[0][0].lower() , 'last-modified' )
        self.assertEqual( headers[0][1]
                        , rfc1123_date(self._epoch.timeTime()) )
        self.assertEqual( headers[1][0].lower() , 'expires' )
        self.assertEqual( headers[1][1]
                        , rfc1123_date(self._epoch.timeTime()) )
        self.assertEqual( headers[2][0].lower() , 'cache-control' )
        self.assertEqual( headers[2][1], 'max-age=0' )


    def test_lookupMatchBaz( self ):

        mgr = self._makeOneWithPolicies()
        headers = mgr.getHTTPCachingHeaders( content=DummyContent(self._epoch)
                                           , view_method='foo_view'
                                           , keywords={ 'baz' : 1 }
                                           )
        self.assertEqual( len( headers ), 3 )
        self.assertEqual( headers[0][0].lower() , 'last-modified' )
        self.assertEqual( headers[0][1]
                        , rfc1123_date(self._epoch.timeTime()) )
        self.assertEqual( headers[1][0].lower() , 'expires' )

        exp_time = DateTime( headers[1][1] )
        target = self._epoch + ( 1.0 / 24.0 )
        self.assertEqualDelta( exp_time, target, 0.01 )

        self.assertEqual( headers[2][0].lower() , 'cache-control' )
        self.assertEqual( headers[2][1] , 'max-age=3600' )


    def test_lookupMatchQux( self ):

        mgr = self._makeOneWithPolicies()
        headers = mgr.getHTTPCachingHeaders( content=DummyContent(self._epoch)
                                           , view_method='foo_view'
                                           , keywords={ 'qux' : 1 }
                                           )
        self.assertEqual( len( headers ), 3 )
        self.assertEqual( headers[0][0].lower() , 'last-modified' )
        self.assertEqual( headers[0][1]
                        , rfc1123_date(self._epoch.timeTime()) )
        self.assertEqual( headers[1][0].lower() , 'expires' )

        exp_time = DateTime( headers[1][1] )
        target = self._epoch + 1.0
        self.assertEqualDelta( exp_time, target, 0.01 )

        self.assertEqual( headers[2][0].lower() , 'cache-control' )
        self.assertEqual( headers[2][1] , 'max-age=86400' )

def test_suite():
    return unittest.TestSuite((
                                unittest.makeSuite( CachingPolicyTests ),
                                unittest.makeSuite( CachingPolicyManagerTests ),
                             ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
