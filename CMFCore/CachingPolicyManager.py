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

"""Caching tool implementation.

$Id$
"""
from App.Common import rfc1123_date

from AccessControl import ClassSecurityInfo

from DateTime.DateTime import DateTime

from Globals import InitializeClass
from Globals import DTMLFile
from Globals import PersistentMapping

from OFS.SimpleItem import SimpleItem

from Products.PageTemplates.Expressions import getEngine
from Products.PageTemplates.Expressions import SecureModuleImporter

from Products.CMFCore.interfaces.CachingPolicyManager \
        import CachingPolicyManager as ICachingPolicyManager

from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.CMFCorePermissions import View
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore.Expression import Expression

from Products.CMFCore.utils import _getAuthenticatedUser
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import _dtmldir
import time


def createCPContext( content, view_method, keywords, time=None ):
    """
        Construct an expression context for TALES expressions,
        for use by CachingPolicy objects.
    """
    pm = getToolByName( content, 'portal_membership', None )
    if not pm or pm.isAnonymousUser():
        member = None
    else:
        member = pm.getAuthenticatedMember()

    if time is None:
        time = DateTime()

    data = { 'content'  : content
           , 'view'     : view_method
           , 'keywords' : keywords
           , 'request'  : getattr( content, 'REQUEST', {} )
           , 'member'   : member
           , 'modules'  : SecureModuleImporter
           , 'nothing'  : None
           , 'time'     : time
           }

    return getEngine().getContext( data )

class CachingPolicy:
    """
        Represent a single class of cachable objects:

          - class membership is defined by 'predicate', a TALES expression
            with access to the following top-level names:

            'content' -- the content object itself

            'view' -- the name of the view method
           
            'keywords' -- keywords passed to the request
           
            'request' -- the REQUEST object itself
           
            'member' -- the authenticated member, or None if anonymous
           
            'modules' -- usual TALES access-with-import
           
            'nothing' -- None

          - The "Last-modified" HTTP response header will be set using
            'mtime_func', which is another TALES expression evaluated
            against the same namespace.  If not specified explicitly,
            uses 'content/modified'.

          - The "Expires" HTTP response header and the "max-age" token of
            the "Cache-control" header will be set using 'max_age_secs',
            if passed;  it should be an integer value in seconds.

          - Other tokens will be added to the "Cache-control" HTTP response
            header as follows:

             'no_cache=1' argument => "no-cache" token

             'no_store=1' argument => "no-store" token

             'must_revalidate=1' argument => "must-revalidate" token
    """

    def __init__( self
                , policy_id
                , predicate=''
                , mtime_func=''
                , max_age_secs=None
                , no_cache=0
                , no_store=0
                , must_revalidate=0
                ):

        if not predicate:
            predicate = 'python:1'

        if not mtime_func:
            mtime_func = 'content/modified'

        if max_age_secs is not None:
            max_age_secs = int( max_age_secs )

        self._policy_id = policy_id
        self._predicate = Expression( text=predicate )
        self._mtime_func = Expression( text=mtime_func )
        self._max_age_secs = max_age_secs
        self._no_cache = int( no_cache )
        self._no_store = int( no_store )
        self._must_revalidate = int( must_revalidate )

    def getPolicyId( self ):
        """
        """
        return self._policy_id

    def getPredicate( self ):
        """
        """
        return self._predicate.text

    def getMTimeFunc( self ):
        """
        """
        return self._mtime_func.text

    def getMaxAgeSecs( self ):
        """
        """
        return self._max_age_secs

    def getNoCache( self ):
        """
        """
        return self._no_cache

    def getNoStore( self ):
        """
        """
        return self._no_store

    def getMustRevalidate( self ):
        """
        """
        return self._must_revalidate

    def getHeaders( self, expr_context ):
        """
            Does this request match our predicate?  If so, return a
            sequence of caching headers as ( key, value ) tuples.
            Otherwise, return an empty sequence.
        """
        headers = []

        if self._predicate( expr_context ):

            mtime = self._mtime_func( expr_context )

            if type( mtime ) is type( '' ):
                mtime = DateTime( mtime )

            if mtime is not None:
                mtime_flt = mtime.timeTime()
                mtime_str = rfc1123_date(mtime_flt)
                headers.append( ( 'Last-modified', mtime_str ) )

            control = []

            if self._max_age_secs is not None:
                now = expr_context.vars[ 'time' ]
                exp_time_str = rfc1123_date(now.timeTime() + self._max_age_secs)
                headers.append( ( 'Expires', exp_time_str ) )
                control.append( 'max-age=%d' % self._max_age_secs )

            if self._no_cache:
                control.append( 'no-cache' )

            if self._no_store:
                control.append( 'no-store' )

            if self._must_revalidate:
                control.append( 'must-revalidate' )

            if control:
                headers.append( ( 'Cache-control', ', '.join( control ) ) )

        return headers


class CachingPolicyManager( SimpleItem ):
    """
        Manage the set of CachingPolicy objects for the site;  dispatch
        to them from skin methods.
    """

    __implements__ = ICachingPolicyManager

    id = 'caching_policy_manager'
    meta_type = 'CMF Caching Policy Manager'

    security = ClassSecurityInfo()

    def __init__( self ):
        self._policy_ids = ()
        self._policies = PersistentMapping()

    #
    #   ZMI
    #
    manage_options = ( ( { 'label' : 'Policies'
                         , 'action' : 'manage_cachingPolicies'
                         }
                       ,
                       )
                     + SimpleItem.manage_options
                     )

    security.declareProtected( ManagePortal, 'manage_cachingPolicies' )
    manage_cachingPolicies = DTMLFile( 'cachingPolicies', _dtmldir )

    security.declarePublic( 'listPolicies' )
    def listPolicies( self ):
        """
            Return a sequence of tuples,
            '( policy_id, ( policy, typeObjectName ) )'
            for all policies in the registry 
        """
        result = []
        for policy_id in self._policy_ids:
            result.append( ( policy_id, self._policies[ policy_id ] ) )
        return tuple( result )

    security.declareProtected( ManagePortal, 'addPolicy' )
    def addPolicy( self
                 , policy_id
                 , predicate        # TALES expr (def. 'python:1')
                 , mtime_func       # TALES expr (def. 'content/modified')
                 , max_age_secs     # integer, seconds (def. 0)
                 , no_cache         # boolean (def. 0)
                 , no_store         # boolean (def. 0)
                 , must_revalidate  # boolean (def. 0)
                 , REQUEST
                 ):
        """
            Add a caching policy.
        """
        self._addPolicy( policy_id
                       , predicate
                       , mtime_func
                       , max_age_secs
                       , no_cache
                       , no_store
                       , must_revalidate
                       )
        REQUEST[ 'RESPONSE' ].redirect( self.absolute_url()
                              + '/manage_cachingPolicies'
                              + '?manage_tabs_message=Policy+added.'
                              )

    security.declareProtected( ManagePortal, 'updatePolicy' )
    def updatePolicy( self
                    , policy_id
                    , predicate         # TALES expr (def. 'python:1')
                    , mtime_func        # TALES expr (def. 'content/modified')
                    , max_age_secs      # integer, seconds
                    , no_cache          # boolean (def. 0)
                    , no_store          # boolean (def. 0)
                    , must_revalidate   # boolean (def. 0)
                    , REQUEST ):
        """
            Update a caching policy.
        """
        self._updatePolicy( policy_id
                          , predicate
                          , mtime_func
                          , max_age_secs
                          , no_cache
                          , no_store
                          , must_revalidate
                          )
        REQUEST[ 'RESPONSE' ].redirect( self.absolute_url()
                              + '/manage_cachingPolicies'
                              + '?manage_tabs_message=Policy+updated.'
                              )

    security.declareProtected( ManagePortal, 'movePolicyUp' )
    def movePolicyUp( self, policy_id, REQUEST ):
        """
            Move a caching policy up in the list.
        """
        policy_ids = list( self._policy_ids )
        ndx = policy_ids.index( policy_id )
        if ndx == 0:
            msg = "Policy+already+first."
        else:
            self._reorderPolicy( predicate_id, ndx - 1 )
            msg = "Policy+moved."
        REQUEST[ 'RESPONSE' ].redirect( self.absolute_url()
                              + '/manage_cachingPolicies'
                              + '?manage_tabs_message=%s' % msg
                              )

    security.declareProtected( ManagePortal, 'movePolicyDown' )
    def movePolicyDown( self, policy_id, REQUEST ):
        """
            Move a caching policy down in the list.
        """
        policy_ids = list( self._policy_ids )
        ndx = policy_ids.index( policy_id )
        if ndx == len( policy_ids ) - 1:
            msg = "Policy+already+last."
        else:
            self._reorderPolicy( policy_id, ndx + 1 )
            msg = "Policy+moved."
        REQUEST[ 'RESPONSE' ].redirect( self.absolute_url()
                              + '/manage_cachingPolicies'
                              + '?manage_tabs_message=%s' % msg
                              )

    security.declareProtected( ManagePortal, 'removePolicy' )
    def removePolicy( self, policy_id, REQUEST ):
        """
            Remove a caching policy.
        """
        self._removePolicy( policy_id )
        REQUEST[ 'RESPONSE' ].redirect( self.absolute_url()
                              + '/manage_cachingPolicies'
                              + '?manage_tabs_message=Policy+removed.'
                              )

    #
    #   Policy manipulation methods.
    #
    security.declarePrivate( '_addPolicy' )
    def _addPolicy( self
                  , policy_id
                  , predicate
                  , mtime_func
                  , max_age_secs
                  , no_cache
                  , no_store
                  , must_revalidate
                  ):
        """
            Add a policy to our registry.
        """
        policy_id = str( policy_id ).strip()

        if not policy_id:
            raise ValueError, "Policy ID is required!"

        if policy_id in self._policy_ids:
            raise KeyError, "Policy %s already exists!" % policy_id

        self._policies[ policy_id ] = CachingPolicy( policy_id
                                                   , predicate
                                                   , mtime_func
                                                   , max_age_secs
                                                   , no_cache
                                                   , no_store
                                                   , must_revalidate
                                                   )
        idlist = list( self._policy_ids )
        idlist.append( policy_id )
        self._policy_ids = tuple( idlist )

    security.declarePrivate( '_updatePolicy' )
    def _updatePolicy( self
                     , policy_id
                     , predicate
                     , mtime_func
                     , max_age_secs
                     , no_cache
                     , no_store
                     , must_revalidate
                     ):
        """
            Update a policy in our registry.
        """
        if policy_id not in self._policy_ids:
            raise KeyError, "Policy %s does not exist!" % policy_id

        self._policies[ policy_id ] = CachingPolicy( policy_id
                                                   , predicate
                                                   , mtime_func
                                                   , max_age_secs
                                                   , no_cache
                                                   , no_store
                                                   , must_revalidate
                                                   )

    security.declarePrivate( '_reorderPolicy' )
    def _reorderPolicy( self, policy_id, newIndex ):
        """
            Reorder a policy in our registry.
        """
        if policy_id not in self._policy_ids:
            raise KeyError, "Policy %s does not exist!" % policy_id

        idlist = list( self._policy_ids )
        ndx = idlist.index( policy_id )
        pred = idlist[ ndx ]
        idlist = idlist[ :ndx ] + idlist[ ndx+1: ]
        idlist.insert( newIndex, pred )
        self._policy_ids = tuple( idlist )

    security.declarePrivate( '_removePolicy' )
    def _removePolicy( self, policy_id ):
        """
            Remove a policy from our registry.
        """
        if policy_id not in self._policy_ids:
            raise KeyError, "Policy %s does not exist!" % policy_id

        del self._policies[ policy_id ]
        idlist = list( self._policy_ids )
        ndx = idlist.index( policy_id )
        idlist = idlist[ :ndx ] + idlist[ ndx+1: ]
        self._policy_ids = tuple( idlist )


    #
    #   'portal_caching' interface methods
    #
    security.declareProtected( View, 'getHTTPCachingHeaders' )
    def getHTTPCachingHeaders( self, content, view_method, keywords ):
        """
            Return a list of HTTP caching headers based on 'content',
            'view_method', and 'keywords'.
        """
        context = createCPContext( content, view_method, keywords )
        for policy_id, policy in self.listPolicies():

            headers = policy.getHeaders( context )

            if headers:

                return headers

        return ()


InitializeClass( CachingPolicyManager )

def manage_addCachingPolicyManager( self, REQUEST=None ):
    """
        Add a CPM to self.
    """
    id = CachingPolicyManager.id
    mgr = CachingPolicyManager()
    self._setObject( id, mgr )

    if REQUEST is not None:
        REQUEST[ 'RESPONSE' ].redirect( self.absolute_url()
                      + '/manage_main'
                      + '?manage_tabs_message=Caching+Policy+Manager+added.'
                      )
