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
class ReviewableContent:
    """
    Interface for Portal reviewing/publishing.
    
    Reviewing/publishing is the process of manipulating the
    'View' permission of an object. Assigning different roles
    to the 'View' permission makes the object visible to different
    groups of people.

    This interface seems quite stable.  A couple more hooks may be added.
    
    PortalContent implements this interface.
    """
    
    def publish(self, REQUEST):
        """
        Returns the reviewing management interface.
        
        Return: HTML page
        Permission: 'View management screens'
        """

    def setReviewState(self, review_state, comments, effective_date, REQUEST):
        """
        Handle a web request to change the review state.

        'review_state' is the desired state.  This method needs to verify that
        the authenticated member is allowed to change to this state, and that
        the change makes sense.

        'comments' are the user-supplied comments to be associated with this
        action in the review history.

        'effective_date' is a string representation of a date, which should be
        passwd to set_effective_date if it differs from the presently set
        effective_date.

        Return: HTML page
        Permission: None bound, checks for 'Request review', 'Review item'.
        """



    # Effective date methods
    # ---------------------

    def set_effective_date(self, effective_date, REQUEST):
        """
        Set the effective_date property
        
        This is when this resource becomes available to be
        published.

        TODO: Shouldn't return an HTML page in all cases.
              Should accept a DataTime object as well as a string.
        
        Arguments: effective_date -- a DateTime parsable string
        Return: HTML page
        Permission: 'Request review'         
        """
