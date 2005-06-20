import sys
from distutils.core import setup
from zopeedit import __version__

try:
    import py2exe
except ImportError:
    if sys.platform == 'win32':
        raise
    packages = None
else:
    packages = ['Plugins']

setup(name='zopeedit',
      version=__version__,
      description="Zope External Editor",
      author="Casey Duncan and Contributors, maintained by Chris McDonough",
      author_email="chrism@plope.com",
      url="http://www.plope.com/software/ExternalEditor",
      scripts=['zopeedit.py'],
      windows=['zopeedit.py'],
      options={"py2exe": {"packages": ["encodings", "Plugins", "win32com"]}},
      
      packages=packages
      )
