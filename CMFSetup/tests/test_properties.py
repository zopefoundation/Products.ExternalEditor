##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Site properties export / import unit tests.

$Id$
"""

import unittest
import Testing
import Zope
Zope.startup()

from OFS.Folder import Folder

from common import BaseRegistryTests
from common import DummyExportContext
from common import DummyImportContext


_EMPTY_EXPORT = """\
<?xml version="1.0"?>
<site>
</site>
"""

_NORMAL_EXPORT = """\
<?xml version="1.0"?>
<site>
  <property name="foo" type="string">Foo</property>
  <property name="bar" type="tokens">
   <element value="Bar"/></property>
</site>
"""


class DummySite(Folder):

    _properties = ()


class _SitePropertiesSetup(BaseRegistryTests):

    def _initSite(self, foo=2, bar=2):

        self.root.site = DummySite()
        site = self.root.site

        if foo > 0:
            site._setProperty('foo', '', 'string')
        if foo > 1:
            site._updateProperty('foo', 'Foo')

        if bar > 0:
            site._setProperty( 'bar', (), 'tokens' )
        if bar > 1:
            site._updateProperty( 'bar', ('Bar',) )

        return site


class SitePropertiesConfiguratorTests(_SitePropertiesSetup):

    def _getTargetClass(self):

        from Products.CMFSetup.properties import SitePropertiesConfigurator
        return SitePropertiesConfigurator

    def test_listSiteInfos_normal(self):

        site = self._initSite()

        EXPECTED = [ { 'id': 'foo',
                       'value': 'Foo',
                       'elements': (),
                       'type': 'string',
                       'select_variable': None },
                     { 'id': 'bar',
                       'value': '',
                       'elements': ('Bar',),
                       'type': 'tokens',
                       'select_variable': None } ]

        configurator = self._makeOne(site)

        site_info = configurator.listSiteInfos()
        self.assertEqual( len(site_info), len(EXPECTED) )

        for found, expected in zip(site_info, EXPECTED):
            self.assertEqual(found, expected)

    def test_generateXML_empty(self):

        site = self._initSite(0, 0)
        configurator = self._makeOne(site).__of__(site)

        self._compareDOM(configurator.generateXML(), _EMPTY_EXPORT)

    def test_generateXML_normal(self):

        site = self._initSite()
        configurator = self._makeOne(site).__of__(site)

        self._compareDOM( configurator.generateXML(), _NORMAL_EXPORT )

    def test_parseXML_empty(self):

        site = self._initSite(0, 0)
        configurator = self._makeOne(site)
        site_info = configurator.parseXML(_EMPTY_EXPORT)

        self.assertEqual( len( site_info['properties'] ), 0 )

    def test_parseXML_normal(self):

        site = self._initSite()
        configurator = self._makeOne(site)
        site_info = configurator.parseXML(_NORMAL_EXPORT)

        self.assertEqual( len( site_info['properties'] ), 2 )

        info = site_info['properties'][0]
        self.assertEqual( info['id'], 'foo' )
        self.assertEqual( info['value'], 'Foo' )
        self.assertEqual( len( info['elements'] ), 0 )

        info = site_info['properties'][1]
        self.assertEqual( info['id'], 'bar' )
        self.assertEqual( info['value'], '' )
        self.assertEqual( len( info['elements'] ), 1 )
        self.assertEqual( info['elements'][0], 'Bar' )


class Test_exportSiteProperties(_SitePropertiesSetup):

    def test_empty(self):

        site = self._initSite(0, 0)
        context = DummyExportContext(site)

        from Products.CMFSetup.properties import exportSiteProperties
        exportSiteProperties(context)

        self.assertEqual( len(context._wrote), 1 )
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'properties.xml')
        self._compareDOM(text, _EMPTY_EXPORT)
        self.assertEqual(content_type, 'text/xml')

    def test_normal(self):

        site = self._initSite()
        context = DummyExportContext( site )

        from Products.CMFSetup.properties import exportSiteProperties
        exportSiteProperties(context)

        self.assertEqual( len(context._wrote), 1 )
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'properties.xml')
        self._compareDOM(text, _NORMAL_EXPORT)
        self.assertEqual(content_type, 'text/xml')


class Test_importSiteProperties(_SitePropertiesSetup):

    def test_empty_default_purge(self):

        site = self._initSite()

        self.assertEqual( len( site.propertyIds() ), 2 )
        self.failUnless( 'foo' in site.propertyIds() )
        self.assertEqual( site.getProperty('foo'), 'Foo' )
        self.failUnless( 'bar' in site.propertyIds() )
        self.assertEqual( site.getProperty('bar'), ('Bar',) )

        context = DummyImportContext(site)
        context._files['properties.xml'] = _EMPTY_EXPORT

        from Products.CMFSetup.properties import importSiteProperties
        importSiteProperties(context)

        self.assertEqual( len( site.propertyIds() ), 0 )

    def test_empty_explicit_purge(self):

        site = self._initSite()

        self.assertEqual( len( site.propertyIds() ), 2 )
        self.failUnless( 'foo' in site.propertyIds() )
        self.assertEqual( site.getProperty('foo'), 'Foo' )
        self.failUnless( 'bar' in site.propertyIds() )
        self.assertEqual( site.getProperty('bar'), ('Bar',) )

        context = DummyImportContext(site, True)
        context._files['properties.xml'] = _EMPTY_EXPORT

        from Products.CMFSetup.properties import importSiteProperties
        importSiteProperties(context)

        self.assertEqual( len( site.propertyIds() ), 0 )

    def test_empty_skip_purge(self):

        site = self._initSite()

        self.assertEqual( len( site.propertyIds() ), 2 )
        self.failUnless( 'foo' in site.propertyIds() )
        self.assertEqual( site.getProperty('foo'), 'Foo' )
        self.failUnless( 'bar' in site.propertyIds() )
        self.assertEqual( site.getProperty('bar'), ('Bar',) )

        context = DummyImportContext(site, False)
        context._files['properties.xml'] = _EMPTY_EXPORT

        from Products.CMFSetup.properties import importSiteProperties
        importSiteProperties(context)

        self.assertEqual( len( site.propertyIds() ), 2 )
        self.failUnless( 'foo' in site.propertyIds() )
        self.assertEqual( site.getProperty('foo'), 'Foo' )
        self.failUnless( 'bar' in site.propertyIds() )
        self.assertEqual( site.getProperty('bar'), ('Bar',) )

    def test_normal(self):

        site = self._initSite(0,0)

        self.assertEqual( len( site.propertyIds() ), 0 )

        context = DummyImportContext(site)
        context._files['properties.xml'] = _NORMAL_EXPORT

        from Products.CMFSetup.properties import importSiteProperties
        importSiteProperties(context)

        self.assertEqual( len( site.propertyIds() ), 2 )
        self.failUnless( 'foo' in site.propertyIds() )
        self.assertEqual( site.getProperty('foo'), 'Foo' )
        self.failUnless( 'bar' in site.propertyIds() )
        self.assertEqual( site.getProperty('bar'), ('Bar',) )

    def test_normal_encode_as_ascii(self):

        site = self._initSite(0,0)

        self.assertEqual( len( site.propertyIds() ), 0 )

        context = DummyImportContext(site, encoding='ascii')
        context._files['properties.xml'] = _NORMAL_EXPORT

        from Products.CMFSetup.properties import importSiteProperties
        importSiteProperties(context)

        self.assertEqual( len( site.propertyIds() ), 2 )
        self.failUnless( 'foo' in site.propertyIds() )
        self.assertEqual( site.getProperty('foo'), 'Foo' )
        self.failUnless( 'bar' in site.propertyIds() )
        self.assertEqual( site.getProperty('bar'), ('Bar',) )


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(SitePropertiesConfiguratorTests),
        unittest.makeSuite(Test_exportSiteProperties),
        unittest.makeSuite(Test_importSiteProperties),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
