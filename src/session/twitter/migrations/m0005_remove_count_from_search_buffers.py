from core.sessions.storage.storage_migration import MigrationBase

class Migration (MigrationBase):
 def forwards(self):
  root = self.session.connection.get_root()
  if 'config' in root.keys() and 'buffers' in root['config'].keys() and hasattr(root['config']['buffers'], 'keys'):
   for buffer in root['config']['buffers'].keys():
    data = root['config']['buffers'][buffer]
    if buffer.startswith("Search_for_") and hasattr(data, 'has_key') and data.has_key('retrieveCount'):
     del data['retrieveCount']
