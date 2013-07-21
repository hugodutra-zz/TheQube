import threading
from main import GoogleVoice

class Missed(GoogleVoice):

 def __init__(self, *args, **kwargs):
  self.init_done_event = threading.Event()
  self.item_name = _("missed call")
  self.item_name_plural = _("missed calls")
  super(Missed, self).__init__(*args, **kwargs)
  self.default_template = 'call'
  self.init_done_event.set()

 def retrieve_update(self, *args, **kwargs):
  return self.session.gv.missed().folder['messages']

