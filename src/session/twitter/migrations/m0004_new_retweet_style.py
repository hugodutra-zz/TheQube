from core.sessions.storage.storage_migration import MigrationBase

class Migration (MigrationBase):
 def forwards(self):
  root = self.session.connection.get_root()
  if 'config' in root.keys() and 'UI' in root['config'].keys() and root['config']['UI'].has_key('AutomaticallyRT'):
   if root['config']['UI']['AutomaticallyRT']:
    root['config']['UI']['RTStyle'] = 1
   else:
    root['config']['UI']['RTStyle'] = 0
   del root['config']['UI']['AutomaticallyRT']
