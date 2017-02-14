from setuptools import setup, find_packages

setup(name='Products.ExternalEditor',
      version='1.1.3',
      description="Zope External Editor",
      long_description=(open("README.rst").read() + "\n" +
                        open("CHANGES.rst").read()),
      classifiers=[
          'Framework :: Zope2',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
      ],
      author="Zope Foundation and Contributors",
      author_email="zope-dev@zope.org",
      maintainer="Chris McDonough",
      maintainer_email="chrism@plope.com",
      license="ZPL 2.1",
      keywords="zope external editor",
      url="https://pypi.python.org/pypi/Products.ExternalEditor",
      packages=find_packages(),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      [console_scripts]
          zopeedit=Products.ExternalEditor.zopeedit:main
      """,
      )
