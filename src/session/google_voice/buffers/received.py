import threading
from main import GoogleVoice

class Received(GoogleVoice):

 def __init__(self, *args, **kwargs):
  self.init_done_event = threading.Event()
  self.item_name = _("received call")
  self.item_name_plural = _("received calls")
  super(Received, self).__init__(*args, **kwargs)
  self.default_template = 'call'
  self.init_done_event.set()

 def retrieve_update(self, *args, **kwargs):
  return self.session.gv.received().folder['messages']
  