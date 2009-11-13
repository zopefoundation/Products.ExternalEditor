from setuptools import setup, find_packages


setup(name='Products.ExternalEditor',
      version='1.0a2',
      description="Zope External Editor",
      long_description=open("README.txt").read() + "\n" + \
                       open("CHANGES.txt").read(),
      classifiers=[
        'Framework :: Zope2',
      ],
      author="Casey Duncan and Contributors, maintained by Chris McDonough",
      author_email="chrism@plope.com",
      url="http://pypi.python.org/pypi/Products.ExternalEditor",
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
