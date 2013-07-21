import os
import shutil
import codecs

import paths

from core.sessions.session import Session

class FileSystem (Session):
 """Give sessions access to the file system."""

 base_user_data_path = u'data'

 def __init__ (self, name=None, *args, **kwargs):
  self.name = name
  self._setup_paths()
  super(FileSystem, self).__init__(name=name, *args, **kwargs)

 def _setup_paths(self):
  if not os.path.exists(self.session_path):
   os.mkdir(self.session_path)
  if not os.path.exists(self.user_data_path):
   os.mkdir(self.user_data_path)

 @property
 def session_path(self):
  """Returns the path where all of this session's data is stored."""
  return paths.data_path(self.name)

 @property
 def user_data_path(self):
  """Returns a path where data which is added to the session by users (such as voicemails, rss items, etc. can be stored."""
  return os.path.join(self.session_path, self.base_user_data_path)

 def open_file(self, filename, mode):
  """Given a filename, opens it from this session's directory."""
  full_path = os.path.join(self.session_path, filename)
  return codecs.open(full_path, mode, 'utf-8')

 def rename_session(self, new_name):
  shutil.move(self.session_path, paths.data_path(new_name))
  super(FileSystem, self).rename_session(new_name)
