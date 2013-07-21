import config
from core.sessions.storage.storage_migration import MigrationBase

class Migration (MigrationBase):
 def forwards(self):
  root = self.session.connection.get_root()
  if 'config' in root.keys() and 'templates' in root['config'].keys():
   templates = root['config']['templates']
   if 'post' in templates.keys() and 'geo' not in templates['post']:
    templates['post'] = '$?geo=="yes"?*geo*? ? %s' % templates['post']
   if 'sent_tweet' in templates.keys() and 'geo' not in templates['sent_tweet']:
    templates['sent_tweet'] = '$?geo=="yes"?*geo*? ? %s' % templates['sent_tweet']
