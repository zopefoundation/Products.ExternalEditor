from setuptools import setup, find_packages

setup(name='Products.ExternalEditor',
      version='3.0',
      description="Zope External Editor",
      long_description=(open("README.rst").read() + "\n" +
                        open("CHANGES.rst").read()),
      classifiers=[
          'Development Status :: 6 - Mature',
          'Environment :: Web Environment',
          'Framework :: Zope :: 4',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 2 :: Only',
          'Programming Language :: Python :: Implementation :: CPython',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
          'Topic :: Software Development',
          'Topic :: Text Editors :: Text Processing',
      ],
      author="Zope Foundation and Contributors",
      author_email="zope-dev@zope.org",
      maintainer="Chris McDonough",
      maintainer_email="chrism@plope.com",
      license="ZPL 2.1",
      keywords="zope external editor WebDAV",
      url="https://github.com/zopefoundation/Products.ExternalEditor",
      packages=find_packages(),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Zope >= 4.0b4',
          'ZServer >= 4.0b1',
          'six',
      ],
      entry_points="""
      [console_scripts]
          zopeedit=Products.ExternalEditor.zopeedit:main
      """,
      )
