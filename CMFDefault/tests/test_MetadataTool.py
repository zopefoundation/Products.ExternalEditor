import Zope
from Acquisition import aq_base
from unittest import TestCase, TestSuite, makeSuite, main

from Products.CMFDefault.MetadataTool import \
     MetadataElementPolicy, MetadataTool, ElementSpec, \
     DEFAULT_ELEMENT_SPECS, MetadataError

from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl

class TestMetadataElementPolicy( TestCase ):

    def setUp( self ):
        self.sv_policy = MetadataElementPolicy( 0 )
        self.mv_policy = MetadataElementPolicy( 1 )

    def tearDown( self ):
        del self.sv_policy
        del self.mv_policy

    def test_emptySV( self ):
        assert not self.sv_policy.isMultiValued()
        assert not self.sv_policy.isRequired()
        assert not self.sv_policy.supplyDefault()
        assert not self.sv_policy.defaultValue()
        assert not self.sv_policy.enforceVocabulary()
        assert not self.sv_policy.allowedVocabulary()

    def test_editSV( self ):
        self.sv_policy.edit( 1, 1, 'xxx', 0, '' )
        assert not self.sv_policy.isMultiValued()
        assert self.sv_policy.isRequired()
        assert self.sv_policy.supplyDefault()
        assert self.sv_policy.defaultValue() == 'xxx'
        assert not self.sv_policy.enforceVocabulary()
        assert not self.sv_policy.allowedVocabulary()

    def test_emptyMV( self ):
        assert self.mv_policy.isMultiValued()
        assert not self.mv_policy.isRequired()
        assert not self.mv_policy.supplyDefault()
        assert not self.mv_policy.defaultValue()
        assert not self.mv_policy.enforceVocabulary()
        assert not self.mv_policy.allowedVocabulary()

    def test_editMV( self ):
        self.mv_policy.edit( 1, 1, 'xxx', 1, ( 'xxx', 'yyy' ) )
        assert self.mv_policy.isMultiValued()
        assert self.mv_policy.isRequired()
        assert self.mv_policy.supplyDefault()
        assert self.mv_policy.defaultValue() == 'xxx'
        assert self.mv_policy.enforceVocabulary()
        assert len( self.mv_policy.allowedVocabulary() ) == 2
        assert 'xxx' in self.mv_policy.allowedVocabulary()
        assert 'yyy' in self.mv_policy.allowedVocabulary()

class TestElementSpec( TestCase ):

    def setUp( self ):
        self.sv_spec    = ElementSpec( 0 )
        self.mv_spec    = ElementSpec( 1 )

    def tearDown( self ):
        del self.sv_spec
        del self.mv_spec

    def test_empty( self ):
        assert not self.sv_spec.isMultiValued()
        assert self.sv_spec.getPolicy() == self.sv_spec.getPolicy( 'XYZ' )
        policies = self.sv_spec.listPolicies()
        assert len( policies ) == 1
        assert policies[0][0] is None

        assert self.mv_spec.isMultiValued()
        assert self.mv_spec.getPolicy() == self.mv_spec.getPolicy( 'XYZ' )
        policies = self.mv_spec.listPolicies()
        assert len( policies ) == 1
        assert policies[0][0] is None

class Foo( DefaultDublinCoreImpl ):

    description = title = language = format = rights = ''
    subject = ()

    def __init__( self ):
        pass # skip DDCI's default values

    def Type( self ):
        return 'Foo'

class Bar( Foo ):

    def Type( self ):
        return 'Bar'

class TestMetadataTool( TestCase ):

    def setUp( self ):
        self.tool = MetadataTool()

    def tearDown( self ):
        del self.tool

    def test_empty( self ):

        assert not self.tool.getPublisher()
        assert self.tool.getFullName( 'foo' ) == 'foo'

        specs = list( self.tool.listElementSpecs() )
        defaults = list( DEFAULT_ELEMENT_SPECS )
        specs.sort(); defaults.sort()

        assert len( specs ) == len( defaults )
        for i in range( len( specs ) ):
            assert specs[i][0] == defaults[i][0]
            assert specs[i][1].isMultiValued() == defaults[i][1]
            policies = specs[i][1].listPolicies()
            assert len( policies ) == 1
            assert policies[0][0] is None

        assert not self.tool.getElementSpec( 'Title'        ).isMultiValued()
        assert not self.tool.getElementSpec( 'Description'  ).isMultiValued()
        assert     self.tool.getElementSpec( 'Subject'      ).isMultiValued()
        assert not self.tool.getElementSpec( 'Format'       ).isMultiValued()
        assert not self.tool.getElementSpec( 'Language'     ).isMultiValued()
        assert not self.tool.getElementSpec( 'Rights'       ).isMultiValued()

        try:
            dummy = self.tool.getElementSpec( 'Foo' )
        except KeyError:
            pass
        else:
            assert 0, "Expected KeyError"
        
        assert not self.tool.listAllowedSubjects()
        assert not self.tool.listAllowedFormats()
        assert not self.tool.listAllowedLanguages()
        assert not self.tool.listAllowedRights()

    def test_add( self ):
        self.tool.addElementSpec( 'Rating', 1 )
        assert len( self.tool.listElementSpecs() ) \
            == len( DEFAULT_ELEMENT_SPECS ) + 1
        rating = self.tool.getElementSpec( 'Rating' )
        assert rating.isMultiValued()

    def test_remove( self ):
        self.tool.removeElementSpec( 'Rights' )

        assert len( self.tool.listElementSpecs() ) \
            == len( DEFAULT_ELEMENT_SPECS ) - 1

        try:
            dummy = self.tool.getElementSpec( 'Rights' )
        except KeyError:
            pass
        else:
            assert 0, "Expected KeyError"

        try:
            self.tool.removeElementSpec( 'Foo' )
        except KeyError:
            pass
        else:
            assert 0, "Expected KeyError"

    def test_simplePolicies( self ):

        tSpec = self.tool.getElementSpec( 'Title' )

        # Fetch default policy.
        tDef  = tSpec.getPolicy()
        assert not tDef.isRequired()
        assert not tDef.supplyDefault()
        assert not tDef.defaultValue()

        # Fetch (default) policy for a type.
        tDoc  = tSpec.getPolicy( 'Document' )
        self.assertEqual(aq_base(tDoc), aq_base(tDef))

        # Changing default changes policies found from there.
        tDef.edit( 1, 1, 'xyz', 0, () )
        assert tDef.isRequired()
        assert tDef.supplyDefault()
        assert tDef.defaultValue() == 'xyz'
        assert tDoc.isRequired()
        assert tDoc.supplyDefault()
        assert tDoc.defaultValue() == 'xyz'

        tSpec.addPolicy( 'Document' )
        assert len( tSpec.listPolicies() ) == 2

        tDoc  = tSpec.getPolicy( 'Document' )
        self.assertNotEqual(aq_base(tDoc), aq_base(tDef))
        assert not tDoc.isRequired()
        assert not tDoc.supplyDefault()
        assert not tDoc.defaultValue()

        tSpec.removePolicy( 'Document' )
        tDoc  = tSpec.getPolicy( 'Document' )
        self.assertEqual(aq_base(tDoc), aq_base(tDef))
        assert tDoc.isRequired()
        assert tDoc.supplyDefault()
        assert tDoc.defaultValue() == 'xyz'

    def test_multiValuedPolicies( self ):

        sSpec = self.tool.getElementSpec( 'Subject' )

        # Fetch default policy.
        sDef  = sSpec.getPolicy()
        assert not sDef.isRequired()
        assert not sDef.supplyDefault()
        assert not sDef.defaultValue()
        assert not sDef.enforceVocabulary()
        assert not sDef.allowedVocabulary()

        # Fetch (default) policy for a type.
        sDoc  = sSpec.getPolicy( 'Document' )
        self.assertEqual(aq_base(sDoc), aq_base(sDef))

        # Changing default changes policies found from there.
        sDef.edit( 1, 1, 'xyz', 1, ( 'foo', 'bar' ) )
        assert sDef.isRequired()
        assert sDef.supplyDefault()
        assert sDef.defaultValue() == 'xyz'
        assert sDoc.isRequired()
        assert sDoc.supplyDefault()
        assert sDoc.defaultValue() == 'xyz'
        assert sDef.enforceVocabulary()
        assert len( sDef.allowedVocabulary() ) == 2
        assert 'foo' in sDef.allowedVocabulary()
        assert 'bar' in sDef.allowedVocabulary()
        assert sDoc.enforceVocabulary()
        assert len( sDoc.allowedVocabulary() ) == 2
        assert 'foo' in sDoc.allowedVocabulary()
        assert 'bar' in sDoc.allowedVocabulary()

        sSpec.addPolicy( 'Document' )
        assert len( sSpec.listPolicies() ) == 2

        sDoc  = sSpec.getPolicy( 'Document' )
        self.assertNotEqual(aq_base(sDoc), aq_base(sDef))
        assert not sDoc.isRequired()
        assert not sDoc.supplyDefault()
        assert not sDoc.defaultValue()
        assert not sDoc.enforceVocabulary()
        assert not sDoc.allowedVocabulary()

        sSpec.removePolicy( 'Document' )
        sDoc  = sSpec.getPolicy( 'Document' )
        self.assertEqual(aq_base(sDoc), aq_base(sDef))
        assert sDoc.isRequired()
        assert sDoc.supplyDefault()
        assert sDoc.defaultValue() == 'xyz'
        assert sDoc.enforceVocabulary()
        assert len( sDoc.allowedVocabulary() ) == 2
        assert 'foo' in sDoc.allowedVocabulary()
        assert 'bar' in sDoc.allowedVocabulary()

    def test_vocabularies( self ):
        fSpec   = self.tool.getElementSpec( 'Format' )
        fDef    = fSpec.getPolicy()
        formats = ( 'text/plain', 'text/html' )
        fDef.edit( 0, 0, '', 0, ( 'text/plain', 'text/html' ) )
        assert self.tool.listAllowedFormats() == formats
        
        foo = Foo()
        assert self.tool.listAllowedFormats( foo ) == formats
        fSpec.addPolicy( 'Foo' )
        assert not self.tool.listAllowedFormats( foo )
        foo_formats = ( 'image/jpeg', 'image/gif', 'image/png' )
        fFoo        = fSpec.getPolicy( 'Foo' )
        fFoo.edit( 0, 0, '', 0, foo_formats )
        assert self.tool.listAllowedFormats( foo ) == foo_formats

    def test_initialValues( self ):
        foo = Foo()
        assert not foo.Title()
        assert not foo.Description()
        assert not foo.Subject()
        assert not foo.Format(), foo.Format()
        assert not foo.Language()
        assert not foo.Rights()

        self.tool.setInitialMetadata( foo )
        assert not foo.Title()
        assert not foo.Description()
        assert not foo.Subject()
        assert not foo.Format()
        assert not foo.Language()
        assert not foo.Rights()

        # Test default policy.
        foo     = Foo()
        fSpec   = self.tool.getElementSpec( 'Format' )
        fPolicy = fSpec.getPolicy()
        fPolicy.edit( 0, 1, 'text/plain', 0, () )
        self.tool.setInitialMetadata( foo )
        assert not foo.Title()
        assert not foo.Description()
        assert not foo.Subject()
        assert foo.Format() == 'text/plain'
        assert not foo.Language()
        assert not foo.Rights()

        # Test type-specific policy.
        foo     = Foo()
        tSpec   = self.tool.getElementSpec( 'Title' )
        tSpec.addPolicy( 'Foo' )
        tPolicy = tSpec.getPolicy( foo.Type() )
        tPolicy.edit( 1, 0, '', 0, () )

        try:
            self.tool.setInitialMetadata( foo )
        except MetadataError:
            pass
        else:
            assert 0, "Expected MetadataError"

        foo.setTitle( 'Foo title' )
        self.tool.setInitialMetadata( foo )
        assert foo.Title() == 'Foo title'
        assert not foo.Description()
        assert not foo.Subject()
        assert foo.Format() == 'text/plain'
        assert not foo.Language()
        assert not foo.Rights()

        #   Ensure Foo's policy doesn't interfere with other types.
        bar = Bar()
        self.tool.setInitialMetadata( bar )
        assert not bar.Title()
        assert not bar.Description()
        assert not bar.Subject()
        assert bar.Format() == 'text/plain'
        assert not bar.Language()
        assert not bar.Rights()

    def test_validation( self ):

        foo = Foo()
        self.tool.setInitialMetadata( foo )
        self.tool.validateMetadata( foo )

        tSpec   = self.tool.getElementSpec( 'Title' )
        tSpec.addPolicy( 'Foo' )
        tPolicy = tSpec.getPolicy( foo.Type() )
        tPolicy.edit( 1, 0, '', 0, () )

        try:
            self.tool.validateMetadata( foo )
        except MetadataError:
            pass
        else:
            assert 0, "Expected MetadataError"

        foo.setTitle( 'Foo title' )
        self.tool.validateMetadata( foo )


def test_suite():
    return TestSuite((
        makeSuite(TestMetadataElementPolicy),
        makeSuite(TestElementSpec),
        makeSuite(TestMetadataTool),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
