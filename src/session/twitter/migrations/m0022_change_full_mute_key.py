import config
from core.sessions.storage.storage_migration import MigrationBase

class Migration (MigrationBase):
 def forwards(self):
  root = self.session.connection.get_root()
  if 'sounds' in config.main and 'fullMute' in config.main['sounds']:
   if config.main['sounds']['fullMute'] and config.main['sounds']['fullMute'] == 'True':
    config.main['sounds']['mute'] = True
   else:
    config.main['sounds']['mute'] = False
   del config.main['sounds']['fullMute']
   config.main.write()
