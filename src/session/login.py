from logger import logger
logging = logger.getChild('core.sessions.login')

import output
from utils.wx_utils import always_call_after

from core.sessions.configuration.configuration import Configuration

class Login (Configuration):
 """An abstract class which handles logging in for various sessions."""

 @always_call_after
 def login (self):
  if self.is_login_required():
   self.login_required()
  else:
   self.complete_login()

 @always_call_after
 def complete_login (self):
  succeeded = False
  try:
   succeeded = self.do_login()
  except:
   pass
  if succeeded:
   self.login_succeeded()
  else:
   self.login_failed()

 def login_succeeded (self):
  output.speak(_("Login succeeded."), True)

 def login_failed (self):
  output.speak(_("Login failed."), True)

 def do_login (self, *args, **kwargs):
  #Replace this for your own sessions
  raise NotImplementedError

 def login_required (self):
  raise NotImplementedError

 def is_login_required (self):
  raise NotImplementedError
