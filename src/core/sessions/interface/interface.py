import sessions

class Interface(object):

 @property
 def session (self):
  #Shortcut to return the active session.
  return sessions.current_session
