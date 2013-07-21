import re
from core.sessions.storage.storage_migration import MigrationBase

NAMED = r"(?P<name>[_a-zA-Z][_a-zA-Z0-9]*)"
BRACED = r"\{(?P<braced>[_a-zA-Z][_a-zA-Z0-9]*)\}"
PATTERN = r"(?P<about>about\s+)?\$(?:" + NAMED + "|" + BRACED + ")"

class Migration (MigrationBase):
 def _Convert(self, old_template):
  def replace_when(m):
   name = m.group('name') or m.group('braced')
   if name.endswith("when") and m.group('about') is None:
    return u"about " + m.group()
   else:
    return m.group()
  return re.sub(PATTERN, replace_when, old_template)

 def forwards(self):
  root = self.session.connection.get_root()
  if 'config' not in root:
   return
  if 'templates' in root['config']:
   templates = root['config']['templates']
   for name in ('default_template', 'reply', 'retweet', 'default_followers_friends', 'user_info', 'search'):
    if name in templates:
     templates[name] = self._Convert(templates[name])
  if 'buffers' in root['config']:
   for buffer_data in root['config']['buffers'].itervalues():
    if not hasattr(buffer_data, 'has_key'):
     continue
    if 'spoken' in buffer_data:
     buffer_data['spoken'] = self._Convert(buffer_data['spoken'])
    if 'clipboard' in buffer_data:
     buffer_data['clipboard'] = self._Convert(buffer_data['clipboard'])
