from unittest import TestCase, TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()
from Interface.Verify import verifyClass

from Acquisition import aq_base

from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl

class TestMetadataElementPolicy( TestCase ):

    def _getTargetClass( self ):

        from Products.CMFDefault.MetadataTool import MetadataElementPolicy
        return MetadataElementPolicy

    def _makeOne( self, multi_valued=False ):

        return self._getTargetClass()( multi_valued )

    def test_emptySV( self ):

        sv_policy = self._makeOne()

        self.failIf( sv_policy.isMultiValued() )
        self.failIf( sv_policy.isRequired() )
        self.failIf( sv_policy.supplyDefault() )
        self.failIf( sv_policy.defaultValue() )
        self.failIf( sv_policy.enforceVocabulary() )
        self.failIf( sv_policy.allowedVocabulary() )

    def test_editSV( self ):

        sv_policy = self._makeOne()

        sv_policy.edit( is_required=True
                      , supply_default=True
                      , default_value='xxx'
                      , enforce_vocabulary=False
                      , allowed_vocabulary=''
                      )

        self.failIf( sv_policy.isMultiValued() )
        self.failUnless( sv_policy.isRequired() )
        self.failUnless( sv_policy.supplyDefault() )
        self.assertEqual( sv_policy.defaultValue(), 'xxx' )
        self.failIf( sv_policy.enforceVocabulary() )
        self.failIf( sv_policy.allowedVocabulary() )

    def test_emptyMV( self ):

        mv_policy = self._makeOne( True )

        self.failUnless( mv_policy.isMultiValued() )
        self.failIf( mv_policy.isRequired() )
        self.failIf( mv_policy.supplyDefault() )
        self.failIf( mv_policy.defaultValue() )
        self.failIf( mv_policy.enforceVocabulary() )
        self.failIf( mv_policy.allowedVocabulary() )

    def test_editMV( self ):

        mv_policy = self._makeOne( True )

        mv_policy.edit( is_required=True
                      , supply_default=True
                      , default_value='xxx'
                      , enforce_vocabulary=True
                      , allowed_vocabulary=( 'xxx', 'yyy' )
                      )

        self.failUnless( mv_policy.isMultiValued() )
        self.failUnless( mv_policy.isRequired() )
        self.failUnless( mv_policy.supplyDefault() )
        self.assertEqual( mv_policy.defaultValue(), 'xxx' )
        self.failUnless( mv_policy.enforceVocabulary() )

        self.assertEqual( len( mv_policy.allowedVocabulary() ), 2 )
        self.failUnless( 'xxx' in mv_policy.allowedVocabulary() )
        self.failUnless( 'yyy' in mv_policy.allowedVocabulary() )

class TestElementSpec( TestCase ):

    def _getTargetClass( self ):

        from Products.CMFDefault.MetadataTool import ElementSpec
        return ElementSpec

    def _makeOne( self, multi_valued=False ):

        return self._getTargetClass()( multi_valued )

    def test_single_valued( self ):

        sv_spec = self._makeOne()

        self.failIf( sv_spec.isMultiValued() )
        self.assertEqual( sv_spec.getPolicy(), sv_spec.getPolicy( 'XYZ' ) )

        policies = sv_spec.listPolicies()
        self.assertEqual( len( policies ), 1 )
        self.assertEqual( policies[0][0], None )

    def test_multi_valued( self ):

        mv_spec = self._makeOne( True )

        self.failUnless( mv_spec.isMultiValued() )
        self.assertEqual( mv_spec.getPolicy(), mv_spec.getPolicy( 'XYZ' ) )

        policies = mv_spec.listPolicies()
        self.assertEqual( len( policies ), 1 )
        self.assertEqual( policies[0][0], None )


class Foo( DefaultDublinCoreImpl ):

    description = title = language = format = rights = ''
    subject = ()

    def __init__( self ):
        pass # skip DDCI's default values

    def getPortalTypeName( self ):
        return 'Foo'


class Bar( Foo ):

    def getPortalTypeName( self ):
        return 'Bar'


class TestMetadataTool( TestCase ):

    def _getTargetClass( self ):

        from Products.CMFDefault.MetadataTool import MetadataTool
        return MetadataTool

    def _makeOne( self, *args, **kw ):

        return self._getTargetClass()( *args, **kw )

    def test_interface( self ):

        from Products.CMFCore.interfaces.portal_metadata \
                import portal_metadata as IMetadataTool
        from Products.CMFCore.interfaces.portal_actions \
                import ActionProvider as IActionProvider

        verifyClass(IMetadataTool, self._getTargetClass())
        verifyClass(IActionProvider, self._getTargetClass())

    def test_empty( self ):

        from Products.CMFDefault.MetadataTool import DEFAULT_ELEMENT_SPECS

        tool = self._makeOne()

        self.failIf( tool.getPublisher() )
        self.assertEqual( tool.getFullName( 'foo' ), 'foo' )

        specs = list( tool.listElementSpecs() )
        defaults = list( DEFAULT_ELEMENT_SPECS )
        specs.sort()
        defaults.sort()

        self.assertEqual( len( specs ), len( defaults ) )

        for i in range( len( specs ) ):
            self.assertEqual( specs[i][0], defaults[i][0] )
            self.assertEqual( specs[i][1].isMultiValued(), defaults[i][1] )
            policies = specs[i][1].listPolicies()
            self.assertEqual( len( policies ), 1 )
            self.assertEqual( policies[0][0], None )

        self.failIf( tool.getElementSpec( 'Title'        ).isMultiValued() )
        self.failIf( tool.getElementSpec( 'Description'  ).isMultiValued() )
        self.failUnless( tool.getElementSpec( 'Subject'  ).isMultiValued() )
        self.failIf( tool.getElementSpec( 'Format'       ).isMultiValued() )
        self.failIf( tool.getElementSpec( 'Language'     ).isMultiValued() )
        self.failIf( tool.getElementSpec( 'Rights'       ).isMultiValued() )

        self.assertRaises( KeyError, tool.getElementSpec, 'Foo' )

        self.assertEqual( len( tool.listAllowedSubjects() ), 0 )
        self.assertEqual( len( tool.listAllowedFormats() ), 0 )
        self.assertEqual( len( tool.listAllowedLanguages() ), 0 )
        self.assertEqual( len( tool.listAllowedRights() ), 0 )

    def test_addElementSpec( self ):

        from Products.CMFDefault.MetadataTool import DEFAULT_ELEMENT_SPECS

        tool = self._makeOne()

        tool.addElementSpec( 'Rating', is_multi_valued=True )

        self.assertEqual( len( tool.listElementSpecs() )
                        , len( DEFAULT_ELEMENT_SPECS ) + 1 )

        rating = tool.getElementSpec( 'Rating' )
        self.failUnless( rating.isMultiValued() )

    def test_remove( self ):

        from Products.CMFDefault.MetadataTool import DEFAULT_ELEMENT_SPECS

        tool = self._makeOne()

        tool.removeElementSpec( 'Rights' )

        self.assertEqual( len( tool.listElementSpecs() )
                        , len( DEFAULT_ELEMENT_SPECS ) - 1 )

        self.assertRaises( KeyError, tool.getElementSpec, 'Rights' )

    def test_remove_nonesuch( self ):

        from Products.CMFDefault.MetadataTool import DEFAULT_ELEMENT_SPECS

        tool = self._makeOne()
        self.assertRaises( KeyError, tool.removeElementSpec, 'Foo' )

    def test_simplePolicies_without_override( self ):

        tool = self._makeOne()

        tSpec = tool.getElementSpec( 'Title' )

        tDef = tSpec.getPolicy()
        self.failIf( tDef.isRequired() )
        self.failIf( tDef.supplyDefault() )
        self.failIf( tDef.defaultValue() )

        tDoc = tSpec.getPolicy( 'Document' )
        self.failUnless( aq_base( tDoc ) is aq_base( tDef ) )

    def test_simplePolicies_editing( self ):

        tool = self._makeOne()
        tSpec = tool.getElementSpec( 'Title' )
        tDef = tSpec.getPolicy()
        tDoc = tSpec.getPolicy( 'Document' )

        tDef.edit( is_required=True
                 , supply_default=True
                 , default_value='xyz'
                 , enforce_vocabulary=False
                 , allowed_vocabulary=()
                 )

        self.failUnless( tDef.isRequired() )
        self.failUnless( tDef.supplyDefault() )
        self.assertEqual( tDef.defaultValue(), 'xyz' )

        self.failUnless( tDoc.isRequired() )
        self.failUnless( tDoc.supplyDefault() )
        self.assertEqual( tDoc.defaultValue(), 'xyz' )

    def test_simplePolicies_overriding( self ):

        tool = self._makeOne()
        tSpec = tool.getElementSpec( 'Title' )
        tDef = tSpec.getPolicy()

        tDef.edit( is_required=True
                 , supply_default=True
                 , default_value='xyz'
                 , enforce_vocabulary=False
                 , allowed_vocabulary=()
                 )

        tSpec.addPolicy( 'Document' )
        self.assertEqual( len( tSpec.listPolicies() ), 2 )

        tDoc = tSpec.getPolicy( 'Document' )
        self.failIf( aq_base( tDoc ) is aq_base( tDef ) )
        self.failIf( tDoc.isRequired() )
        self.failIf( tDoc.supplyDefault() )
        self.failIf( tDoc.defaultValue() )

        tSpec.removePolicy( 'Document' )
        tDoc = tSpec.getPolicy( 'Document' )
        self.assertEqual(aq_base(tDoc), aq_base(tDef))
        self.failUnless( tDoc.isRequired() )
        self.failUnless( tDoc.supplyDefault() )
        self.assertEqual( tDoc.defaultValue(), 'xyz' )

    def test_multiValuedPolicies_without_override( self ):

        tool = self._makeOne()

        sSpec = tool.getElementSpec( 'Subject' )

        sDef = sSpec.getPolicy()
        self.failIf( sDef.isRequired() )
        self.failIf( sDef.supplyDefault() )
        self.failIf( sDef.defaultValue() )
        self.failIf( sDef.enforceVocabulary() )
        self.failIf( sDef.allowedVocabulary() )

        sDoc = sSpec.getPolicy( 'Document' )
        self.assertEqual( aq_base( sDoc ), aq_base( sDef ))

    def test_multiValuedPolicies_editing( self ):

        tool = self._makeOne()
        sSpec = tool.getElementSpec( 'Subject' )
        sDef = sSpec.getPolicy()
        sDoc = sSpec.getPolicy( 'Document' )

        sDef.edit( is_required=True
                 , supply_default=True
                 , default_value='xyz'
                 , enforce_vocabulary=True
                 , allowed_vocabulary=( 'foo', 'bar' )
                 )

        self.failUnless( sDef.isRequired() )
        self.failUnless( sDef.supplyDefault() )
        self.assertEqual( sDef.defaultValue(), 'xyz' )

        self.failUnless( sDoc.isRequired() )
        self.failUnless( sDoc.supplyDefault() )
        self.assertEqual( sDoc.defaultValue(), 'xyz' )

        self.failUnless( sDef.enforceVocabulary() )
        self.assertEqual( len( sDef.allowedVocabulary() ), 2 )
        self.failUnless( 'foo' in sDef.allowedVocabulary() )
        self.failUnless( 'bar' in sDef.allowedVocabulary() )

        self.failUnless( sDoc.enforceVocabulary() )
        self.assertEqual( len( sDoc.allowedVocabulary() ), 2 )
        self.failUnless( 'foo' in sDoc.allowedVocabulary() )
        self.failUnless( 'bar' in sDoc.allowedVocabulary() )

    def test_multiValuedPolicies_overriding( self ):

        tool = self._makeOne()
        sSpec = tool.getElementSpec( 'Subject' )
        sDef = sSpec.getPolicy()

        sDef.edit( is_required=True
                 , supply_default=True
                 , default_value='xyz'
                 , enforce_vocabulary=True
                 , allowed_vocabulary=( 'foo', 'bar' )
                 )

        sSpec.addPolicy( 'Document' )
        self.assertEqual( len( sSpec.listPolicies() ), 2 )

        sDoc = sSpec.getPolicy( 'Document' )
        self.failIf( aq_base( sDoc ) is aq_base( sDef ) )
 
        self.failIf( sDoc.isRequired() )
        self.failIf( sDoc.supplyDefault() )
        self.failIf( sDoc.defaultValue() )
        self.failIf( sDoc.enforceVocabulary() )
        self.failIf( sDoc.allowedVocabulary() )

        sSpec.removePolicy( 'Document' )
        sDoc = sSpec.getPolicy( 'Document' )
        self.assertEqual(aq_base(sDoc), aq_base(sDef))
        self.failUnless( sDoc.isRequired() )
        self.failUnless( sDoc.supplyDefault() )
        self.assertEqual( sDoc.defaultValue(), 'xyz' )
        self.failUnless( sDoc.enforceVocabulary() )
        self.assertEqual( len( sDoc.allowedVocabulary() ), 2 )
        self.failUnless( 'foo' in sDoc.allowedVocabulary() )
        self.failUnless( 'bar' in sDoc.allowedVocabulary() )

    def test_vocabularies_default( self ):

        tool = self._makeOne()

        fSpec = tool.getElementSpec( 'Format' )
        fDef = fSpec.getPolicy()
        formats = ( 'text/plain', 'text/html' )
        fDef.edit( is_required=False
                 , supply_default=False
                 , default_value=''
                 , enforce_vocabulary=False
                 , allowed_vocabulary=( 'text/plain', 'text/html' )
                 )

        self.assertEqual( tool.listAllowedFormats(), formats )

        foo = Foo()
        self.assertEqual( tool.listAllowedFormats( foo ), formats )

    def test_vocabularies_overriding( self ):

        tool = self._makeOne()
        foo = Foo()

        fSpec = tool.getElementSpec( 'Format' )
        fDef = fSpec.getPolicy()
        formats = ( 'text/plain', 'text/html' )
        fDef.edit( is_required=False
                 , supply_default=False
                 , default_value=''
                 , enforce_vocabulary=False
                 , allowed_vocabulary=( 'text/plain', 'text/html' )
                 )

        fSpec.addPolicy( 'Foo' )

        self.failIf( tool.listAllowedFormats( foo ) )

        foo_formats = ( 'image/jpeg', 'image/gif', 'image/png' )
        fFoo = fSpec.getPolicy( 'Foo' )
        fFoo.edit( is_required=False
                 , supply_default=False
                 , default_value=''
                 , enforce_vocabulary=False
                 , allowed_vocabulary=foo_formats
                 )

        self.assertEqual( tool.listAllowedFormats( foo ), foo_formats )

    def test_initialValues_no_policy( self ):

        tool = self._makeOne()

        foo = Foo()
        self.assertEqual( foo.Title(), '' )
        self.assertEqual( foo.Description(), '' )
        self.assertEqual( foo.Subject(), () )
        self.assertEqual( foo.Format(), '' )
        self.assertEqual( foo.Language(), '' )
        self.assertEqual( foo.Rights(), '' )

        tool.setInitialMetadata( foo )
        self.assertEqual( foo.Title(), '' )
        self.assertEqual( foo.Description(), '' )
        self.assertEqual( foo.Subject(), () )
        self.assertEqual( foo.Format(), '' )
        self.assertEqual( foo.Language(), '' )
        self.assertEqual( foo.Rights(), '' )

    def test_initialValues_default_policy( self ):

        tool = self._makeOne()

        fSpec = tool.getElementSpec( 'Format' )
        fPolicy = fSpec.getPolicy()
        fPolicy.edit( is_required=False
                    , supply_default=True
                    , default_value='text/plain'
                    , enforce_vocabulary=False
                    , allowed_vocabulary=()
                    )

        foo = Foo()
        tool.setInitialMetadata( foo )

        self.assertEqual( foo.Title(), '' )
        self.assertEqual( foo.Description(), '' )
        self.assertEqual( foo.Subject(), ())
        self.assertEqual( foo.Format(), 'text/plain' )
        self.assertEqual( foo.Language(), '' )
        self.assertEqual( foo.Rights(), '' )

    def test_initialValues_type_policy( self ):

        from Products.CMFDefault.exceptions import MetadataError

        tool = self._makeOne()
        foo = Foo()

        tSpec = tool.getElementSpec( 'Title' )
        tSpec.addPolicy( 'Foo' )
        tPolicy = tSpec.getPolicy( foo.getPortalTypeName() )
        tPolicy.edit( is_required=True
                    , supply_default=False
                    , default_value=''
                    , enforce_vocabulary=False
                    , allowed_vocabulary=()
                    )

        self.assertRaises( MetadataError, tool.setInitialMetadata, foo )

        foo.setTitle( 'Foo title' )
        tool.setInitialMetadata( foo )

        self.assertEqual( foo.Title(), 'Foo title' )
        self.assertEqual( foo.Description(), '' )
        self.assertEqual( foo.Subject(), () )
        self.assertEqual( foo.Format(), '' )
        self.assertEqual( foo.Language(), '' )
        self.assertEqual( foo.Rights(), '' )


    def test_initialValues_type_policy_independant( self ):

        tool = self._makeOne()
        foo = Foo()

        tSpec = tool.getElementSpec( 'Title' )
        tSpec.addPolicy( 'Foo' )
        tPolicy = tSpec.getPolicy( foo.getPortalTypeName() )
        tPolicy.edit( is_required=True
                    , supply_default=False
                    , default_value=''
                    , enforce_vocabulary=False
                    , allowed_vocabulary=()
                    )

        bar = Bar()

        tool.setInitialMetadata( bar )

        self.assertEqual( bar.Title(), '' )
        self.assertEqual( bar.Description(), '' )
        self.assertEqual( bar.Subject(), () )
        self.assertEqual( bar.Format(), '' )
        self.assertEqual( bar.Language(), '' )
        self.assertEqual( bar.Rights(), '' )

    def test_validation( self ):

        from Products.CMFDefault.exceptions import MetadataError

        tool = self._makeOne()

        foo = Foo()
        tool.setInitialMetadata( foo )
        tool.validateMetadata( foo )

        tSpec = tool.getElementSpec( 'Title' )
        tSpec.addPolicy( 'Foo' )
        tPolicy = tSpec.getPolicy( foo.getPortalTypeName() )
        tPolicy.edit( is_required=True
                    , supply_default=False
                    , default_value=''
                    , enforce_vocabulary=False
                    , allowed_vocabulary=()
                    )

        self.assertRaises( MetadataError, tool.validateMetadata, foo )

        foo.setTitle( 'Foo title' )
        tool.validateMetadata( foo )

    def test_getContentMetadata_converting( self ):

        TITLE = 'A Title'

        tool = self._makeOne()
        foo = Foo()
        foo.title = TITLE

        self.assertEqual( tool.getContentMetadata( foo, 'title' ), TITLE )

        self.failIf( 'title' in foo.__dict__.keys() )

    def test_setContentMetadata_converting( self ):

        TITLE = 'A Title'
        DESCRIPTION = 'This is a description'

        tool = self._makeOne()
        foo = Foo()
        foo.title = TITLE

        tool.setContentMetadata( foo, 'description', DESCRIPTION )

        self.failIf( 'title' in foo.__dict__.keys() )
        self.failIf( 'description' in foo.__dict__.keys() )

        self.assertEqual( tool.getContentMetadata( foo, 'title' ), TITLE )
        self.assertEqual( tool.getContentMetadata( foo, 'description' )
                        , DESCRIPTION )


def test_suite():
    return TestSuite((
        makeSuite(TestMetadataElementPolicy),
        makeSuite(TestElementSpec),
        makeSuite(TestMetadataTool),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
