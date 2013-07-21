import config
from core.sessions.storage.storage_migration import MigrationBase

class Migration (MigrationBase):
 def forwards(self):
  root = self.session.connection.get_root()
  if 'config' in root and 'keymap' in root['config'] and 'ViewTweet' in root['config']['keymap']:
   del root['config']['keymap']['ViewTweet']
  if 'keymap' in config.main and 'ViewTweet' in config.main['keymap']:
   del(config.main['keymap']['ViewTweet'])
   config.main.write()
