""" Backward compatibility;  see Products.CMFCollector.permissions

$Id$
"""

from permissions import *

from warnings import warn

warn( "The module, 'Products.CMFCollector.CollectorPermissions' is a "
      "deprecated compatiblity alias for 'Products.CMFCollector.permissions'; "
      "please use the new module instead.", DeprecationWarning)
