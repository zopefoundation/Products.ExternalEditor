from unittest import TestSuite
from sys import modules

def build_test_suite(package_name,module_names,required=1):
    """
    Utlitity for building a test suite from a package name
    and a list of modules.
    
    If required is false, then ImportErrors will simply result
    in that module's tests not being added to the returned
    suite.
    """
    
    suite = TestSuite()
    try:
        for name in module_names:
            the_name = package_name+'.'+name
            __import__(the_name,globals(),locals())
            suite.addTest(modules[the_name].test_suite())
    except ImportError:
        if required:
            raise
    return suite

def has_path( catalog, path ):
    """
        Verify that catalog has an object at path.
    """
    if type( path ) is type( () ):
        path = '/'.join(path)
    rids = map( lambda x: x.data_record_id_, catalog.searchResults() )
    for rid in rids:
        if catalog.getpath( rid ) == path:
            return 1
    return 0

