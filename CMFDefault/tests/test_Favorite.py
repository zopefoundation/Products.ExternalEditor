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
""" Unit tests for Favorites.

$Id$
"""

from unittest import TestCase, TestSuite, makeSuite, main

import Testing
import Zope
try:
    Zope.startup()
except AttributeError:
    # for Zope versions before 2.6.1
    pass

from Products.CMFCore.tests.base.dummy import DummyObject as DummySite
from Products.CMFCore.tests.base.dummy import DummyTool as DummyURLTool
from Products.CMFDefault.Favorite import Favorite


class FavoriteTests( TestCase ):

    def setUp( self ):
        self.tool = DummyURLTool()
        self.site = DummySite( portal_url=self.tool )

    def _makeOne(self, *args, **kw):
        f = Favorite(*args, **kw)
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

    def test_editEmpty( self ):

        f = self._makeOne( 'gnnn' )
        f.edit( '' )
        self.assertEqual( f.getObject(), self.site )
        self.assertEqual( f.getRemoteUrl(), self.tool.root )
        self.assertEqual( f.getIcon(), self.site.getIcon() )


def test_suite():
    return TestSuite((
        makeSuite( FavoriteTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
