import unittest

from Products.PluggableAuthService.tests.conformance \
    import IAuthenticationPlugin_conformance
from Products.PluggableAuthService.tests.conformance \
    import IUserEnumerationPlugin_conformance
from Products.PluggableAuthService.tests.conformance \
    import IUserAdderPlugin_conformance

class DummyUser:

    def __init__( self, id ):
        self._id = id

    def getId( self ):
        return self._id

class ZODBUserManagerTests( unittest.TestCase
                          , IAuthenticationPlugin_conformance
                          , IUserEnumerationPlugin_conformance
                          , IUserAdderPlugin_conformance
                          ):

    def _getTargetClass( self ):

        from Products.PluggableAuthService.plugins.ZODBUserManager \
            import ZODBUserManager

        return ZODBUserManager

    def _makeOne( self, id='test', *args, **kw ):

        return self._getTargetClass()( id=id, *args, **kw )

    def test_empty( self ):

        zum = self._makeOne()

        self.assertEqual( len( zum.listUserIds() ), 0 )
        self.assertEqual( len( zum.enumerateUsers() ), 0 )
        self.assertRaises( KeyError
                         , zum.getUserIdForLogin, 'userid@example.com' )
        self.assertRaises( KeyError
                         , zum.getLoginForUserId, 'userid' )

    def test_addUser( self ):

        zum = self._makeOne()

        zum.addUser( 'userid', 'userid@example.com', 'password' )

        user_ids = zum.listUserIds()
        self.assertEqual( len( user_ids ), 1 )
        self.assertEqual( user_ids[0], 'userid' )
        self.assertEqual( zum.getUserIdForLogin( 'userid@example.com' )
                        , 'userid' )
        self.assertEqual( zum.getLoginForUserId( 'userid' )
                        , 'userid@example.com' )

        info_list = zum.enumerateUsers()
        self.assertEqual( len( info_list ), 1 )
        info = info_list[ 0 ]
        self.assertEqual( info[ 'id' ], 'userid' )
        self.assertEqual( info[ 'login' ], 'userid@example.com' )

    def test_addUser_duplicate_check( self ):

        zum = self._makeOne()

        zum.addUser( 'userid', 'userid@example.com', 'password' )

        self.assertRaises( KeyError, zum.addUser
                         , 'userid', 'luser@other.com', 'wordpass' )

        self.assertRaises( KeyError, zum.addUser
                         , 'new_user', 'userid@example.com', '3733t' )

    def test_removeUser_nonesuch( self ):

        zum = self._makeOne()

        self.assertRaises( KeyError, zum.removeUser, 'nonesuch' )

    def test_removeUser_valid_id( self ):

        zum = self._makeOne()

        zum.addUser( 'userid', 'userid@example.com', 'password' )
        zum.addUser( 'doomed', 'doomed@example.com', 'password' )

        zum.removeUser( 'doomed' )

        user_ids = zum.listUserIds()
        self.assertEqual( len( user_ids ), 1 )
        self.assertEqual( len( zum.enumerateUsers() ), 1 )
        self.assertEqual( user_ids[0], 'userid' )

        self.assertEqual( zum.getUserIdForLogin( 'userid@example.com' )
                        , 'userid' )
        self.assertEqual( zum.getLoginForUserId( 'userid' )
                        , 'userid@example.com' )

        self.assertRaises( KeyError
                         , zum.getUserIdForLogin, 'doomed@example.com' )
        self.assertRaises( KeyError
                         , zum.getLoginForUserId, 'doomed' )

    def test_authenticateCredentials_bad_creds( self ):

        zum = self._makeOne()

        zum.addUser( 'userid', 'userid@example.com', 'password' )

        self.assertEqual( zum.authenticateCredentials( {} ), None )

    def test_authenticateCredentials_valid_creds( self ):

        zum = self._makeOne()

        zum.addUser( 'userid', 'userid@example.com', 'password' )

        user_id, login = zum.authenticateCredentials(
                                { 'login' : 'userid@example.com'
                                , 'password' : 'password'
                                } )

        self.assertEqual( user_id, 'userid' )
        self.assertEqual( login, 'userid@example.com' )

    def test_enumerateUsers_no_criteria( self ):

        from Products.PluggableAuthService.tests.test_PluggableAuthService \
            import FauxRoot

        root = FauxRoot()
        zum = self._makeOne( id='no_crit' ).__of__( root )

        ID_LIST = ( 'foo', 'bar', 'baz', 'bam' )

        for id in ID_LIST:

            zum.addUser( id, '%s@example.com' % id, 'password' )

        info_list = zum.enumerateUsers()

        self.assertEqual( len( info_list ), len( ID_LIST ) )

        sorted = list( ID_LIST )
        sorted.sort()

        for i in range( len( sorted ) ):

            self.assertEqual( info_list[ i ][ 'id' ], sorted[ i ] )
            self.assertEqual( info_list[ i ][ 'login' ]
                            , '%s@example.com' % sorted[ i ] )
            self.assertEqual( info_list[ i ][ 'pluginid' ], 'no_crit' )
            self.assertEqual( info_list[ i ][ 'editurl' ]
                            , 'no_crit/manage_users?user_id=%s' % sorted[ i ])

    def test_enumerateUsers_exact( self ):

        from Products.PluggableAuthService.tests.test_PluggableAuthService \
            import FauxRoot

        root = FauxRoot()
        zum = self._makeOne( id='exact' ).__of__( root )

        ID_LIST = ( 'foo', 'bar', 'baz', 'bam' )

        for id in ID_LIST:

            zum.addUser( id, '%s@example.com' % id, 'password' )

        info_list = zum.enumerateUsers( id='bar', exact_match=True )

        self.assertEqual( len( info_list ), 1 )
        info = info_list[ 0 ]

        self.assertEqual( info[ 'id' ], 'bar' )
        self.assertEqual( info[ 'login' ], 'bar@example.com' )
        self.assertEqual( info[ 'pluginid' ], 'exact' )
        self.assertEqual( info[ 'editurl' ]
                        , 'exact/manage_users?user_id=bar' )


    def test_enumerateUsers_partial( self ):

        from Products.PluggableAuthService.tests.test_PluggableAuthService \
            import FauxRoot

        root = FauxRoot()
        zum = self._makeOne( id='partial' ).__of__( root )

        ID_LIST = ( 'foo', 'bar', 'baz', 'bam' )

        for id in ID_LIST:

            zum.addUser( id, '%s@example.com' % id, 'password' )

        info_list = zum.enumerateUsers( login='example.com', exact_match=False )

        self.assertEqual( len( info_list ), len( ID_LIST ) ) # all match

        sorted = list( ID_LIST )
        sorted.sort()

        for i in range( len( sorted ) ):

            self.assertEqual( info_list[ i ][ 'id' ], sorted[ i ] )
            self.assertEqual( info_list[ i ][ 'login' ]
                            , '%s@example.com' % sorted[ i ] )
            self.assertEqual( info_list[ i ][ 'pluginid' ], 'partial' )
            self.assertEqual( info_list[ i ][ 'editurl' ]
                            , 'partial/manage_users?user_id=%s' % sorted[ i ])

        info_list = zum.enumerateUsers( id='ba', exact_match=False )

        self.assertEqual( len( info_list ), len( ID_LIST ) - 1 ) # no 'foo'

        sorted = list( ID_LIST )
        sorted.sort()

        for i in range( len( sorted ) - 1 ):

            self.assertEqual( info_list[ i ][ 'id' ], sorted[ i ] )
            self.assertEqual( info_list[ i ][ 'login' ]
                            , '%s@example.com' % sorted[ i ] )
            self.assertEqual( info_list[ i ][ 'pluginid' ], 'partial' )
            self.assertEqual( info_list[ i ][ 'editurl' ]
                            , 'partial/manage_users?user_id=%s' % sorted[ i ])

    def test_enumerateUsers_exact_nonesuch( self ):

        from Products.PluggableAuthService.tests.test_PluggableAuthService \
            import FauxRoot

        root = FauxRoot()
        zum = self._makeOne( id='exact_nonesuch' ).__of__( root )

        ID_LIST = ( 'foo', 'bar', 'baz', 'bam' )

        for id in ID_LIST:

            zum.addUser( id, '%s@example.com' % id, 'password' )

        self.assertEquals( zum.enumerateUsers( id='qux', exact_match=True )
                         , () )

    def test_enumerateUsers_multiple_ids( self ):

        from Products.PluggableAuthService.tests.test_PluggableAuthService \
            import FauxRoot

        root = FauxRoot()
        zum = self._makeOne( id='partial' ).__of__( root )

        ID_LIST = ( 'foo', 'bar', 'baz', 'bam' )

        for id in ID_LIST:

            zum.addUser( id, '%s@example.com' % id, 'password' )

        info_list = zum.enumerateUsers( id=ID_LIST )

        self.assertEqual( len( info_list ), len( ID_LIST ) )

        for info in info_list:
            self.failUnless( info[ 'id' ] in ID_LIST )

        SUBSET = ID_LIST[:3]

        info_list = zum.enumerateUsers( id=SUBSET )

        self.assertEqual( len( info_list ), len( SUBSET ) )

        for info in info_list:
            self.failUnless( info[ 'id' ] in SUBSET )

    def test_enumerateUsers_multiple_logins( self ):

        from Products.PluggableAuthService.tests.test_PluggableAuthService \
            import FauxRoot

        root = FauxRoot()
        zum = self._makeOne( id='partial' ).__of__( root )

        ID_LIST = ( 'foo', 'bar', 'baz', 'bam' )
        LOGIN_LIST = [ '%s@example.com' % x for x in ID_LIST ]

        for i in range( len( ID_LIST ) ):

            zum.addUser( ID_LIST[i], LOGIN_LIST[i], 'password' )

        info_list = zum.enumerateUsers( login=LOGIN_LIST )

        self.assertEqual( len( info_list ), len( LOGIN_LIST ) )

        for info in info_list:
            self.failUnless( info[ 'id' ] in ID_LIST )
            self.failUnless( info[ 'login' ] in LOGIN_LIST )

        SUBSET_LOGINS = LOGIN_LIST[:3]
        SUBSET_IDS = ID_LIST[:3]

        info_list = zum.enumerateUsers( login=SUBSET_LOGINS )

        self.assertEqual( len( info_list ), len( SUBSET_LOGINS ) )

        for info in info_list:
            self.failUnless( info[ 'id' ] in SUBSET_IDS )
            self.failUnless( info[ 'login' ] in SUBSET_LOGINS )

if __name__ == "__main__":
    unittest.main()
