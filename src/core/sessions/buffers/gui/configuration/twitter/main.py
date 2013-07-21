from logger import logger
logging = logger.getChild("sessions.buffers.gui.configuration")

from pydispatch import dispatcher

import crypt
import signals
from utils.thread_utils import call_threaded
import wx

from core.gui.configuration import ConfigurationDialog
from panels import *

class BufferConfigDialog (ConfigurationDialog):
 def __init__(self, session, *args, **kwargs):
  self.session = session
  self._attention_dialog = False
  if not kwargs.has_key('title'):
   kwargs['title'] = _("Buffer Configuration")
  super(BufferConfigDialog, self).__init__(*args, **kwargs)
  set_selection = False
  self.panels = [BufferPanel(None, self.nb)]
  self.nb.AddPage(self.panels[0], _("Default Settings"))
  for buffer in self.session.buffers:
   if buffer.get_flag("configurable"):
    self.panels.append(BufferPanel(buffer, self.nb))
    self.nb.AddPage(self.panels[-1], _(buffer.name))
  self.finish_setup()
  dispatcher.connect(self.SetCurrentTab, signals.change_current_buffer, session)
  self.SetCurrentTab()

 def SetDefaultValues (self):
  self.panels[0].checkInterval.SetValue(self.session.config['updates'].get('checkInterval', 240)/60)
  self.panels[0].retrieveCount.SetValue(self.session.config['counts']['retrieveCount'])
  self.panels[0].maxAPIPerUpdate.SetValue(self.session.config['updates']['maxAPIPerUpdate'])
  if int(self.panels[0].retrieveCount.GetValue()) == 200:
   self.panels[0].maxAPIPerUpdate.Enable()
  else:
   self.panels[0].maxAPIPerUpdate.Disable()
  self.panels[0].mute.SetValue(self.session.config['sounds']['defaultBufferMute'])
  for panel in self.panels[1:]:
   if 'interval' in panel.buffer.buffer_metadata:
    panel.checkInterval.SetValue(panel.buffer.buffer_metadata['interval'] / 60)
   else:
    panel.checkInterval.Disable()
   if 'retrieveCount' in panel.buffer.buffer_metadata:
    panel.retrieveCount.SetValue(panel.buffer.buffer_metadata['retrieveCount'])
   else:
    panel.retrieveCount.Disable()
   if 'maxAPIPerUpdate' in panel.buffer.buffer_metadata:
    panel.maxAPIPerUpdate.SetValue(panel.buffer.buffer_metadata['maxAPIPerUpdate'])
    if int(panel.retrieveCount.GetValue()) == 200:
     panel.maxAPIPerUpdate.Enable()
    else:
     panel.maxAPIPerUpdate.Disable()
   else:
    panel._maxAPIPerUpdate_is_active = False
    panel.maxAPIPerUpdate.Disable()
   if 'sounds' in panel.buffer.buffer_metadata and 'mute' in panel.buffer.buffer_metadata['sounds']:
    panel.mute.SetValue(panel.buffer.buffer_metadata['sounds']['mute'])
   else:
    panel.mute.Disable()
   if panel.buffer.get_flag('fixed_template'):
    panel.clipboard.Disable()
    panel.useDefaultClipboard.Disable()
    panel.spoken.Disable()
    panel.useDefaultSpoken.Disable()
   else:
    panel.spoken.SetValue(panel.buffer.get_template('spoken'))
    panel.clipboard.SetValue(panel.buffer.get_template('clipboard'))
    panel.useDefaultSpoken.SetValue('spoken' not in panel.buffer.buffer_metadata)
    panel.useDefaultSpoken_changed()
    panel.useDefaultClipboard.SetValue('clipboard' not in panel.buffer.buffer_metadata)
    panel.useDefaultClipboard_changed()

 def SetNewConfigValues (self):
  logging.debug("Saving default buffer configuration from dialog.")
  self.session.config['updates']['checkInterval'] = int(self.panels[0].checkInterval.GetValue()) * 60
  logging.info("Check interval set to: %s" % self.session.config['updates']['checkInterval'])
  self.session.config['counts']['retrieveCount'] = int(self.panels[0].retrieveCount.GetValue()) or 100
  logging.info("Retrieve count set to: %s" % self.session.config['counts']['retrieveCount'])
  self.session.config['updates']['maxAPIPerUpdate'] = int(self.panels[0].maxAPIPerUpdate.GetValue()) or 1
  logging.info("Max API calls per update set to: %s" % self.session.config['updates']['maxAPIPerUpdate'])
  self.session.config['sounds']['defaultBufferMute'] = self.panels[0].mute.GetValue()
  logging.info("Mute set to: %s" % self.session.config['sounds']['mute'])
  if self.panels[0].applyToAll.GetValue():
   apply = call_threaded(self.ApplyDefaultBufferSettingsToAll)
  else:
   logging.debug("Saving buffer configuration from dialog.")
   for panel in self.panels[1:]:
    if panel.buffer.buffer_metadata.has_key('interval') and panel.buffer.buffer_metadata['interval'] != panel.checkInterval.GetValue() * 60:
     panel.buffer.set_new_interval(panel.checkInterval.GetValue() * 60)
     logging.info("Update interval for buffer %s set to: %s" % (panel.buffer.name, panel.buffer.buffer_metadata['interval'] / 60))
    if panel.buffer.buffer_metadata.has_key('retrieveCount') and panel.buffer.buffer_metadata['retrieveCount'] != panel.retrieveCount.GetValue():
     panel.buffer.count = panel.buffer.buffer_metadata['retrieveCount'] = panel.retrieveCount.GetValue()
     logging.info("Retrieve count for buffer %s set to: %s" % (panel.buffer.name, panel.buffer.buffer_metadata['retrieveCount']))
    if panel.buffer.buffer_metadata.has_key('maxAPIPerUpdate') and panel.buffer.buffer_metadata['maxAPIPerUpdate'] != panel.maxAPIPerUpdate.GetValue():
     panel.buffer.maxAPIPerUpdate = panel.buffer.buffer_metadata['maxAPIPerUpdate'] = panel.maxAPIPerUpdate.GetValue()
     logging.info("Retrieve count for buffer %s set to: %s" % (panel.buffer.name, panel.buffer.buffer_metadata['maxAPIPerUpdate']))
    if panel.buffer.buffer_metadata.has_key('sounds') and panel.buffer.buffer_metadata['sounds'].has_key('mute') and panel.buffer.buffer_metadata['sounds']['mute'] != panel.mute.GetValue():
     panel.buffer.buffer_metadata['sounds']['mute'] = panel.mute.GetValue()
     logging.info("Mute for buffer %s set to: %s" % (panel.buffer.name, panel.buffer.buffer_metadata['sounds']['mute']))
    if not panel.buffer.get_flag('fixed_template'):
     if panel.useDefaultClipboard.GetValue():
      if 'clipboard' in panel.buffer.buffer_metadata:
       del panel.buffer.buffer_metadata['clipboard']
      logging.info("Clipboard template for {0} was reset to default.".format(panel.buffer.name))
     else:
      panel.buffer.buffer_metadata['clipboard'] = panel.clipboard.GetValue()
      logging.info("Clipboard template for buffer %s set to: %s." % (panel.buffer.name, panel.buffer.buffer_metadata['clipboard']))
     if panel.useDefaultSpoken.GetValue():
      if 'spoken' in panel.buffer.buffer_metadata:
       del panel.buffer.buffer_metadata['spoken']
      logging.info("Spoken template for {0} was reset to default.".format(panel.buffer.name))
     else:
      panel.buffer.buffer_metadata['spoken'] = panel.spoken.GetValue()
      logging.info("Spoken template for buffer %s set to: %s." % (panel.buffer.name, panel.buffer.buffer_metadata['spoken']))

 def ApplyDefaultBufferSettingsToAll(self):
  for buffer in self.session.buffer_metadata.keys():
   if hasattr(self.session.buffer_metadata[buffer], 'has_key') and self.session.buffer_metadata[buffer].has_key('interval'):
    self.session.buffer_metadata[buffer]['interval'] = self.session.config['updates']['checkInterval']
    logging.info("Update interval for buffer %s set to: %s" % (buffer, self.session.buffer_metadata[buffer]['interval'] / 60))
   if hasattr(self.session.buffer_metadata[buffer], 'has_key') and self.session.buffer_metadata[buffer].has_key('retrieveCount'):
    self.session.buffer_metadata[buffer]['retrieveCount'] = self.session.config['counts']['retrieveCount']
    logging.info("Retrieve count for buffer %s set to: %s" % (buffer, self.session.buffer_metadata[buffer]['retrieveCount']))
   if hasattr(self.session.buffer_metadata[buffer], 'has_key') and self.session.buffer_metadata[buffer].has_key('maxAPIPerUpdate'):
    self.session.buffer_metadata[buffer]['maxAPIPerUpdate'] = self.session.config['updates']['maxAPIPerUpdate']
    logging.info("Max API calls per update for buffer %s set to: %s" % (buffer, self.session.buffer_metadata[buffer]['maxAPIPerUpdate']))
   if hasattr(self.session.buffer_metadata[buffer], 'has_key') and self.session.buffer_metadata[buffer].has_key('sounds') and self.session.buffer_metadata[buffer]['sounds'].has_key('mute'):
    self.session.buffer_metadata[buffer]['sounds']['mute'] = self.session.config['sounds']['defaultBufferMute']
    logging.info("Mute for buffer %s set to: %s" % (buffer, self.session.buffer_metadata[buffer]['sounds']['mute']))
  for buffer in self.session.buffers:
   if buffer.buffer_metadata.has_key('interval'):
    buffer.set_new_interval()

 def SetCurrentTab(self, buffer = None):
  if buffer is None:
   buffer = self.session.current_buffer
  buffer = self.get_configurable_buffer(buffer)
  found = 0
  for (i, panel) in enumerate(self.panels):
   if panel.buffer is buffer:
    found = i
    break
  self.nb.SetSelection(found)
  self.panels[found]._first.SetFocus()
  if found == 0 and not self._attention_dialog:
   self._attention_dialog = True
   dlg = wx.MessageDialog(self, _("No modifiable properties for buffer %s; showing default buffer configuration." % self.session.current_buffer.name), _("Attention"), wx.OK | wx.ICON_INFORMATION)
   dlg.ShowModal()
   dlg.Destroy()
   self._attention_dialog = False

 def Destroy(self, *args, **kwargs):
  dispatcher.disconnect(self.SetCurrentTab, signals.change_current_buffer, self.session)
  super(BufferConfigDialog, self).Destroy(*args, **kwargs)

 def get_configurable_buffer(self, buffer):
  while buffer is not None and not buffer.get_flag("configurable"):
   buffer = buffer.replaces
  return buffer
