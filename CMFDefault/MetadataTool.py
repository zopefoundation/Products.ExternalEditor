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
""" CMFDefault portal_metadata tool.

$Id$
"""

from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from Globals import DTMLFile
from Globals import InitializeClass
from Globals import PersistentMapping
from OFS.PropertySheets import PropertySheet
from OFS.SimpleItem import SimpleItem

from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.interfaces.portal_metadata \
        import portal_metadata as IMetadataTool
from Products.CMFCore.utils import UniqueObject

from exceptions import MetadataError
from permissions import ManagePortal
from permissions import ModifyPortalContent
from permissions import View
from utils import _dtmldir


class MetadataElementPolicy( SimpleItem ):

    """ Represent a type-specific policy about a particular DCMI element.
    """

    security = ClassSecurityInfo()
    #
    #   Default values.
    #
    is_required         = 0
    supply_default      = 0
    default_value       = ''
    enforce_vocabulary  = 0
    allowed_vocabulary  = ()

    def __init__( self, is_multi_valued=0 ):
        self.is_multi_valued    = not not is_multi_valued

    #
    #   Mutator.
    #
    security.declareProtected(ManagePortal , 'edit')
    def edit( self
            , is_required
            , supply_default
            , default_value
            , enforce_vocabulary
            , allowed_vocabulary
            ):
        self.is_required        = not not is_required
        self.supply_default     = not not supply_default
        self.default_value      = default_value
        self.enforce_vocabulary = not not enforce_vocabulary
        self.allowed_vocabulary = tuple( allowed_vocabulary )

    #
    #   Query interface
    #
    security.declareProtected(View , 'isMultiValued')
    def isMultiValued( self ):

        """ Can this element hold multiple values?
        """
        return self.is_multi_valued

    security.declareProtected(View , 'isRequired')
    def isRequired( self ):

        """ Must this element be supplied?
        """
        return self.is_required

    security.declareProtected(View , 'supplyDefault')
    def supplyDefault( self ):

        """ Should the tool supply a default?
        """
        return self.supply_default

    security.declareProtected(View , 'defaultValue')
    def defaultValue( self ):

        """ If so, what is the default?
        """
        return self.default_value

    security.declareProtected(View , 'enforceVocabulary')
    def enforceVocabulary( self ):

        """ Should the vocabulary for this element be restricted?
        """
        return self.enforce_vocabulary

    security.declareProtected(View , 'allowedVocabulary')
    def allowedVocabulary( self ):

        """ If so, what are the allowed values?
        """
        return self.allowed_vocabulary

InitializeClass( MetadataElementPolicy )


DEFAULT_ELEMENT_SPECS = ( ( 'Title', 0 )
                        , ( 'Description', 0 )
                        , ( 'Subject', 1 )
                        , ( 'Format', 0 )
                        , ( 'Language', 0 )
                        , ( 'Rights', 0 )
                        )


class ElementSpec( SimpleItem ):

    """ Represent all the tool knows about a single metadata element.
    """
    security = ClassSecurityInfo()

    #
    #   Default values.
    #
    is_multi_valued = 0

    def __init__( self, is_multi_valued ):
        self.is_multi_valued  = is_multi_valued
        self.policies         = PersistentMapping()
        self.policies[ None ] = self._makePolicy()  # set default policy

    security.declarePrivate( '_makePolicy' )
    def _makePolicy( self ):
        return MetadataElementPolicy( self.is_multi_valued )

    security.declareProtected(View , 'isMultiValued')
    def isMultiValued( self ):

        """ Is this element multi-valued?
        """
        return self.is_multi_valued

    security.declareProtected(View , 'getPolicy')
    def getPolicy( self, typ=None ):

        """ Find the policy this element for objects of a given type.

        o Return a default, if none found.
        """
        try:
            return self.policies[ typ ].__of__(self)
        except KeyError:
            return self.policies[ None ]

    security.declareProtected(View , 'listPolicies')
    def listPolicies( self ):

        """ Return a list of all policies for this element.
        """
        res = []
        for k, v in self.policies.items():
            res.append((k, v.__of__(self)))
        return res

    security.declareProtected(ManagePortal , 'addPolicy')
    def addPolicy( self, typ ):

        """ Add a policy to this element for objects of a given type.
        """
        if typ is None:
            raise MetadataError, "Can't replace default policy."

        if self.policies.has_key( typ ):
            raise MetadataError, "Existing policy for content type:" + typ

        self.policies[ typ ] = self._makePolicy()

    security.declareProtected(ManagePortal, 'removePolicy')
    def removePolicy( self, typ ):

        """ Remove the policy from this element for objects of a given type.
        
        o Note that this method does *not* remove the default!
        """
        if typ is None:
            raise MetadataError, "Can't remove default policy."
        del self.policies[ typ ]

InitializeClass( ElementSpec )


class MetadataTool( UniqueObject, SimpleItem, ActionProviderBase ):

    """ Hold, enable, and enforce site-wide metadata policies.
    """
    __implements__ = (IMetadataTool, ActionProviderBase.__implements__)

    id = 'portal_metadata'
    meta_type = 'Default Metadata Tool'
    _actions = ()

    #
    #   Default values.
    #
    publisher           = ''
    element_specs       = None
    #initial_values_hook = None
    #validation_hook     = None

    security = ClassSecurityInfo()

    def __init__( self
                , publisher=None
               #, initial_values_hook=None
               #, validation_hook=None
                , element_specs=DEFAULT_ELEMENT_SPECS
                ):

        self.editProperties( publisher
                          #, initial_values_hook
                          #, validation_hook
                           )

        self.element_specs = PersistentMapping()

        for name, is_multi_valued in element_specs:
            self.element_specs[ name ] = ElementSpec( is_multi_valued )

    #
    #   ZMI methods
    #
    manage_options = ( ActionProviderBase.manage_options +
                     ( { 'label'      : 'Overview'
                         , 'action'     : 'manage_overview'
                         }
                       , { 'label'      : 'Properties'
                         , 'action'     : 'propertiesForm'
                         }
                       , { 'label'      : 'Elements'
                         , 'action'     : 'elementPoliciesForm'
                         }
            # TODO     , { 'label'      : 'Types'
            #            , 'action'     : 'typesForm'
            #            }
                       )
                     + SimpleItem.manage_options
                     )

    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = DTMLFile( 'explainMetadataTool', _dtmldir )

    security.declareProtected(ManagePortal, 'propertiesForm')
    propertiesForm = DTMLFile( 'metadataProperties', _dtmldir )

    security.declareProtected(ManagePortal, 'editProperties')
    def editProperties( self
                      , publisher=None
               # TODO , initial_values_hook=None
               # TODO , validation_hook=None
                      , REQUEST=None
                      ):

        """ Form handler for "tool-wide" properties .
        """
        if publisher is not None:
            self.publisher = publisher

        # TODO self.initial_values_hook = initial_values_hook
        # TODO self.validation_hook = validation_hook

        if REQUEST is not None:
            REQUEST[ 'RESPONSE' ].redirect( self.absolute_url()
                                        + '/propertiesForm'
                                        + '?manage_tabs_message=Tool+updated.'
                                        )

    security.declareProtected(ManagePortal, 'elementPoliciesForm')
    elementPoliciesForm = DTMLFile( 'metadataElementPolicies', _dtmldir )

    security.declareProtected(ManagePortal, 'addElementPolicy')
    def addElementPolicy( self
                        , element
                        , content_type
                        , is_required
                        , supply_default
                        , default_value
                        , enforce_vocabulary
                        , allowed_vocabulary
                        , REQUEST=None
                        ):

        """ Add a type-specific policy for one of our elements.
        """
        if content_type == '<default>':
            content_type = None

        spec = self.getElementSpec( element )
        spec.addPolicy( content_type )
        policy = spec.getPolicy( content_type )
        policy.edit( is_required
                   , supply_default
                   , default_value
                   , enforce_vocabulary
                   , allowed_vocabulary
                   )
        if REQUEST is not None:
            REQUEST[ 'RESPONSE' ].redirect( self.absolute_url()
               + '/elementPoliciesForm'
               + '?element=' + element
               + '&manage_tabs_message=Policy+added.'
               )

    security.declareProtected(ManagePortal, 'removeElementPolicy')
    def removeElementPolicy( self
                           , element
                           , content_type
                           , REQUEST=None
                           ):

        """ Remvoe a type-specific policy for one of our elements.
        """
        if content_type == '<default>':
            content_type = None

        spec = self.getElementSpec( element )
        spec.removePolicy( content_type )
        if REQUEST is not None:
            REQUEST[ 'RESPONSE' ].redirect( self.absolute_url()
               + '/elementPoliciesForm'
               + '?element=' + element
               + '&manage_tabs_message=Policy+removed.'
               )

    security.declareProtected(ManagePortal, 'updateElementPolicy')
    def updateElementPolicy( self
                           , element
                           , content_type
                           , is_required
                           , supply_default
                           , default_value
                           , enforce_vocabulary
                           , allowed_vocabulary
                           , REQUEST=None
                           ):

        """ Update a policy for one of our elements
        
        o Note that 'content_type' will be passed as '<default>' when we
          are editing the default.
        """
        if content_type == '<default>':
            content_type = None

        spec = self.getElementSpec( element )
        policy = spec.getPolicy( content_type )
        policy.edit( is_required
                   , supply_default
                   , default_value
                   , enforce_vocabulary
                   , allowed_vocabulary
                   )
        if REQUEST is not None:
            REQUEST[ 'RESPONSE' ].redirect( self.absolute_url()
               + '/elementPoliciesForm'
               + '?element=' + element
               + '&manage_tabs_message=Policy+updated.'
               )


    #
    #   Element spec manipulation.
    #
    security.declareProtected(ManagePortal, 'listElementSpecs')
    def listElementSpecs( self ):

        """ Return a list of ElementSpecs describing our elements.
        """
        res = []
        for k, v in self.element_specs.items():
            res.append((k, v.__of__(self)))
        return res

    security.declareProtected(ManagePortal, 'getElementSpec')
    def getElementSpec( self, element ):

        """ Return an ElementSpec describing what we know about 'element'.
        """
        return self.element_specs[ element ].__of__( self )

    security.declareProtected(ManagePortal, 'addElementSpec')
    def addElementSpec( self, element, is_multi_valued, REQUEST=None ):

        """ Add 'element' to our list of managed elements.
        """
        # Don't replace.
        if self.element_specs.has_key( element ):
           return

        self.element_specs[ element ] = ElementSpec( is_multi_valued )

        if REQUEST is not None:
            REQUEST[ 'RESPONSE' ].redirect( self.absolute_url()
               + '/propertiesForm'
               + '?manage_tabs_message=Element+' + element + '+added.'
               )

    security.declareProtected(ManagePortal, 'removeElementSpec')
    def removeElementSpec( self, element, REQUEST=None ):

        """ Remove 'element' from our list of managed elements.
        """
        del self.element_specs[ element ]

        if REQUEST is not None:
            REQUEST[ 'RESPONSE' ].redirect( self.absolute_url()
               + '/propertiesForm'
               + '?manage_tabs_message=Element+' + element + '+removed.'
               )

    security.declareProtected(ManagePortal, 'listPolicies')
    def listPolicies( self, typ=None ):

        """ Show all policies for a given content type.
        
        o If 'typ' is none, return the set of default policies.
        """
        result = []

        for element, spec in self.listElementSpecs():
            result.append( ( element, spec.getPolicy( typ ) ) )

        return result

    #
    #   'portal_metadata' interface
    #
    security.declarePrivate( 'getFullName' )
    def getFullName( self, userid ):

        """ See 'portal_metadata' interface.
        """
        return userid   # TODO: do lookup here

    security.declarePublic( 'getPublisher' )
    def getPublisher( self ):

        """ See 'portal_metadata' interface.
        """
        return self.publisher

    security.declarePublic( 'listAllowedVocabulary' )
    def listAllowedVocabulary( self, element, content=None, content_type=None ):

        """ See 'portal_metadata' interface.
        """
        spec = self.getElementSpec( element )
        if content_type is None and content:
            content_type = content.getPortalTypeName()
        return spec.getPolicy( content_type ).allowedVocabulary()

    security.declarePublic( 'listAllowedSubjects' )
    def listAllowedSubjects( self, content=None, content_type=None ):

        """ See 'portal_metadata' interface.
        """
        return self.listAllowedVocabulary( 'Subject', content, content_type )

    security.declarePublic( 'listAllowedFormats' )
    def listAllowedFormats( self, content=None, content_type=None ):

        """ See 'portal_metadata' interface.
        """
        return self.listAllowedVocabulary( 'Format', content, content_type )

    security.declarePublic( 'listAllowedLanguages' )
    def listAllowedLanguages( self, content=None, content_type=None ):

        """ See 'portal_metadata' interface.
        """
        return self.listAllowedVocabulary( 'Language', content, content_type )

    security.declarePublic( 'listAllowedRights' )
    def listAllowedRights( self, content=None, content_type=None ):

        """ See 'portal_metadata' interface.
        """
        return self.listAllowedVocabulary( 'Rights', content, content_type )

    security.declareProtected(ModifyPortalContent, 'setInitialMetadata')
    def setInitialMetadata( self, content ):

        """ See 'portal_metadata' interface.
        """
        for element, policy in self.listPolicies(content.getPortalTypeName()):

            if not getattr( content, element )():

                if policy.supplyDefault():
                    setter = getattr( content, 'set%s' % element )
                    setter( policy.defaultValue() )
                elif policy.isRequired():
                    raise MetadataError, \
                          'Metadata element %s is required.' % element

        # TODO:  Call initial_values_hook, if present


    security.declareProtected(View, 'validateMetadata')
    def validateMetadata( self, content ):

        """ See 'portal_metadata' interface.
        """
        for element, policy in self.listPolicies(content.getPortalTypeName()):

            value = getattr( content, element )()
            if not value and policy.isRequired():
                raise MetadataError, \
                        'Metadata element %s is required.' % element

            if policy.enforceVocabulary():
                values = policy.isMultiValued() and value or [ value ]
                for value in values:
                    if not value in policy.allowedVocabulary():
                        raise MetadataError, \
                        'Value %s is not in allowed vocabulary for' \
                        'metadata element %s.' % ( value, element )

        # TODO:  Call validation_hook, if present

    security.declarePrivate( 'getContentMetadata' )
    def getContentMetadata( self, content, element ):

        """ See 'portal_metadata' interface.
        """
        dcmi = self._checkAndConvert( content )
        return dcmi.getProperty( element )

    security.declarePrivate( 'setContentMetadata' )
    def setContentMetadata( self, content, element, value ):

        """ See 'portal_metadata' interface.
        """
        dcmi = self._checkAndConvert( content )
        dcmi._updateProperty( element, value )

    #
    #   Helper methods
    #
    def _getDCMISheet( self, content ):

        """ Return the DCMI propertysheet for content.

        o Return 'None' if the sheet does not exist.
        """
        return content.propertysheets.get( DCMI_NAMESPACE )

    def _checkAndConvert( self, content ):

        """ Ensure that content has the DCMI propertysheet.

        o Copy any legacy values from DCMI attributes to it, and remove
          them.
        """
        sheets = content.propertysheets

        sheet = sheets.get( DCMI_NAMESPACE )
        if sheet is not None:
            return sheet

        md = { 'xmlns' : DCMI_NAMESPACE }
        sheet = DCMISchema( 'dc', md )
        marker = object()

        for prop_name, attr in _DCMI_CONVERSIONS:

            old = getattr( content, attr, marker )

            if old is not marker:
                setattr( sheet, prop_name, old )
                try:
                    delattr( content, attr )
                except ( AttributeError, KeyError ):
                    pass

        sheets.addPropertySheet( sheet )
        return sheet.__of__( sheets )

InitializeClass( MetadataTool )


DCMI_NAMESPACE = 'http://purl.org/dc/elements/1.1/'

class DCMISchema( PropertySheet ):

    """ Fixed schema for DublinCore metadata.

    o It gets its schema from a static map but has control over its
      value storage.
    """
    def _propertyMap(self):
        # Return a tuple of mappings, giving meta-data for properties.
        result = []

        for info in _DCMI_PROPERTY_MAP:
            info = info.copy()
            result.append( info )

        return tuple( result )

    def propertyMap(self):
        return self._propertyMap()

    def property_extensible_schema__(self):
        return False

InitializeClass( DCMISchema )

_DCMI_PROPERTY_MAP = \
( { 'id' : 'title', 'type' : 'string', 'mode' : 'w' }
, { 'id' : 'description', 'type' : 'string', 'mode' : 'w' }
, { 'id' : 'subject', 'type' : 'lines', 'mode' : 'w' }
, { 'id' : 'contributors', 'type' : 'lines', 'mode' : 'w' }
, { 'id' : 'created', 'type' : 'date', 'mode' : 'w' }
, { 'id' : 'modified', 'type' : 'date', 'mode' : 'w' }
, { 'id' : 'efffective', 'type' : 'date', 'mode' : 'w' }
, { 'id' : 'expires', 'type' : 'date', 'mode' : 'w' }
, { 'id' : 'format', 'type' : 'string', 'mode' : 'w' }
, { 'id' : 'language', 'type' : 'string', 'mode' : 'w' }
, { 'id' : 'rights', 'type' : 'string', 'mode' : 'w' }
)

# Map properties onto attributes
_DCMI_CONVERSIONS = \
( ( 'title', 'title' )
, ( 'description', 'description' )
, ( 'subject', 'subject' )
, ( 'contributors', 'contributors' )
, ( 'created', 'creation_data' )
, ( 'modified', 'modification_date' )
, ( 'efffective', 'effective_date' )
, ( 'expires', 'expiration_date' )
, ( 'format', 'format' )
, ( 'language', 'language' )
, ( 'rights', 'rights' )
)
