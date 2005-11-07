Overview

  Basket is a Zope product which allows you to employ the Python Egg
  format to deploy Zope products.

Where Do Eggs Go?

  You can put Product eggs anywhere on your Zope instance's
  PYTHONPATH, but the conventional location for them is in
  INSTANCE_HOME/lib/python.

How Does Basket Determine Which Products To Install?

  Default: Implicit

    By default, Basket will scan your PYTHONPATH for files or
    directories ending with the extension ".egg".  These are known as
    "distributions".  For each of these distributions Basket finds, it
    will introspect the content of the file or directory.  If the file
    is a zip file and within its internal file structure contains a
    top-level namespace package named 'Products', this distribution
    will be considered a Product distribution and considered for
    initialization.  The same action will happen if the .egg is a
    directory and contains a top-level namespace package named
    'Products'.  If two versions of the same distribution are found on
    the PYTHONPATH, Basket will prevent startup from occurring by
    raising a pkg_resources.VersionConflictError.

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
    pkg_resources.VersionConflictError will be raised.

How Do I Create Eggs that are Compatible with Basket?

  The only hard-and-fast requirement for creating a Product
  distribution is that you must create a "built
  egg":http://peak.telecommunity.com/DevCenter/PkgResources that
  includes a 'Products' "namespace package".  Packages that exist
  beneath the Products namespace package should be "normal" Zope
  products, which are simply Python packages that optionally include
  an initialization function function which Zope calls during its
  startup process.  If your product needs to be imported and
  initialized during Zope startup, you will need to define a
  'zope2.initialize' "entry point" in your setup.py 'setup' call
  indicating which function should be called during initialization.
  Conventionally, this is 'Products.YourProductName:initialize'.

  Products that are packaged as 'zip-safe' egg files must not attempt
  to use Zope API functions that expect Product files to exist within
  a filesystem structure.

Forward Compatibility Notices

  Note that the use of PRODUCT_DISTRIBUTIONS.txt may vanish in a later
  release of Basket in favor of a section within the Zope
  configuration file.

  The implicit load-all-product-distributions behavior may become
  non-default in a later release in favor of using explicit
  distribution naming.






