import sys
from distutils.core import setup
try:
    import py2exe
except ImportError:
    if sys.platform == 'win32':
        raise
    packages = None
else:
    packages = ['Plugins']

setup(name='zopeedit', 
      scripts=['zopeedit.py'],
      windows=['zopeedit.py'],
      options={"py2exe": {"packages": ["encodings", "Plugins", "win32com"]}},
      packages=packages)
