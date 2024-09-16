from setuptools import find_packages
from setuptools import setup


setup(name='Products.ExternalEditor',
      version='4.0.1',
      description="Zope External Editor",
      long_description=(open("README.rst").read() + "\n" +
                        open("CHANGES.rst").read()),
      classifiers=[
          'Development Status :: 6 - Mature',
          'Environment :: Web Environment',
          'Framework :: Plone',
          'Framework :: Zope :: 5',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: Implementation :: CPython',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
          'Topic :: Software Development',
          'Topic :: Text Editors :: Text Processing',
      ],
      author="Zope Foundation and Contributors",
      author_email="zope-dev@zope.dev",
      license="ZPL 2.1",
      keywords="zope external editor WebDAV",
      url="https://github.com/zopefoundation/Products.ExternalEditor",
      project_urls={
        'Issue Tracker': ('https://github.com/zopefoundation/'
                          'Products.ExternalEditor/issues'),
        'Sources': 'https://github.com/zopefoundation/Products.ExternalEditor',
      },
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      python_requires='>=3.7',
      install_requires=[
          'setuptools',
          'Zope >= 5',
      ],
      )
