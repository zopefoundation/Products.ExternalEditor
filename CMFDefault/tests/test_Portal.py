##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Unit / functional tests for a CMFSite.

$Id$
"""

from unittest import TestSuite, makeSuite, main
import Testing
import Zope2
Zope2.startup()

from Acquisition import aq_base

from Products.CMFCore.tests.base.testcase import SecurityRequestTest


class CMFSiteTests( SecurityRequestTest ):

    def _makeSite( self, id='testsite' ):

        from Products.CMFSetup.factory import addConfiguredSite

        addConfiguredSite(self.root, id, 'CMFDefault:default', snapshot=False)
        return getattr( self.root, id )

    def _makeContent( self, site, portal_type, id='document', **kw ):

        site.invokeFactory( type_name=portal_type, id=id )
        content = getattr( site, id )

        if getattr( aq_base( content ), 'editMetadata', None ) is not None:
            content.editMetadata( **kw )

        return content

    def test_new( self ):

        site = self._makeSite()
        self.assertEqual( len( site.portal_catalog ), 0 )

    def test_MetadataCataloguing( self ):

        site = self._makeSite()
        catalog = site.portal_catalog
        site.portal_membership.memberareaCreationFlag = 0
        uid_handler = getattr(site, 'portal_uidhandler', None)

        portal_types = [ x for x in site.portal_types.listContentTypes()
                           if x not in ( 'Discussion Item'
                                       , 'Folder'
                                       , 'Topic'
                                       ) ]

        self.assertEqual( len( catalog ), 0 )

        for portal_type in portal_types:

            doc = self._makeContent( site
                                   , portal_type=portal_type
                                   , title='Foo' )

            # in case of the CMFUid beeing installed this test
            # indexes also the site root because the 'Favorite'
            # references it by unique id
            isUidEnabledFavorite = uid_handler and portal_type == 'Favorite'
            if isUidEnabledFavorite:
                self.assertEqual( len( catalog ), 2 )
            else:
                self.assertEqual( len( catalog ), 1 )

            # find the right brain
            rid = catalog._catalog.paths.keys()[0]
            title = _getMetadata( catalog, rid )
            if isUidEnabledFavorite and title == 'Portal':
                rid = catalog._catalog.paths.keys()[1]
                title = _getMetadata( catalog, rid )
            self.assertEqual( title, 'Foo' )

            doc.editMetadata( title='Bar' )
            self.assertEqual( _getMetadata( catalog, rid ), 'Bar' )

            site._delObject( doc.getId() )
            
            if isUidEnabledFavorite:
                # unindex the site root by hand
                catalog.unindexObject(site)
                
            self.assertEqual( len( catalog ), 0 )

    def test_DocumentEditCataloguing( self ):

        site = self._makeSite()
        catalog = site.portal_catalog

        doc = self._makeContent( site
                               , portal_type='Document'
                               , title='Foo' )

        rid = catalog._catalog.paths.keys()[0]

        doc.setTitle( 'Bar' )   # doesn't reindex
        self.assertEqual( _getMetadata( catalog, rid ), 'Foo' )

        doc.edit( text_format='structured-text'
                , text='Some Text Goes Here\n\n   A paragraph\n   for you.'
                )
        self.assertEqual( _getMetadata( catalog, rid ), 'Bar' )

    def test_ImageEditCataloguing( self ):

        site = self._makeSite()
        catalog = site.portal_catalog

        doc = self._makeContent( site
                               , portal_type='Image'
                               , title='Foo' )

        rid = catalog._catalog.paths.keys()[0]

        doc.setTitle( 'Bar' )   # doesn't reindex
        self.assertEqual( _getMetadata( catalog, rid ), 'Foo' )

        doc.edit( 'GIF89a' )
        self.assertEqual( _getMetadata( catalog, rid ), 'Bar' )

    def test_FileEditCataloguing( self ):

        site = self._makeSite()
        catalog = site.portal_catalog

        doc = self._makeContent( site
                               , portal_type='File'
                               , title='Foo' )

        rid = catalog._catalog.paths.keys()[0]

        doc.setTitle( 'Bar' )   # doesn't reindex
        self.assertEqual( _getMetadata( catalog, rid ), 'Foo' )

        doc.edit( '%PDF-1.2\r' )
        self.assertEqual( _getMetadata( catalog, rid ), 'Bar' )

    def test_LinkEditCataloguing( self ):

        site = self._makeSite()
        catalog = site.portal_catalog

        doc = self._makeContent( site
                               , portal_type='Link'
                               , title='Foo' )

        rid = catalog._catalog.paths.keys()[0]

        doc.setTitle( 'Bar' )   # doesn't reindex
        self.assertEqual( _getMetadata( catalog, rid ), 'Foo' )

        doc.edit( 'http://www.example.com' )
        self.assertEqual( _getMetadata( catalog, rid ), 'Bar' )

    def test_NewsItemEditCataloguing( self ):

        site = self._makeSite()
        catalog = site.portal_catalog

        doc = self._makeContent( site
                               , portal_type='News Item'
                               , title='Foo' )

        rid = catalog._catalog.paths.keys()[0]

        doc.setTitle( 'Bar' )   # doesn't reindex
        self.assertEqual( _getMetadata( catalog, rid ), 'Foo' )

        doc.edit( '<h1>Extra!</h1>' )
        self.assertEqual( _getMetadata( catalog, rid ), 'Bar' )


def _getMetadata( catalog, rid, field='Title' ):
    md = catalog.getMetadataForRID( rid )
    return md[ field ]


def test_suite():
    return TestSuite((
        makeSuite(CMFSiteTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
