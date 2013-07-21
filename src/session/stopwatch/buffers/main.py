from core.sessions.buffers.buffer_defaults import buffer_defaults

from core.sessions.buffers.buffers import Buffer

class Time(Buffer):
 #A buffer which holds time objects.

 def __init__(self, *args, **kwargs):
  super(Time, self).__init__(*args, **kwargs)
  self.set_field('name', _("Name"), self.get_name)

 @buffer_defaults
 def get_name(self, item=None):
  return item.name
