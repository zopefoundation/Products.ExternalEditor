##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################
"""
    Unit tests for Favorites.

$Id$
"""
__version__ = "$Revision$"[11:-2]


import unittest
import Acquisition
from Acquisition import aq_inner, aq_parent

class DummyURLTool( Acquisition.Implicit ):

    root = 'DummyTool'

    def __call__( self ):
        return self.root

    getPortalPath = __call__

    def getPortalObject( self ):
        return aq_parent( aq_inner( self ) )

    def getIcon( self, relative=0 ):
        return 'Tool: %s' % relative

class DummySite( Acquisition.Implicit ):

    def __init__( self, **kw ):
        self.__dict__.update( kw )

    def restrictedTraverse( self, path ):
        return path and getattr( self, path ) or self

    def getIcon( self, relative=0 ):
        return 'Site: %s' % relative

class FavoriteTests( unittest.TestCase ):

    def setUp( self ):

        self.tool = DummyURLTool()
        self.site = DummySite( portal_url=self.tool )

    def _makeOne( self, *args, **kw ):

        from Products.CMFDefault.Favorite import Favorite

        f = apply( Favorite, args, kw )
        return f.__of__( self.site )

    def test_Empty( self ):

        f = self._makeOne( 'foo' )

        self.assertEqual( f.getId(), 'foo' )
        self.assertEqual( f.Title(), '' )
        self.assertEqual( f.Description(), '' )
        self.assertEqual( f.getRemoteUrl(), self.tool.root )
        self.assertEqual( f.getObject(), self.site )
        self.assertEqual( f.getIcon(), self.site.getIcon() )
        self.assertEqual( f.getIcon(1), self.site.getIcon(1) )

    def test_CtorArgs( self ):

        self.assertEqual( self._makeOne( 'foo'
                                       , title='Title'
                                       ).Title(), 'Title' )

        self.assertEqual( self._makeOne( 'bar'
                                       , description='Description'
                                       ).Description(), 'Description' )

        baz = self._makeOne( 'baz', remote_url='portal_url' )
        self.assertEqual( baz.getObject(), self.tool )
        self.assertEqual( baz.getRemoteUrl()
                        , '%s/portal_url' % self.tool.root )
        self.assertEqual( baz.getIcon(), self.tool.getIcon() )

    def test_edit( self ):

        f = self._makeOne( 'foo' )
        f.edit( 'portal_url' )
        self.assertEqual( f.getObject(), self.tool )
        self.assertEqual( f.getRemoteUrl()
                        , '%s/portal_url' % self.tool.root )
        self.assertEqual( f.getIcon(), self.tool.getIcon() )


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite( FavoriteTests ) )
    return suite

def run():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    run()

