from log import logging
import config
from core.sessions.storage.storage_migration import MigrationBase

class Migration (MigrationBase):
 def forwards(self):
  root = self.session.connection.get_root()
  if 'config' in root and 'keymap' in root['config'] and 'FullMute' in root['config']['keymap']:
   root['config']['keymap']['ToggleGlobalMute'] = root['config']['keymap']['FullMute']
   del root['config']['keymap']['FullMute']
  if 'config' in root and 'keymap' in root['config'] and 'ToggleMute' in root['config']['keymap']:
   root['config']['keymap']['ToggleSessionMute'] = root['config']['keymap']['ToggleMute']
   del root['config']['keymap']['ToggleMute']
  if 'keymap' in config.main and 'ToggleMute' in config.main['keymap']:
   del config.main['keymap']['ToggleMute']
   config.main.write()
