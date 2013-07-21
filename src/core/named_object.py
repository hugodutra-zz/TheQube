

class NamedObject(object):

 def __init__(self, name=None, display_name=None, *args, **kwargs):
  super(NamedObject, self).__init__()
  self.name = unicode(name)
  self._display_name = None
  if display_name:
   self.display_name = unicode(display_name)

 def displayed_name (self, name=None):
  if name:
   self._display_name = name
  if self._display_name:
   name = self._display_name
  else:
   name = self.name
  return unicode(name)

 display_name = property(fget=displayed_name, fset=displayed_name)

