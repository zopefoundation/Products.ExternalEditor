""" CMFHotfix_20030908 product.

Please see the README.txt for affected versions, installation, etc.

$Id$
"""

from Globals import InitializeClass
from zLOG import LOG, INFO
from Products.CMFCore.ActionProviderBase import ActionProviderBase

InitializeClass( ActionProviderBase )

LOG( 'CMFHotfix_20030908', INFO
    , 'Initialized class: CMFCore.ActionProviderBase.ActionProviderBase.'
    )
