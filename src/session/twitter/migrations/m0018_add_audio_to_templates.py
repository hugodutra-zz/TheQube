import config
from core.sessions.storage.storage_migration import MigrationBase

class Migration (MigrationBase):
 def forwards(self):
  root = self.session.connection.get_root()
  if 'config' in root.keys() and 'templates' in root['config'].keys():
   templates = root['config']['templates']
   if 'default_template' in templates.keys() and 'audio' not in templates['default_template']:
    templates['default_template'] = '$if(audio){*audio* } %s' % templates['default_template']
  if 'config' in root.keys() and 'buffers' in root['config'].keys():
   buffers = root['config']['buffers']
   if 'spoken' in buffers['Home'].keys() and 'audio' not in buffers['Home']['spoken']:
    buffers['Home']['spoken'] = '$if(audio){*audio* } %s' % buffers['Home']['spoken']
   if 'spoken' in buffers['Sent'].keys() and 'audio' not in buffers['Sent']['spoken']:
    buffers['Sent']['spoken'] = '$if(audio){*audio* } %s' % buffers['Sent']['spoken']
   if 'spoken' in buffers['Mentions'].keys() and 'audio' not in buffers['Mentions']['spoken']:
    buffers['Mentions']['spoken'] = '$if(audio){*audio* } %s' % buffers['Mentions']['spoken']
