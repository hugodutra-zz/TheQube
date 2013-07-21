from core.sessions.storage.storage_migration import MigrationBase

class Migration (MigrationBase):
 def forwards(self):
  root = self.session.connection.get_root()
  if 'config' in root.keys() and 'buffers' in root['config'].keys() and hasattr(root['config']['buffers'], 'keys') and 'templates' in root['config'].keys() and 'post' in root['config']['templates'].keys() and 'clipboard' in root['config']['templates'].keys():
   for buffer in root['config']['buffers'].keys():
    data = root['config']['buffers'][buffer]
    if hasattr(data, 'has_key') and data.has_key('spoken') and data.has_key('clipboard') and not buffer.startswith("Search_for_"):
     del data['spoken']
     del data['clipboard']
     data['spoken'] = root['config']['templates']['post']
     data['clipboard'] = root['config']['templates']['clipboard']
    elif hasattr(data, 'has_key') and data.has_key('spoken') and data.has_key('clipboard') and buffer.startswith("Search_for_"):
     del data['spoken']
     del data['clipboard']
     data['spoken'] = root['config']['templates']['search']
     data['clipboard'] = root['config']['templates']['search']
