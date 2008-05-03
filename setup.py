from setuptools import setup, find_packages
from zopeedit import __version__


setup(name='Products.ExternalEditor',
      version=__version__,
      description="Zope External Editor",
      classifiers=[
        'Framework :: Zope2',
      ],
      author="Casey Duncan and Contributors, maintained by Chris McDonough",
      author_email="chrism@plope.com",
      url="http://www.plope.com/software/ExternalEditor",
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
