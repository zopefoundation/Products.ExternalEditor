import unittest
import os
import sys
import copy
import pkg_resources
import Products
from Products.Basket.utils import EggProductContext
from Products.Basket import get_containing_package
from OFS.ObjectManager import ObjectManager
from OFS.SimpleItem import SimpleItem

here = os.path.dirname(__file__)

class DummyProduct:

	def __init__(self, id):
		self.id = id

class DummyPackage:
	__name__ = 'Products.Basket'
        __path__ = os.path.split(here)[:-2]

class DummyApp(ObjectManager):

	def __init__(self):
		self.Control_Panel = SimpleItem()
		self.Control_Panel.id = 'Control_Panel'
		self.Control_Panel.Products = ObjectManager()
		self.Control_Panel.Products.id = 'Products'
	
class DummyProductContext:

	def __init__(self, product_name):
		self._ProductContext__app = DummyApp()
		self._ProductContext__prod = DummyProduct(product_name)
		self._ProductContext__pack = DummyPackage()

class TestBasket(unittest.TestCase):

    def setUp(self):
        self.working_set = pkg_resources.working_set
        self.oldsyspath = sys.path[:]
        self.oldsysmodules = copy.copy(sys.modules)
        self.oldentries = self.working_set.entries[:]
        self.oldby_key = copy.copy(self.working_set.by_key)
        self.oldentry_keys = copy.copy(self.working_set.entry_keys)
        self.old_callbacks = self.working_set.callbacks[:]
        self.oldproductpath = Products.__path__
        self.fixtures = os.path.join(here, 'fixtures')

    def tearDown(self):
        sys.path[:] = self.oldsyspath
        sys.modules.clear()
        sys.modules.update(self.oldsysmodules)
        working_set = self.working_set
        working_set.entries[:] = self.oldentries
        working_set.by_key.clear()
        working_set.by_key.update(self.oldby_key)
        working_set.entry_keys.clear()
        working_set.entry_keys.update(self.oldentry_keys)
        working_set.callbacks[:] = self.old_callbacks
        Products.__path__[:] = self.oldproductpath

    def _getTargetClass(self):
        from Products.Basket import Basket
        return Basket

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_require_success(self):
        basket = self._makeOne()
        basket.pre_initialized = True

        self.failIf(sys.modules.has_key('Products.product1'))
        self.failIf(sys.modules.has_key('Products.product2'))

        sys.path.append(self.fixtures)
        self.working_set.add_entry(self.fixtures)

        basket.require(distro_str='product1>=0.1')
        basket.require(distro_str='product2>=0.1')

        import Products.product1
        import Products.product2

        self.failUnless(sys.modules.has_key('Products.product1'))
        self.failUnless(sys.modules.has_key('Products.product2'))

    def test_require_fail(self):
        basket = self._makeOne()
        basket.pre_initialized = True

        sys.path.append(self.fixtures)
        self.working_set.add_entry(self.fixtures)

        self.assertRaises(pkg_resources.DistributionNotFound,
                          basket.require,
                          distro_str='product1>=0.2')

    def test_initialize(self):
        basket = self._makeOne()
        basket.pre_initialized = True
        
        sys.path.append(self.fixtures)
        self.working_set.add_entry(self.fixtures)

        basket.require(distro_str='product1>=0.1')
        basket.require(distro_str='product2>=0.1')
		
        result = basket.initialize(DummyProductContext('Basket'))
        self.assertEqual(result, ['product1 initialized',
                                  'product2 initialized'])
        self.failUnless(sys.modules.has_key('Products.product1'))
        self.failUnless(sys.modules.has_key('Products.product2'))

    def test_parse_product_distributions_file(self):
        from StringIO import StringIO
        fp = StringIO("jammyjam>0.1\n\njohnnyjoe>=0.2\n\n")
        basket = self._makeOne()
        basket.pre_initialized = True
        distributions = basket.parse_product_distributions_file(fp)
        expected = ['jammyjam>0.1', 'johnnyjoe>=0.2']
        self.assertEqual(distributions, expected)

    def test_source_egg(self):
        basket = self._makeOne()
        basket.pre_initialized = True

        sys.path.append(self.fixtures)
        self.working_set.add_entry(self.fixtures)

        basket.require(distro_str='diskproduct1')
        result = basket.initialize(DummyProductContext('Basket'))
        self.assertEqual(result, ['diskproduct1 initialized'])

    def test_product_distributions_by_dwim(self):
        basket = self._makeOne()
        basket.pre_initialized = True

        sys.path.append(self.fixtures)
        self.working_set.add_entry(self.fixtures)

        distributions = basket.product_distributions_by_dwim()
        expected = [ 'diskproduct1', 'product1', 'product2' ]
        # don't consider other eggs that happen to be on the path, only
        # test that we find the things that are in our fixture dir
        actual = [ dist.key for dist in distributions if dist.key in expected ]
        self.assertEqual(expected, actual)

    def test_preinitalize_pdist_file_success(self):
        basket = self._makeOne()
        sys.path.append(self.fixtures)
        self.working_set.add_entry(self.fixtures)

        pdist = os.path.join(self.fixtures, 'pdist-ok.txt')
        self.assertEqual(basket.pre_initialized, False)
        basket.preinitialize(pdist)
        self.assertEqual(basket.pre_initialized, True)

        import Products.product1
        import Products.product2
        self.assertRaises(ImportError,
                          self._importProduct,
                          'Products.diskproduct1')
        
        self.failUnless(sys.modules.has_key('Products.product1'))
        self.failUnless(sys.modules.has_key('Products.product2'))
        self.failIf(sys.modules.has_key('Products.diskproduct1'))
        
    def test_preinitalize_pdist_file_fail(self):
        basket = self._makeOne()
        sys.path.append(self.fixtures)
        self.working_set.add_entry(self.fixtures)

        pdist = os.path.join(self.fixtures, 'pdist-fail.txt')
        self.assertEqual(basket.pre_initialized, False)
        self.assertRaises(pkg_resources.DistributionNotFound,
                          basket.preinitialize,
                          pdist)
        self.assertEqual(basket.pre_initialized, False)

        self.failIf(sys.modules.has_key('Products.product1'))
        self.failIf(sys.modules.has_key('Products.product2'))
        self.failIf(sys.modules.has_key('Products.product3'))
        self.failIf(sys.modules.has_key('Products.diskproduct1'))

        import Products.product1
        import Products.product2
        self.assertRaises(ImportError,
                          self._importProduct,
                          'Products.product3')
        self.assertRaises(ImportError,
                          self._importProduct,
                          'Products.diskproduct1')
        
        self.failUnless(sys.modules.has_key('Products.product1'))
        self.failUnless(sys.modules.has_key('Products.product2'))
        self.failIf(sys.modules.has_key('Products.product3'))
        self.failIf(sys.modules.has_key('Products.diskproduct1'))

    def test_preinitialize_missing_pdist(self):
        basket = self._makeOne()
        sys.path.append(self.fixtures)
        self.working_set.add_entry(self.fixtures)

        pdist = os.path.join(self.fixtures, 'nothere.txt')
        # falls back to dwim mode

        self.assertEqual(basket.pre_initialized, False)
        basket.preinitialize(pdist)
        self.assertEqual(basket.pre_initialized, True)

        import Products.product1
        import Products.product2
        import Products.diskproduct1

        self.failUnless(sys.modules.has_key('Products.product1'))
        self.failUnless(sys.modules.has_key('Products.product2'))
        self.failUnless(sys.modules.has_key('Products.diskproduct1'))

    def test_get_containing_package(self):
        self.assertEqual(
            get_containing_package('Products.PageTemplates.PageTemplate'
                                   ).__name__,
            'Products.PageTemplates')
        self.assertEqual(
            get_containing_package('Shared.DC.ZRDB').__name__,
            'Shared.DC.ZRDB')

    def _importProduct(self, name):
        __import__(name)

class TestEggProductContext(unittest.TestCase):

    def tearDown(self):
        if sys.modules.has_key('Dummy.Foo'):
            del sys.modules['Dummy.Foo']
        if sys.modules.has_key('Dummy.Bar'):
            del sys.modules['Dummy.Bar']

    def _getTargetClass(self):
        from Products.Basket.utils import EggProductContext
        return EggProductContext

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_constructor(self):
        def initializer(context):
            return 'initializer called'
        app = DummyApp()
        package = DummyPackage()
        context = self._makeOne('DummyProduct', initializer, app, package)
        data = context.install()
        self.assertEqual(data, 'initializer called')
        self.assertEqual(context.productname, 'DummyProduct')
        self.assertEqual(context.initializer, initializer)
        self.assertEqual(context.package, package)
        self.assertEqual(context.product.__class__.__name__, 'EggProduct')

    def test_module_aliases(self):
        def initializer(context):
            return 'initializer called'
        app = DummyApp()
        package = DummyPackage()
        package.__module_aliases__ = (
            ('Dummy.Foo', 'Products.Basket'),
            ('Dummy.Bar', 'Products.Basket')
            )
        context = self._makeOne('DummyProduct', initializer, app, package)
        data = context.install()
        self.assertEqual(data, 'initializer called')
        self.assertEqual(sys.modules['Dummy.Foo'].__name__,
                         'Products.Basket')
        self.assertEqual(sys.modules['Dummy.Bar'].__name__,
                         'Products.Basket')

    def test_misc_under_set(self):
        def initializer(context):
            return 'initializer called'
        app = DummyApp()
        package = DummyPackage()
        def afunction():
            pass
        package.misc_ = {'afunction':afunction}
        context = self._makeOne('DummyProduct', initializer, app, package)
        data = context.install()
        from OFS import Application
        self.assertEqual(
            Application.misc_.__dict__['DummyProduct']['afunction'],
            afunction)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBasket))
    suite.addTest(makeSuite(TestEggProductContext))
    return suite
