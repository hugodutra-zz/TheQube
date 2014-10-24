# -*- coding: utf-8 -*-


from setuptools import setup, find_packages
import py2exe, innosetup
import shutil
from glob import glob
import os
from logger import logger
logging = logger.getChild("Installer")


name = 'TheQube'
__version__ = 0.7
__author__ = 'TheQube developers team'
DELETE_DIRS = (
 'build',
 'dist',
 'release',
 'update'
)

[shutil.rmtree(i, ignore_errors=True) for i in DELETE_DIRS]
def get_datafiles():
 return [("", ["main.defaults"] + glob('*.exe') + glob("*.dll"))
] + list_all_documentation() + list_session_defaults()  + accessible_output_data() + sound_lib_data() + requests_data() + get_soundpacks() + get_locales()

def accessible_output_data():
 import accessible_output2
 return accessible_output2.find_datafiles()

def sound_lib_data():
 import sound_lib
 return sound_lib.find_datafiles()

def requests_data():
 import requests
 path = os.path.join(requests.__path__[0], '*.pem')
 results = glob(path)
 dest_dir = os.path.join('requests')
 return [(dest_dir, results)]

def list_session_defaults():
 files = glob('session/*/*.defaults') + glob('core/sessions/*/*.defaults')
 answer = []
 for i in files:
  answer.append((os.path.split(i)[0], [i]))
 return answer

def get_soundpacks():
 answer = []
 depth = 6
 for root, dirs, files in os.walk('sounds'):
  if depth == 0:
   break
  new = (root, glob('%s/*.wav' % root))
  answer.append(new)
  depth -= 1
 return answer

def get_locales():
 answer = []
 for root, dirs, files in os.walk('locale'):
  new = (root, glob(os.path.join(root, '*.mo')))
  answer.append(new)
 return answer

def list_all_documentation ():
 answer = []
 depth = 6
 for root, dirs, files in os.walk('../Documentation'):
  if depth == 0:
   break
  readme = (root[3:], [os.path.join(root, 'readme.html')])
  answer.append(readme)
  changelog = (root[3:], [os.path.join(root, 'changelog.html')])
  answer.append(changelog)
  depth -= 1
 return answer

if __name__ == '__main__':
 setup(
  name = name,
  author = __author__,
  author_email = "theqube@lists.oire.org",
  version = __version__,
  url = 'http://theqube.oire.org/',
  packages = find_packages(),
  data_files = get_datafiles(),
  options = {
   'py2exe': {
    'compressed': False,
    'dll_excludes': ["powrprof.dll", "mswsock.dll"],
    'optimize': 1,
    'skip_archive': True,
    'excludes': ["win32ui", "pywin.dialogs", "pywin.debugger.dbgcon", "tkinter", "tk", "Tkconstants", "Tkinter", "tcl", "_imagingtk", "PIL._imagingtk", "ImageTk", "PIL.ImageTk", "FixTk", "twisted", "django", "gobject", "gtk", "unittest", "remote", "ZODB", "zope.interface"],
   },
   'innosetup': {
    'inno_setup_exe': "C:\\Program Files\\Inno Setup 5\\ISCC.exe"
   },
  },
  windows = [
   {
    'script': 'main.pyw',
    'dest_base': 'TheQube',
   }
  ],
  install_requires = [
  ]
 )

