"""
    Scaffolding methods for CMF_base tests.

    - "setup" methods should return boolean "OK to continue" values.

    - "postcondition" methods should return boolean "test succeeded" values.

    - "teardown" methods don't need to return anything at all.

    Methods can assume that Zope has been imported;  they may not (yet)
    import any Zope-specific packages or modules.

    Each method will be passed a handle to the root Zope object ('app')
    and a dictionary ('test_vars') containing the "defaults" used in
    constructing the functional tests.
"""

from Products.CMFCore.PortalFolder import PortalFolder

def submit_news_setup( app, test_vars, result ):
    """
        Ensure that member exists, with given password, and that she
        has an member folder without an object called "testnews".
    """
    site_path   = test_vars.get( 'site_path', '/' )
    userid      = test_vars.get( 'userid', 'user' )
    password    = test_vars.get( 'password', 'password' )
    newsitem_id = test_vars.get( 'newsitem_id', 'testnews' )

    cmf_site    = app.unrestrictedTraverse( site_path )
    acl_users   = cmf_site.acl_users

    user        = acl_users.getUserById( userid, None )
    if user is None:
        acl_users._doAddUser( userid, password, ( 'Member', ), () )
        user    = acl_users.getUserById( userid, None )
    user        = user.__of__( acl_users )
    
    try:
        folder      = cmf_site.unrestrictedTraverse( 'Members/%s' % userid )
    except:
        cmf_site.portal_membership.createMemberarea( userid )
        folder      = cmf_site.unrestrictedTraverse( 'Members/%s' % userid )

    if newsitem_id in folder.objectIds():
        folder.manage_delObjects( ids=[newsitem_id] )
    
    get_transaction().commit()

    return 1

def submit_news_postcondition( app, test_vars, result ):
    """
    """
    app._p_jar.sync() # must get caught up!

    site_path   = test_vars.get( 'site_path', '/' )
    userid      = test_vars.get( 'userid', 'user' )
    newsitem_id = test_vars.get( 'newsitem_id', 'testnews' )

    cmf_site    = app.unrestrictedTraverse( site_path )
    wf_tool     = cmf_site.portal_workflow

    newsitem    = cmf_site.unrestrictedTraverse( 'Members/%s/%s'
                                % ( userid, newsitem_id ) )
    assert wf_tool.getInfoFor( newsitem, 'review_state' ) == 'pending'
    
    get_transaction().commit()

    return 1

def submit_news_teardown( app, test_vars, result ):
    """
    """
    site_path   = test_vars.get( 'site_path', '/' )
    userid      = test_vars.get( 'userid', 'user' )
    newsitem_id = test_vars.get( 'newsitem_id', 'testnews' )

    cmf_site    = app.unrestrictedTraverse( site_path )
    folder      = cmf_site.unrestrictedTraverse( 'Members/%s' % userid )
    if newsitem_id in folder.objectIds():
        folder.manage_delObjects( ids=[newsitem_id] )
    
    get_transaction().commit()
