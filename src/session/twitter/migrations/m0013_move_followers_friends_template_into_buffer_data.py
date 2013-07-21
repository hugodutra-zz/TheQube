from core.sessions.storage.storage_migration import MigrationBase

class Migration (MigrationBase):
 def forwards(self):
  root = self.session.connection.get_root()
  if 'config' in root.keys() and 'buffers' in root['config'].keys() and hasattr(root['config']['buffers'], 'keys') and 'templates' in root['config'].keys() and 'followers_friends' in root['config']['templates'].keys():
   for buffer in root['config']['buffers'].keys():
    data = root['config']['buffers'][buffer]
    if hasattr(data, 'has_key') and not data.has_key('spoken') and not data.has_key('clipboard') and buffer.startswith('followers') or buffer.startswith('friends'):
     data['spoken'] = root['config']['templates']['followers_friends']
     data['clipboard'] = root['config']['templates']['followers_friends']
