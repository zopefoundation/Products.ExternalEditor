"""
    CMF-based Tracker product.
"""

def initialize( context ):

    context.registerHelpTitle('CMF Tracker')
    context.registerHelp( directory="help", clear=1 )
    context.registerHelp( directory="interfaces", clear=0 )
