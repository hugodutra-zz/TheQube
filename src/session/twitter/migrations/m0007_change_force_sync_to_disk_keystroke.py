import config
from core.sessions.storage.storage_migration import MigrationBase

class Migration (MigrationBase):
 def forwards(self):
  root = self.session.connection.get_root()
  if 'config' in root.keys() and 'keymap' in root['config'].keys() and 'ForceSyncToDisk' in root['config']['keymap'].keys():
   del root['config']['keymap']['ForceSyncToDisk']
  if 'keymap' in config.main.keys() and 'ForceSyncToDisk' in config.main['keymap'].keys() and config.main['keymap']['ForceSyncToDisk'] == "control+win+s":
   config.main['keymap']['ForceSyncToDisk'] = "control+shift+win+alt+s"
   config.main.write()
