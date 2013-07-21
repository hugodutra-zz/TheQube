import config
from core.sessions.storage.storage_migration import MigrationBase

class Migration (MigrationBase):
 def forwards(self):
  root = self.session.connection.get_root()
  if 'config' in root.keys() and 'templates' not in root['config'].keys():
   try:
    root['config']['templates'] = config.twitter['templates']
   except AttributeError:
    # The user doesn't have twitter.conf (i.e. updated from old revision), try templates.conf
    try:
     root['config']['templates'] = config.templates
    except AttributeError:
     # Hmm, no templates.conf either, giving up
     pass