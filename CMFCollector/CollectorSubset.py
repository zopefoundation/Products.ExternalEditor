from Products.CMFCore.PortalContent import PortalContent
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent

from Acquisition import aq_parent
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from urllib import urlencode

factory_type_information = \
( { 'id'            : 'Collector Subset'
  , 'icon'          : 'collector_icon.gif'
  , 'meta_type'     : 'CMF Collector Issue'
  , 'description'   : ( 'A Collector Subset represents a view on a subset '
                      + 'of the issues in a collector.'
                      )
  , 'product'       : 'CMFCollector'
  , 'factory'       : 'addCollectorSubset'
  , 'immediate_view': 'subset_edit_form'
  , 'actions'       :
    ( { 'id'        : 'view'
      , 'name'          : 'View'
      , 'action'        : 'subset_view'
      , 'permissions'   : ( View, )
      }
    , { 'id'            : 'edit'
      , 'name'          : 'Edit'
      , 'action'        : 'subset_edit_form'
      , 'permissions'   : ( ModifyPortalContent, )
      }
    , { 'id'            : 'metadata'
      , 'name'          : 'Metadata'
      , 'action'        : 'metadata_edit_form'
      , 'permissions'   : ( ModifyPortalContent, )
      }
    )
  }
,
)

PARAMETER_TYPES = ( 'review_state'
                  , 'submitter_id'
                  , 'supporters:list'
                  , 'topics:list'
                  , 'classifications:list'
                  , 'importances:list'
                  )

class CollectorSubset( PortalContent, DefaultDublinCoreImpl ):
    """
        Represent a "persistent" query against a collector's issues.
    """
    meta_type = 'Collector Subset'

    _parameters = None

    security = ClassSecurityInfo()

    security.declareObjectProtected( View )

    def __init__( self, id ):
        self._setId( id )

    index_html = None   # Self-publishing

    security.declarePrivate( '_buildQueryString' )
    def _buildQueryString( self ):

        parameters = {}

        for k, v in self.listParameters():
            if v not in ( None, '' ):
                parameters[ k ] = v

        return urlencode( parameters )

    security.declarePrivate( '_getParameterDict' )
    def _getParameterDict( self ):

        return self._parameters or {}

    security.declareProtected( View, 'listParameterTypes' )
    def listParameterTypes( self ):
        """
            Return a list of the allowed query parameter types for defining
            the subset.
        """
        return PARAMETER_TYPES

    def __call__( self, *args, **kw ):
        """
            Redirect to the parent collector's main view, but with
            query parameters set.
        """
        self.REQUEST['RESPONSE'].redirect( self.getCollectorURL() )

    security.declareProtected( View, 'getCollectorURL' )
    def getCollectorURL( self ):
        """
            Return the URL into our collector, with qualifying query string
            matching our parameters.
        """
        parent = aq_parent( self )
        return ( '%s/collector_contents?%s'
               % ( parent.absolute_url(), self._buildQueryString() )
               )

    security.declareProtected( View, 'getParameterValue' )
    def getParameterValue( self, key ):
        """
            Return the value for the given key.
        """
        if key not in PARAMETER_TYPES:
            raise ValueError, 'Invalid key: %s' % key

        return self._getParameterDict().get( key, '' )

    security.declareProtected( View, 'listParameters' )
    def listParameters( self ):
        """
            Return a list of the query parameters which define this subset,
            as a sequence of (key,value) tuples.
        """
        return self._getParameterDict().items()

    security.declareProtected( ModifyPortalContent, 'setParameter' )
    def setParameter( self, key, value ):
        """
            Add / update a single parameter used to define this subset.

            o 'key' must be in PARAMETER_TYPES

            o 'value' should be a string
        """
        if key not in PARAMETER_TYPES:
            raise ValueError, 'Invalid key: %s' % key

        parms = self._getParameterDict()
        parms[ key ] = value
        self._parameters = parms

    security.declareProtected( ModifyPortalContent, 'clearParameters' )
    def clearParameters( self ):
        """
            Erase all parameters.
        """
        try:
            del self._parameters
        except KeyError:
            pass


def addCollectorSubset( self, id, REQUEST=None ):
    """
        Add one.
    """
    self._setObject( id, CollectorSubset( id ) )

    if REQUEST is not None:
        REQUEST[ 'RESPONSE' ].redirect( '%s/manage_main?Subset+added.' )
