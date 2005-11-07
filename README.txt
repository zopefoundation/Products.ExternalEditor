Overview

  Basket is a Zope 2 product which allows you to employ the Python Egg
  format to deploy other Zope 2 products.

Where Do Eggs Go?

  You can put Product eggs anywhere on your Zope 2 instance's
  PYTHONPATH.  A "safe" place to put them is
  '$INSTANCE_HOME/lib/python' which is on the PYTHONPATH of every
  post-2.6 Zope 2 installation.
  
Definitions

  Product -- A Python package that (optionally) includes an
  initialization function which gets called at Zope startup time.
  Products may be packaged as eggs using Basket; otherwise they are
  typically packaged as tarballs which are meant to be unpacked in a
  Zope 2 "Products" directory.

  Egg Product -- a Product packaged up as part of a Product Distribution.

  Product Distribution -- A Python "egg" which contains one or more
  Zope 2 Products.

How Does Basket Determine Which Products To Install?

  Default: Implicit

    By default, Basket will scan your PYTHONPATH for files or
    directories ending with the extension ".egg".  These are known as
    "distributions".  For each of these distributions Basket finds, it
    will introspect the content of the file or directory.  If the file
    is a zip file and its egg metadata contains one or more
    "zope2.initialize" "entry points", this distribution will be
    considered to be a Product distribution and its constituent
    Products will be considered for initialization.  The same action
    will happen if the .egg is a directory.  If two versions of the
    same distribution are found on the PYTHONPATH, Basket will prevent
    startup from occurring by raising a
    pkg_resources.VersionConflictError.  If Basket detects a situation
    in which two distinct Product distributions contain a Product that
    has the same name (a case which is not caught by pkg_resources),
    Basket will prevent startup by raising an exception.

  Optional: Explicit

    If you create a file in your INSTANCE_HOME/etc directory named
    PRODUCT_DISTRIBUTIONS.txt, Basket will not scan the PYTHONPATH for
    Product distributions.  Instead, Basket will attempt to load
    Product distributions based only on the explicit Python Egg-format
    Product distribution names on each line within the
    PRODUCT_DISTRIBUTIONS.txt file.  The eggs representing these
    distributions must be somewhere on the PYTHONPATH.  If a line in
    the file names a distribution that cannot be in the PYTHONPATH,
    Basket will prevent startup from occurring by raising a
    pkg_resources.DistribtionNotFound error.  If the
    PRODUCT_DISTRIBUTIONS.txt contains directives that cause two or
    more versions of the same distribution to be considered, a
    pkg_resources.VersionConflictError will be raised.  If Basket
    detects a situation in which two distinct Product distributions
    contain a Product that has the same name (a case which is not
    caught by pkg_resources), Basket will prevent startup by raising
    an exception.

How Do I Create Eggs that are Compatible with Basket?

  The only hard-and-fast requirement for creating a Product
  distribution is that you must create a "built
  egg":http://peak.telecommunity.com/DevCenter/PkgResources.  A
  Product distribution is are simply a set of Python packages which
  includes one or more initialization functions which Zope will call
  during its startup process.

  If your Product needs to be imported and initialized during Zope
  startup (e.g. to register meta types or to show up in the Control
  Panel Product list), you will need to define one or more "entry
  points" of type 'zope2.initialize' in your setup.py 'setup' call
  indicating which functions should be called during initialization.
  If your product distribution contains only one Product, this "entry
  point" is conventionally just 'SomePackageName:initialize'.

  Products that are packaged as 'zip-safe' egg files must not attempt
  to use Zope API functions that expect Product files to exist within
  a filesystem structure.

  A Product distribution may include a "Products" namespace package,
  but it is not required.  Each package within a Product distribution
  which directly contains a 'zope2.initialize' function will be
  considered a separate "Product".  This means that the name of a
  non-module package which directly contains the 'zope2.initialize'
  function will be used as a Product name in Zope's control panel and
  for legacy Zope API methods which expect to be able to use a Product
  name to access constructor functions.  Note that the behavior of
  Products packaged within Product distributions differs slightly from
  that of "legacy" Products inasmuch as "egg Products" are not
  imported at Zope startup time and will not show up in the
  ControlPanel list unless their packaging specifies a
  'zope2.initialize' entry point.

Hello World (with Products Namespace Package)

  filesystem layout::

    |
    |-- setup.py
    |
    |-- Products --
                  |
                  |-- __init__.py
                  |
                  |-- product1 -- 
                                 |
                                 |-- __init__.py

  setup.py::

    from setuptools import setup, find_packages
    import ez_setup
    ez_setup.use_setuptools()

    setup(
        name = 'product1',
        version = '0.1',
        packages = find_packages(),
        namespace_packages=['Products'],
        entry_points = {'zope2.initialize':
                        ['initialize=Products.product1:initialize']},
        url = 'http://www.example.com/product1',
        author = 'Joe Bloggs',
        author_email = 'bloggs@example.com',
        )

  Products/__init__.py::

     # this is a namespace package

  Products/product1/__init__.py::

     # this is a product initializer
     def initialize(self):
        return "product1 initialized"

Hello World (no namespace packages)

  filesystem layout::

    |
    |-- setup.py
    |
    |-- product1 -- 
                   |
                   |-- __init__.py

  setup.py::

    from setuptools import setup, find_packages
    import ez_setup
    ez_setup.use_setuptools()

    setup(
        name = 'product1',
        version = '0.1',
        packages = find_packages(),
        entry_points = {'zope2.initialize':
                        ['initialize=product1:initialize']},
        url = 'http://www.example.com/product1',
        author = 'Joe Bloggs',
        author_email = 'bloggs@example.com',
        )

  product1/__init__.py::

     # this is a product initializer
     def initialize(self):
        return "product1 initialized"

Multiple Products In A Single Distribution


  filesystem layout::

    |
    |-- setup.py
    |
    |-- product1 -- 
    |              |
    |              |-- __init__.py
    |
    |-- product2 -- 
                   |
                   |-- __init__.py

  setup.py::

    from setuptools import setup, find_packages
    import ez_setup
    ez_setup.use_setuptools()

    setup(
        name = 'products1and2',
        version = '0.1',
        packages = find_packages(),
        entry_points = {'zope2.initialize':
                        ['initialize1=product1:initialize',
                         'initialize2=product2:initialize']},
        url = 'http://www.example.com/products1and2',
        author = 'Joe Bloggs',
        author_email = 'bloggs@example.com',
        )

  product1/__init__.py::

     # this is a product initializer
     def initialize(self):
        return "product1 initialized"

  product2/__init__.py::

     # this is a product initializer
     def initialize(self):
        return "product2 initialized"

Building a Product Distribution

 'python setup.py bdist_egg'

 The ".egg" file created in dist is the Product distribution.  Refer
 to the setuptools documentation for advanced options.

Forward Compatibility Notices

  Note that the use of PRODUCT_DISTRIBUTIONS.txt may vanish in a later
  release of Basket in favor of a special section within the Zope 2
  main configuration file.

  The implicit load-all-product-distributions behavior may become
  non-default in a later release in favor of using explicit
  distribution naming.

  The "Basket" product is a stopgap solution to the problem of being
  able to package Zope products as Python eggs.  Its functionality
  will be foldeed into a later Zope release, at which point it will
  cease to be useful and disappear.  Therefore, you should not depend
  on importing or otherwise using the "Products.Basket" package or its
  contents anywhere in your own Zope code.
