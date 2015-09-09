from setuptools import setup, find_packages


setup(name='Products.ExternalEditor',
      version='2.0.0dev',
      description="Zope External Editor",
      long_description=open("README.txt").read() + "\n" + \
                       open("CHANGES.txt").read(),
      classifiers=[
        'Framework :: Zope2',
      ],
      author="Zope Foundation and Contributors",
      maintainer="Chris McDonough",
      maintainer_email="chrism@plope.com",
      license="ZPL 2.1",
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
