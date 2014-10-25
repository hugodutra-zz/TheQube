import os
import sys
import shlobj

from functools import wraps

def merge_paths(func):
 @wraps(func)
 def merge_paths_wrapper(*a):
  return unicode(os.path.join(func(), *a))
 return merge_paths_wrapper


@merge_paths
def data_path(app_name='TheQube'):
 data_path = os.path.join(os.getenv('APPDATA'), app_name)
 if not os.path.exists(data_path):
  os.mkdir(data_path)
 return data_path

@merge_paths
def app_path():
 if hasattr(sys, "frozen"):
  from win32api import GetModuleFileName #We should only be here if using py2exe hence windows
  app_path = os.path.dirname(GetModuleFileName(0))
 else:
  app_path = os.path.normpath(os.path.dirname(__file__))
 return app_path

@merge_paths
def locale_path():
 return app_path(u"locale")

@merge_paths
def sounds_path():
 return app_path(u"sounds")

@merge_paths
def sessions_path():
 return app_path(u"sessions")
