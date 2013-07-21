from logger import logger
logging = logger.getChild('core.sessions.configuration')

from copy import deepcopy
from pkg_resources import resource_filename
import os
from pydispatch import dispatcher

from configobj import ConfigObj
from validate import Validator, VdtValueError
from utils.thread_utils import call_threaded
import misc
import signals
import threading

from core.sessions.storage.storage import Storage
from core.sessions.file_system import FileSystem

class Configuration(FileSystem,Storage):

 def __init__(self, config={},*args,**kwargs):
  super(Configuration, self).__init__(*args, **kwargs)
  self.load_session_configuration()
  self.load_session_defaults()
  dispatcher.connect(self.configuration_saved, signal=signals.config_saved, sender=self)

 def load_session_configuration(self):
  self.config = self.load_config_file('session.defaults')

 def load_config_file(self, filename=None):
  if filename.endswith(('.confspec', '.defaults')):
   cfg_file = filename.split('.')
   cfg_file[-1] = 'conf'
   cfg_file = ".".join(cfg_file)
  else:
   cfg_file = filename
  cfg_file = os.path.join(self.session_path, cfg_file)
  file = self._config_spec_path(self, filename)
  spec = ConfigObj(file, list_values=False, encoding='UTF8')
  config =    ConfigObj(infile=cfg_file, configspec=spec, create_empty=True, unrepr=True, encoding='UTF8')
  return self.validate_config(config)

 def validate_config(self, config):
  validator = Validator()
  try:
   validated = config.validate(validator, copy=True)
   if validated:
    config.write()
  except VdtValueError:
   logging.exception("Unable to validate configuration")
   raise
  return config

 @staticmethod
 def _config_spec_path(cls, filename):
  return resource_filename(cls.__module__, filename)

 def update_dict(self, dict1, dict2):
  for key in dict2.keys():
   if key not in dict1.keys():
    dict1[key] = deepcopy(dict2[key])
   elif key in dict1.keys() and hasattr(dict1[key], 'keys') and hasattr(dict2[key], 'keys'):
    self.update_dict(dict1[key], dict2[key])

 def configuration_saved (self):
  pass

 def required_config (self):
  #This is called when a session requires config from the user and should be overridden on a session-by-session basis.
  raise NotImplementedError

 @staticmethod 
 def _all_parents (base):
  parents = [type(base)]
  for i in parents:
   if len(i.mro()) > 1 and i.mro()[1] not in parents:
    parents.extend(i.mro())
  parents = misc.RemoveDuplicates(parents)
  parents.remove(type(base))
  return parents

 def load_session_defaults (self, filename=None):
  if not filename:
   filename = "session.defaults"
  for i in self._all_parents(self):
   file = self._config_spec_path(i, filename)
   if not os.path.exists(file):
    continue
   spec = ConfigObj(file, list_values=False, encoding='UTF8')
   config = ConfigObj(configspec=spec, encoding='UTF8')
   config = self.validate_config(config)
   #First, merge with the values from the main dictionary so to avoid overriding them
   config.merge(self.config)
   #And now, load anything extra into the session config
   self.config.merge(config)
   self.save_config()

 def save_config(self):
  self.config.write()

