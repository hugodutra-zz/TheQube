from logger import logger
logging = logger.getChild('core.sessions.interface.main')

import session
import interface

from core.sessions.session import Session

class Interface (Session):
 """Abstract class which provides a .interface which will have methods meant to interact with the session from a user-interface perspective."""

 def __init__ (self, interface=None, *args, **kwargs):
  if not interface:
   #If no interface is provided, attempt to load a default session interface for current session.
   module = self.__module__
   module = module.split('.')
   module = eval(".".join(module[:-1]))
   logging.debug("Current module: %r" % module)
   interface = module.interface.interface
   logging.debug("Potential interface: %r" % interface)
   interface = interface()
  self.interface = interface
  super(Interface, self).__init__(*args, **kwargs)

