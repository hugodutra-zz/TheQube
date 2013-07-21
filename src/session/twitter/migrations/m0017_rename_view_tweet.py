from core.sessions.storage.storage_migration import MigrationBase

class Migration (MigrationBase):

 def forwards(self):
  root = self.session.storage
  if 'config' in root and 'keymap' in root['config'] and 'ViewTweet' in root['config']['keymap']:
   del root['config']['keymap']['ViewTweet']
