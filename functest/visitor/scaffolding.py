"""
    Scaffolding methods for CMF_base visitor tests.

    - "setup" methods should return boolean "OK to continue" values.

    - "postcondition" methods should return boolean "test succeeded" values.

    - "teardown" methods don't need to return anything at all.

    Methods can assume that Zope has been imported;  they may not (yet)
    import any Zope-specific packages or modules.

    Each method will be passed a handle to the root Zope object ('app'),
    a dictionary ('test_vars') containing the "defaults" used in
    constructing the functional tests, and the result object (useful
    for storing / retrieving "state" values.)
"""
import string

from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFDefault.NewsItem import NewsItem

#
#   Fake out security (blech!)
#
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
import Acquisition


class FTUser( Acquisition.Implicit ):

    def getId( self ):
        return 'ft_user'
    
    getUserName = getId

    def allowed( self, object, object_roles=None ):
        return 1

    def getRoles( self ):
        return ( 'Manager', )

def fakeSecurity( site ):
    newSecurityManager( None, FTUser().__of__( site.acl_users ) )

#
#   User management.
#
def _ensureMember( site, member_id, password, roles=('Member',) ):
    """
        Ensure that a member with 'member_id' exists.
    """
    user = site.acl_users.getUserById( member_id, None )

    if user is not None:
        return user

    site.acl_users._doAddUser( name=member_id
                             , password=password
                             , roles=roles
                             , domains=()
                             )

    user = site.acl_users.getUserById( member_id, None )
    user._added_by_FT = 1
    site.portal_membership.createMemberarea( member_id )
    getattr( site.Members, member_id )._added_by_FT = 1
    return user

def _scrubMember( site, member_id, force=0 ):
    """
        Blow away 'member_id', IFF created by FT.
    """
    user = site.acl_users.getUserById( member_id, None )
    if not user:
        return
    
    if getattr( user, '_added_by_FT', 0 ) or force:
        site.acl_users._doDelUsers( [ member_id ] )
        _scrubPath( site, 'Members/%s' % member_id )
 
#
#   Set up default content
#
def _ensurePath( site, path ):
    """
        Ensure that 'path' exists within 'site';  return the folder
        at the end of 'path'.
    """
    if not path:
        return site

    if type( path ) is type( '' ):
        path = string.split( path, '/' )

    base = site

    for element in path:

        if element not in base.objectIds():
            folder = PortalFolder( element )
            folder._added_by_FT = 1
            base._setOb( element, folder )
    
        base = base._getOb( element )

    return base

def _scrubPath( site, path ):
    """
        Remove any folders added by FT.
    """
    if not path:
        return

    if type( path ) is type( '' ):
        path = string.split( path, '/' )

    base = site

    for element in path:

        if element not in base.objectIds():
            return
        
        if getattr( element, '_added_by_FT', 0 ):
            base._delOb( element )
            return
    
        base = base._getOb( element )

def _ensureContent( site, id, type_name, path='' ):
    """
        Ensure that a content object exists.
    """
    base = _ensurePath( site, path )

    if id not in base.objectIds():

        fakeSecurity( site )

        try:
            base.invokeFactory( type_name=type_name, id=id )
            item = base._getOb( id )
            item._added_by_FT = 1
            return item
        finally:
            noSecurityManager()

def _ensurePublishedDocument( site, id, path=''
                           , title='', type_name='Document' ):
    """
    """
    document = _ensureContent( site, id, type_name, path )

    if not getattr( document, '_added_by_FT', 0 ):
        return

    fakeSecurity( site )
    try:
        document.edit( text_format='structured-text'
                    , text='This is some sample content'
                    )
        document.portal_workflow.doActionFor( document
                                            , 'publish'
                                            , comment='FT'
                                            )
    finally:
        noSecurityManager()

def _ensureTopic( site, id, path='', field='Type', value='News Item' ):
    """
        Find / create a topic at path/id;  if creating, add an SSC
        for 'field'/'value'.
    """
    base = _ensurePath( site, path )

    if id not in base.objectIds():

        fakeSecurity( site )

        try:
            base.invokeFactory( type_name='Topic', id=id )
            item = base._getOb( id )
            item._added_by_FT = 1
            item.addCriterion( field=field
                             , criterion_type='String Criterion' )
            crit = item.getCriterion( criterion_id=field )
            crit.edit( value=value )
            return item
        finally:
            noSecurityManager()

def _scrubContent( site, id, path='' ):
    """
        Remove content, if created by FT.
    """
    try:
        base = _ensurePath( site, path )
        item = getattr( base, id, None )
        if item and getattr( item, '_added_by_FT', 0 ):
            base._delObject( id )
    except:
        pass

#
#   Ensure that correct user exists
#
def _setup_test_user( app, test_vars ):
    site_path   = test_vars.get( 'site_path', '/' )
    userid      = test_vars.get( 'userid', 'test_user' )
    password    = test_vars.get( 'password', 'xyzzy' )
    site        = app.unrestrictedTraverse( site_path )

    _ensureMember( site, userid, password )

def _teardown_test_user( app, test_vars ):
    site_path   = test_vars.get( 'site_path', '/' )
    userid      = test_vars.get( 'userid', 'test_user' )
    site        = app.unrestrictedTraverse( site_path )

    _scrubMember( site, userid )

#
#   Ensure that 'test_news' (or looked up value) is present, published.
#
def _setup_test_news( app, test_vars ):
    site_path           = test_vars.get( 'site_path', '/' )
    click_through_type  = test_vars.get( 'click_through_type', 'News Item' )
    click_through_id    = test_vars.get( 'click_through_id', 'test_news' )

    site            = app.unrestrictedTraverse( site_path )

    _ensurePublishedDocument( site=site
                           , id=click_through_id
                           , type_name=click_through_type
                           )

def _teardown_test_news( app, test_vars ):
    site_path           = test_vars.get( 'site_path', '/' )
    click_through_id    = test_vars.get( 'click_through_id', 'test_news' )
    site                = app.unrestrictedTraverse( site_path )

    _scrubContent( site, click_through_id )

#
#   Ensure that 'test_news' (or looked up value) is present, published.
#
def _setup_test_topic( app, test_vars ):
    site_path           = test_vars.get( 'site_path', '/' )
    topic_id            = test_vars.get( 'topic_id', 'test_topic' )
    topic_crit_field    = test_vars.get( 'topic_crit_field', 'Type' )
    topic_crit_value    = test_vars.get( 'topic_crit_value', 'News Item' )

    site                = app.unrestrictedTraverse( site_path )

    _ensureTopic( site=site
                , id=topic_id
                , field=topic_crit_field
                , value=topic_crit_value
                )

def _teardown_test_topic( app, test_vars ):
    site_path           = test_vars.get( 'site_path', '/' )
    topic_id            = test_vars.get( 'topic_id', 'test_topic' )
    site                = app.unrestrictedTraverse( site_path )

    _scrubContent( site, topic_id )

#
#   advanced_search.zft
#
def advanced_search_setup( app, test_vars, result ):
    """
        Ensure that we have at least the one expected piece of content.
    """
    _setup_test_news( app, test_vars )
    get_transaction().commit()
    return 1

def advanced_search_teardown( app, test_vars, result ):
    """
        Ensure that we scrub any content we created.
    """
    _teardown_test_news( app, test_vars )
    get_transaction().commit()

#
#   become_member.zft
#
def become_member_setup( app, test_vars, result ):
    """
    """
    site_path   = test_vars.get( 'site_path', '/' )
    userid      = test_vars.get( 'userid', 'test_user' )
    site        = app.unrestrictedTraverse( site_path )

    _scrubMember( site, userid, 1 )
    get_transaction().commit()
    return 1

def become_member_postcondition( app, test_vars, result ):
    """
    """
    site_path   = test_vars.get( 'site_path', '/' )
    userid      = test_vars.get( 'userid', 'test_user' )
    site        = app.unrestrictedTraverse( site_path )

    user = site.acl_users.getUserById( userid )
    folder = getattr( site.Members, userid )

    return ( user.allowed( 'Member' )
         and 'Owner' in user.getRolesInContext( folder )
           )

def become_member_teardown( app, test_vars, result ):
    """
    """
    site_path   = test_vars.get( 'site_path', '/' )
    userid      = test_vars.get( 'userid', 'test_user' )
    site        = app.unrestrictedTraverse( site_path )

    _scrubMember( site, userid )
    get_transaction().commit()

#
#   browse_news.zft
#
def browse_news_setup( app, test_vars, result ):
    """
        Ensure that we have at least the one expected piece of content.
    """
    _setup_test_news( app, test_vars )
    get_transaction().commit()
    return 1

def browse_news_teardown( app, test_vars, result ):
    """
        Ensure that we scrub any content we created.
    """
    _teardown_test_news( app, test_vars )
    get_transaction().commit()

#
#   browse_topic.zft
#
def browse_topic_setup( app, test_vars, result ):
    # Note that we are *not* (yet) guaranteeing that the
    # "click through" page actually shows up on any search
    # results page, merely that we can execute these requests.
    _setup_test_user( app, test_vars )
    _setup_test_news( app, test_vars )
    _setup_test_topic( app, test_vars )
    get_transaction().commit()
    return 1

def browse_topic_teardown( app, test_vars, result ):
    _teardown_test_topic( app, test_vars )
    _teardown_test_news( app, test_vars )
    _teardown_test_user( app, test_vars )
    get_transaction().commit()
 
#
#   log_in.zft
#
def log_in_setup( app, test_vars, result ):
    """
    """
    _setup_test_user( app, test_vars )
    get_transaction().commit()
    return 1

def log_in_teardown( app, test_vars, result ):
    """
    """
    _teardown_test_user( app, test_vars )
    get_transaction().commit()
#
#   provide_feeback.zft
#
def provide_feedback_setup( app, test_vars, result ):
    """
    """
    site_path           = test_vars.get( 'site_path', '/' )
    click_through_type  = test_vars.get( 'click_through_type', 'News Item' )
    site                = app.unrestrictedTraverse( site_path )
    type_info           = getattr( site.portal_types, click_through_type )

    result.setStateValue( 'provide_feedback_discussable '
                        , type_info.allow_discussion )

    type_info.allow_discussion = 1

    _setup_test_news( app, test_vars )
    _setup_test_user( app, test_vars )
    get_transaction().commit()
    return 1

def provide_feedback_postcondition( app, test_vars, result ):
    """
    """
    return 1

def provide_feedback_teardown( app, test_vars, result ):
    """
    """
    site_path           = test_vars.get( 'site_path', '/' )
    click_through_type  = test_vars.get( 'click_through_type', 'News Item' )
    site                = app.unrestrictedTraverse( site_path )
    type_info           = getattr( site.portal_types, click_through_type )

    type_info.allow_discussion = result.getStateValue(
                                          'provide_feedback_discussable ' )

    _teardown_test_user( app, test_vars )
    _teardown_test_news( app, test_vars )
    get_transaction().commit()
#
#   quick_search.zft
#
def quick_search_setup( app, test_vars, result ):
    # Note that we are *not* (yet) guaranteeing that the
    # "click through" page actually shows up on any search
    # results page, merely that we can execute these requests.
    _setup_test_news( app, test_vars )
    _setup_test_user( app, test_vars )
    get_transaction().commit()
    return 1

def quick_search_teardown( app, test_vars, result ):
    _teardown_test_user( app, test_vars )
    _teardown_test_news( app, test_vars )
    get_transaction().commit()
