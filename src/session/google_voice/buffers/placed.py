import threading
from main import GoogleVoice

class Placed(GoogleVoice):

 def __init__(self, *args, **kwargs):
  self.init_done_event = threading.Event()
  self.item_name = _("placed call")
  self.item_name_plural = _("placed calls")
  super(Placed, self).__init__(*args, **kwargs)
  self.default_template = 'placed_call'
  self.init_done_event.set()

 def retrieve_update(self, *args, **kwargs):
  return self.session.gv.placed().folder['messages']

  