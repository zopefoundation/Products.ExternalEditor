""" Backward compatibility;  see Products.CMFWiki.permissions

$Id$
"""

from permissions import *

from warnings import warn

warn( "The module, 'Products.CMFWiki.CMFWikiPermissions' is a deprecated "
      "compatiblity alias for 'Products.CMFWiki.permissions';  please use "
      "the new module instead.", DeprecationWarning)
