from core.sessions.storage.storage_migration import MigrationBase

class Migration (MigrationBase):
 def forwards(self):
  root = self.session.connection.get_root()
  if 'config' in root.keys() and 'twitter' in root['config'].keys() and root['config']['twitter'].has_key('checkInterval'):
   if not root['config'].has_key('updates'):
    root['config']['updates'] = {}
   root['config']['updates']['checkInterval'] = root['config']['twitter']['checkInterval']
   del root['config']['twitter']['checkInterval']