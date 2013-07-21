from core.sessions.buffers.exporter.exporters import BaseExporter
import codecs

class TextExporter (BaseExporter):
 def __init__(self, **kwargs):
  if 'item_template' not in kwargs or kwargs['item_template'] is None:
   raise TypeError("This exporter requires item_template to be str or unicode.")
  super(TextExporter, self).__init__(**kwargs)
 
 def Run(self):
  with self:
   with codecs.open(self.filename, "w", "utf8") as f:
    for item in self.GetFormattedItems():
     f.write(item + u"\r\n")

 @classmethod
 def GetFileExtension(self):
  return "txt"

 @classmethod
 def GetName(self):
  return _("Text file")
