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
""" CMFSetup.utils unit tests

$Id$
"""

import unittest
import Testing
import Zope2
Zope2.startup()

from DateTime.DateTime import DateTime
from OFS.Folder import Folder

from common import BaseRegistryTests


_NORMAL_PROPERTY_NODES = """\
  <property name="foo_boolean" type="boolean">True</property>
  <property name="foo_date" type="date">2000/01/01</property>
  <property name="foo_float" type="float">1.1</property>
  <property name="foo_int" type="int">1</property>
  <property name="foo_lines" type="lines">
   <element value="Foo"/>
   <element value="Lines"/></property>
  <property name="foo_long" type="long">1</property>
  <property name="foo_string" type="string">Foo String</property>
  <property name="foo_text" type="text">Foo
Text</property>
  <property name="foo_tokens" type="tokens">
   <element value="Foo"/>
   <element value="Tokens"/></property>
  <property name="foo_selection" type="selection"
            select_variable="foobarbaz">Foo</property>
  <property name="foo_mselection" type="multiple selection"
            select_variable="foobarbaz">
   <element value="Foo"/>
   <element value="Baz"/></property>
"""

_FIXED_PROPERTY_NODES = """\
  <property name="foo_boolean">True</property>
  <property name="foo_date">2000/01/01</property>
  <property name="foo_float">1.1</property>
  <property name="foo_int">1</property>
  <property name="foo_lines">
   <element value="Foo"/>
   <element value="Lines"/></property>
  <property name="foo_long">1</property>
  <property name="foo_string">Foo String</property>
  <property name="foo_text">Foo
Text</property>
  <property name="foo_tokens">
   <element value="Foo"/>
   <element value="Tokens"/></property>
  <property name="foo_selection" type="selection"
            select_variable="foobarbaz">Foo</property>
  <property name="foo_mselection">
   <element value="Foo"/>
   <element value="Baz"/></property>
"""

_NORMAL_PROPERTY_INFO = ( { 'id': 'foo_boolean',
                            'value': True,
                            'elements': (),
                            'type': 'boolean',
                            'select_variable': None },
                          { 'id': 'foo_date',
                            'value': DateTime('2000/01/01'),
                            'elements': (),
                            'type': 'date',
                            'select_variable': None },
                          { 'id': 'foo_float',
                            'value': 1.1,
                            'elements': (),
                            'type': 'float',
                            'select_variable': None },
                          { 'id': 'foo_int',
                            'value': 1,
                            'elements': (),
                            'type': 'int',
                            'select_variable': None },
                          { 'id': 'foo_lines',
                            'value': '',
                            'elements': ('Foo', 'Lines'),
                            'type': 'lines',
                            'select_variable': None },
                          { 'id': 'foo_long',
                            'value': 1,
                            'elements': (),
                            'type': 'long',
                            'select_variable': None },
                          { 'id': 'foo_string',
                            'value': 'Foo String',
                            'elements': (),
                            'type': 'string',
                            'select_variable': None },
                          { 'id': 'foo_text',
                            'value': 'Foo\nText',
                            'elements': (),
                            'type': 'text',
                            'select_variable': None },
                          { 'id': 'foo_tokens',
                            'value': '',
                            'elements': ('Foo', 'Tokens'),
                            'type': 'tokens',
                            'select_variable': None },
                          { 'id': 'foo_selection',
                            'value': 'Foo',
                            'elements': (),
                            'type': 'selection',
                            'select_variable': 'foobarbaz' },
                          { 'id': 'foo_mselection',
                            'value': '',
                            'elements': ('Foo', 'Baz'),
                            'type': 'multiple selection',
                            'select_variable': 'foobarbaz' } )

_NORMAL_PROPERTY_EXPORT = """\
<?xml version="1.0"?>
<dummy>
%s
</dummy>
""" % _NORMAL_PROPERTY_NODES

_FIXED_PROPERTY_EXPORT = """\
<?xml version="1.0"?>
<dummy>
%s
</dummy>
""" % _FIXED_PROPERTY_NODES

_NORMAL_OBJECT_EXPORT = """\
<?xml version="1.0"?>
<dummy>
 <object meta_type="Dummy Type" name="dummy">
%s
 </object>
</dummy>
""" % _NORMAL_PROPERTY_NODES

_SPECIAL_IMPORT = """\
<?xml version="1.0"?>
<dummy>
 <!-- ignore comment, allow empty description -->
 <description></description>
</dummy>
"""

def _testFunc( *args, **kw ):

    """ This is a test.

    This is only a test.
    """

_TEST_FUNC_NAME = 'Products.CMFSetup.tests.test_utils._testFunc'

class Whatever:
    pass

_WHATEVER_NAME = 'Products.CMFSetup.tests.test_utils.Whatever'

whatever_inst = Whatever()
whatever_inst.__name__ = 'whatever_inst'

_WHATEVER_INST_NAME = 'Products.CMFSetup.tests.test_utils.whatever_inst'

class UtilsTests( unittest.TestCase ):

    def test__getDottedName_simple( self ):

        from Products.CMFSetup.utils import _getDottedName

        self.assertEqual( _getDottedName( _testFunc ), _TEST_FUNC_NAME )

    def test__getDottedName_string( self ):

        from Products.CMFSetup.utils import _getDottedName

        self.assertEqual( _getDottedName( _TEST_FUNC_NAME ), _TEST_FUNC_NAME )

    def test__getDottedName_unicode( self ):

        from Products.CMFSetup.utils import _getDottedName

        dotted = u'%s' % _TEST_FUNC_NAME
        self.assertEqual( _getDottedName( dotted ), _TEST_FUNC_NAME )
        self.assertEqual( type( _getDottedName( dotted ) ), str )

    def test__getDottedName_class( self ):

        from Products.CMFSetup.utils import _getDottedName

        self.assertEqual( _getDottedName( Whatever ), _WHATEVER_NAME )

    def test__getDottedName_inst( self ):

        from Products.CMFSetup.utils import _getDottedName

        self.assertEqual( _getDottedName( whatever_inst )
                        , _WHATEVER_INST_NAME )

    def test__getDottedName_noname( self ):

        from Products.CMFSetup.utils import _getDottedName

        class Doh:
            pass

        doh = Doh()
        self.assertRaises( ValueError, _getDottedName, doh )


class DummyObject(Folder):

    meta_type = 'Dummy Type'
    _properties = ()


class _ConfiguratorBaseTests(BaseRegistryTests):

    def _initSite(self, foo=2):

        self.root.site = Folder(id='site')
        site = self.root.site

        site.dummy = DummyObject(id='dummy')
        site.dummy.foobarbaz = ('Foo', 'Bar', 'Baz')

        if foo > 0:
            site.dummy._setProperty('foo_boolean', '', 'boolean')
            site.dummy._setProperty('foo_date', '', 'date')
            site.dummy._setProperty('foo_float', '', 'float')
            site.dummy._setProperty('foo_int', '', 'int')
            site.dummy._setProperty('foo_lines', '', 'lines')
            site.dummy._setProperty('foo_long', '', 'long')
            site.dummy._setProperty('foo_string', '', 'string')
            site.dummy._setProperty('foo_text', '', 'text')
            site.dummy._setProperty('foo_tokens', (), 'tokens')
            site.dummy._setProperty('foo_selection', 'foobarbaz', 'selection')
            site.dummy._setProperty('foo_mselection', 'foobarbaz',
                                    'multiple selection')

        if foo > 1:
            site.dummy._updateProperty('foo_boolean', 'True')
            site.dummy._updateProperty('foo_date', '2000/01/01')
            site.dummy._updateProperty('foo_float', '1.1')
            site.dummy._updateProperty('foo_int', '1')
            site.dummy._updateProperty('foo_lines', 'Foo\nLines')
            site.dummy._updateProperty('foo_long', '1')
            site.dummy._updateProperty('foo_string', 'Foo String')
            site.dummy._updateProperty('foo_text', 'Foo\nText')
            site.dummy._updateProperty( 'foo_tokens', ('Foo', 'Tokens') )
            site.dummy._updateProperty('foo_selection', 'Foo')
            site.dummy._updateProperty( 'foo_mselection', ('Foo', 'Baz') )

        return site


class ExportConfiguratorBaseTests(_ConfiguratorBaseTests):

    def _getTargetClass(self):

        from Products.CMFSetup.utils import ExportConfiguratorBase

        class Configurator(ExportConfiguratorBase):
            def _getExportTemplate(self):
                return None

        return Configurator

    def test__extractProperty_normal(self):

        site = self._initSite()

        EXPECTED = _NORMAL_PROPERTY_INFO

        configurator = self._makeOne(site)
        prop_infos = [ configurator._extractProperty(site.dummy, prop_def)
                       for prop_def in site.dummy._propertyMap() ]

        self.assertEqual( len(prop_infos), len(EXPECTED) )

        for found, expected in zip(prop_infos, EXPECTED):
            self.assertEqual(found, expected)

    def test__extractObject_normal(self):

        site = self._initSite()

        EXPECTED = { 'id': 'dummy',
                     'meta_type': 'Dummy Type',
                     'properties': _NORMAL_PROPERTY_INFO,
                     'subobjects': () }

        configurator = self._makeOne(site)
        obj_info = configurator._extractObject(site.dummy)

        self.assertEqual( len(obj_info), len(EXPECTED) )
        self.assertEqual(obj_info, EXPECTED)

    def test_generatePropertyNodes_normal(self):

        site = self._initSite()
        configurator = self._makeOne(site).__of__(site)
        prop_infos = [ configurator._extractProperty(site.dummy, prop_def)
                       for prop_def in site.dummy._propertyMap() ]
        nodes = configurator.generatePropertyNodes(prop_infos)
        xml = '<?xml version="1.0"?><dummy>%s\n</dummy>' % nodes

        self._compareDOM(xml, _NORMAL_PROPERTY_EXPORT)

    def test_generateObjectNodes_normal(self):

        site = self._initSite()
        configurator = self._makeOne(site).__of__(site)
        obj_infos = ( configurator._extractObject(site.dummy), )
        nodes = configurator.generateObjectNodes(obj_infos)
        xml = '<?xml version="1.0"?><dummy>%s\n</dummy>' % nodes

        self._compareDOM(xml, _NORMAL_OBJECT_EXPORT)


class ImportConfiguratorBaseTests(_ConfiguratorBaseTests):

    def _getTargetClass(self):

        from Products.CMFSetup.utils import ImportConfiguratorBase
        from Products.CMFSetup.utils import CONVERTER, DEFAULT, KEY

        class Configurator(ImportConfiguratorBase):
            def _getImportMapping(self):
                return {
                  'dummy':
                    { 'property':    {KEY: 'properties', DEFAULT: ()},
                      'description': {CONVERTER: self._convertToUnique} } }

        return Configurator


    def test_parseXML_normal(self):

        site = self._initSite()
        configurator = self._makeOne(site)
        site_info = configurator.parseXML(_NORMAL_PROPERTY_EXPORT)

        self.assertEqual( len( site_info['properties'] ), 11 )

        info = site_info['properties'][0]
        self.assertEqual( info['id'], 'foo_boolean' )
        self.assertEqual( info['value'], 'True' )
        self.assertEqual( len( info['elements'] ), 0 )
        self.assertEqual( info['type'], 'boolean' )

        info = site_info['properties'][1]
        self.assertEqual( info['id'], 'foo_date' )
        self.assertEqual( info['value'], '2000/01/01' )
        self.assertEqual( len( info['elements'] ), 0 )
        self.assertEqual( info['type'], 'date' )

        info = site_info['properties'][2]
        self.assertEqual( info['id'], 'foo_float' )
        self.assertEqual( info['value'], '1.1' )
        self.assertEqual( len( info['elements'] ), 0 )
        self.assertEqual( info['type'], 'float' )

        info = site_info['properties'][3]
        self.assertEqual( info['id'], 'foo_int' )
        self.assertEqual( info['value'], '1' )
        self.assertEqual( len( info['elements'] ), 0 )
        self.assertEqual( info['type'], 'int' )

        info = site_info['properties'][4]
        self.assertEqual( info['id'], 'foo_lines' )
        self.assertEqual( info['value'], '' )
        self.assertEqual( len( info['elements'] ), 2 )
        self.assertEqual( info['elements'][0], 'Foo' )
        self.assertEqual( info['elements'][1], 'Lines' )
        self.assertEqual( info['type'], 'lines' )

        info = site_info['properties'][5]
        self.assertEqual( info['id'], 'foo_long' )
        self.assertEqual( info['value'], '1' )
        self.assertEqual( len( info['elements'] ), 0 )
        self.assertEqual( info['type'], 'long' )

        info = site_info['properties'][6]
        self.assertEqual( info['id'], 'foo_string' )
        self.assertEqual( info['value'], 'Foo String' )
        self.assertEqual( len( info['elements'] ), 0 )
        self.assertEqual( info['type'], 'string' )

        info = site_info['properties'][7]
        self.assertEqual( info['id'], 'foo_text' )
        self.assertEqual( info['value'], 'Foo\nText' )
        self.assertEqual( len( info['elements'] ), 0 )
        self.assertEqual( info['type'], 'text' )

        info = site_info['properties'][8]
        self.assertEqual( info['id'], 'foo_tokens' )
        self.assertEqual( info['value'], '' )
        self.assertEqual( len( info['elements'] ), 2 )
        self.assertEqual( info['elements'][0], 'Foo' )
        self.assertEqual( info['elements'][1], 'Tokens' )
        self.assertEqual( info['type'], 'tokens' )

        info = site_info['properties'][9]
        self.assertEqual( info['id'], 'foo_selection' )
        self.assertEqual( info['value'], 'Foo' )
        self.assertEqual( len( info['elements'] ), 0 )
        self.assertEqual( info['type'], 'selection' )
        self.assertEqual( info['select_variable'], 'foobarbaz' )

        info = site_info['properties'][10]
        self.assertEqual( info['id'], 'foo_mselection' )
        self.assertEqual( info['value'], '' )
        self.assertEqual( len( info['elements'] ), 2 )
        self.assertEqual( info['elements'][0], 'Foo' )
        self.assertEqual( info['elements'][1], 'Baz' )
        self.assertEqual( info['type'], 'multiple selection' )
        self.assertEqual( info['select_variable'], 'foobarbaz' )

    def test_parseXML_special(self):

        site = self._initSite()
        configurator = self._makeOne(site)
        try:
            site_info = configurator.parseXML(_SPECIAL_IMPORT)
        except KeyError:
            self.fail('CMF Collector issue #352 (comment or empty '
                      'description bug): KeyError raised')

        self.assertEqual( len(site_info), 2 )
        self.assertEqual( site_info['description'], '' )
        self.assertEqual( len(site_info['properties']), 0 )

    def test_initProperty_normal(self):

        EXPECTED = _NORMAL_PROPERTY_INFO

        site = self._initSite(0)
        dummy = site.dummy
        configurator = self._makeOne(site)
        site_info = configurator.parseXML(_NORMAL_PROPERTY_EXPORT)

        self.assertEqual( len( dummy.propertyIds() ), 0 )

        for prop_info in site_info['properties']:
            configurator.initProperty(dummy, prop_info)

        self.assertEqual( len( dummy.propertyIds() ), len(EXPECTED) )

        for exp_info in EXPECTED:
            exp_id = exp_info['id']
            exp_value = exp_info['elements'] or exp_info['value']
            self.failUnless( exp_id in dummy.propertyIds() )
            self.assertEqual( dummy.getProperty(exp_id), exp_value )

    def test_initProperty_fixed(self):

        EXPECTED = _NORMAL_PROPERTY_INFO

        site = self._initSite(1)
        dummy = site.dummy
        configurator = self._makeOne(site)
        site_info = configurator.parseXML(_FIXED_PROPERTY_EXPORT)

        self.assertEqual( len( dummy.propertyIds() ), 11 )

        for prop_info in site_info['properties']:
            configurator.initProperty(dummy, prop_info)

        self.assertEqual( len( dummy.propertyIds() ), len(EXPECTED) )

        for exp_info in EXPECTED:
            exp_id = exp_info['id']
            exp_value = exp_info['elements'] or exp_info['value']
            self.failUnless( exp_id in dummy.propertyIds() )
            self.assertEqual( dummy.getProperty(exp_id), exp_value )


def test_suite():
    # reimport to make sure tests are run from Products
    from Products.CMFSetup.tests.test_utils import UtilsTests

    return unittest.TestSuite((
        unittest.makeSuite( UtilsTests ),
        unittest.makeSuite( ImportConfiguratorBaseTests ),
        unittest.makeSuite( ExportConfiguratorBaseTests ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
