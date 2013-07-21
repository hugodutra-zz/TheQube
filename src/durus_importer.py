import re

import paths
import sessions
import misc
import output

class SessionImporter(object):

 def __init__(self, filename=None):
  self.session = sessions.current_session  
  if self.session.type != 'Twitter':
   raise TypeError
  if filename:
   self.load_file(filename)

 def load_file(self, filename):
  output.speak(_("Loading file..."))
  FileStorage, Connection = misc.import_durus()
  self.file = FileStorage(paths.data_path(filename))
  self.connection = Connection(self.file)
  self.root = self.connection.root

 def do_import(self):
  output.speak("Initiating import...")
  for k in self.root:
   if type(self.root[k]) == list: #An old buffer that deserves buffership!
    self.import_buffer(k)
  self.file.close()
  del(self.connection)

 def import_buffer(self, buffername):
  output.speak(_("Attempting import of buffer %s") % buffername)
  buffer = self.session.get_buffer_by_name(buffername)
  if buffer is None:
   self.session.storage[buffername] = zc.blist.BList()
  old_buf = self.root[buffername]
  buffername = re.sub(r'^\.', r'', buffername)
  buffername = re.sub(r'\.$', r'', buffername)
  new_buf = self.session.storage[buffername]
  if buffer:
   old_buf = new_buf.find_new_data(old_buf.storage)
  output.speak("In progress...")
  for i in old_buf:
   new_buf.insert(0, i)
  transaction.commit
  output.speak("Done!")

class SessionImportError(Exception): pass
