from logger import logger
logging = logger.getChild('core.sessions.buffers.interface')

from pydispatch import dispatcher
from utils.thread_utils import call_threaded
from utils.wx_utils import modal_dialog
from core.sessions.buffers.buffer_defaults import buffer_defaults

import config
import output
import gui
import signals
import wx

#Handy decorator:
from core.sessions.buffers.buffer_defaults import buffer_defaults

from core.sessions.sound.interface import SoundInterface

class BuffersInterface (SoundInterface):

 @buffer_defaults
 def NextItem(self, buffer=None, step=1):
  """Moves to the next item in the current buffer."""

  if buffer.index+step >= len(buffer):
   self.session.play(self.session.config['sounds']['boundary'])
   step = len(buffer)-buffer.index-1
  buffer.index = buffer.index+step
  buffer.speak_item()

 @buffer_defaults
 def PrevItem(self, buffer=None, step=1):
  """Moves to the previous item in the current buffer."""

  if buffer.index-step < 0:
   self.session.play(self.session.config['sounds']['boundary'])
   buffer.index = 0
  else:
   buffer.index = buffer.index-step
  buffer.speak_item()

 @buffer_defaults
 def NextItemStep(self, buffer=None):
  """Moves forward in the current buffer by the percent set in the main configuration dialog."""

  step = (len(buffer)-1) / 100 * config.main['client']['step']
  self.NextItem(step=step)

 @buffer_defaults
 def PrevItemStep(self, buffer=None):
  """Moves back in the current buffer by the percent set in the main configuration dialog."""

  step = (len(buffer)-1) / 100 * config.main['client']['step']
  self.PrevItem(step=step)

 @buffer_defaults
 def NextItemTimeStep(self, buffer=None, index=None):
  """Moves forward in the current buffer by the time in hours/minutes set in the main configuration dialog."""

  try:
   new_index = buffer.get_next_item_time_step_index(config.main['client']['timeStep'], index)
  except:
   return output.speak(_("Cannot move by time in this buffer."), 1)
  if index == new_index:
   self.session.play(self.session.config['sounds']['boundary'])
  buffer.index = new_index
  buffer.speak_item()

 @buffer_defaults
 def PrevItemTimeStep (self, buffer=None, index=None):
  """Moves back in the current buffer by the time in hours/minutes set in the main configuration dialog."""

  try:
   new_index = buffer.get_prev_item_time_step_index(config.main['client']['timeStep'], index)
  except AttributeError:
   return output.speak(_("Cannot move by time in this buffer."), True)
  if index == new_index:
   self.session.play(self.session.config['sounds']['boundary'])
  buffer.index = new_index
  buffer.speak_item()

 @buffer_defaults
 def NewestItem(self, buffer=None):
  """Moves to the most recent item in the current buffer."""

  buffer.index = len(buffer)-1
  buffer.speak_item()

 @buffer_defaults
 def OldestItem(self, buffer=None):
  """""Moves to the First item in the current buffer."""

  buffer.index = 0
  buffer.speak_item()

 @buffer_defaults
 def CurrentItem(self, buffer=None):
  """Speaks the current item and it's position relative to the total number of items in the current buffer."""

  buffer.speak_item()
  buffer.speak_index()

 def PrevBuffer(self):
  """Moves to the previous buffer in the list of buffers for the current session."""

  try:
   self.session.set_buffer(self.session.get_navigation_index()-1)
   self.session.announce_buffer()
   self.session.current_buffer.announce_buffer_mute(True)
  except ValueError:
   output.speak(_("No active buffers in %s session.") % self.session.name, True)

 def NextBuffer(self):
  """Moves to the next buffer in the list of buffers for the current session."""

  try:
   self.session.set_buffer(self.session.get_navigation_index()+1)
   self.session.announce_buffer()
   self.session.current_buffer.announce_buffer_mute(True)
  except ValueError:
   output.speak(_("No active buffers in %s session.") % self.session.name, True)

 @buffer_defaults
 def DismissBuffer(self, buffer=None):
  """If possible, removes the current buffer from the list of buffers for the current session."""

  if buffer == None or not len(self.session.buffers):
   return output.speak(_("There are no buffers to dismiss."), True)
  if not buffer.get_flag('deletable'):
   return output.speak(_("Unable to dismiss buffer %s") % buffer.display_name, 1)
  cur_buffer_name = buffer.name
  try:
   self.session.remove_buffer(buffer)
  except:
   logging.exception("%s: Unable to dismiss buffer." % buffer.name)
   return output.speak(_("Unable to dismiss buffer %s") % buffer.display_name, 1)

 def UndoNavigation(self):
  """Undo the last navigation (I.E., item or buffer change)"""

  try:
   (buffer_name, index, curbuf_index) = self.session.pop()
  except IndexError:
   return output.speak(_("Undo failed: stack empty"), True)
  buffer = self.session.get_buffer_by_name(buffer_name)
  if not buffer:
   return output.speak(_("Undo failed: buffer no longer exists"), True)
  if curbuf_index >= 0:
   self.buffer().set_index(curbuf_index, False)
  self.session.set_buffer(self.session.get_navigation_index(buffer), False)
  self.buffer().set_index(index, False)
  self.buffer().speak_item()

 @buffer_defaults
 def ClearBuffer(self, buffer = None):
  """Clears all items from the current buffer."""

  if not buffer.get_flag('clearable'):
   return output.speak(_("This buffer cannot be cleared."), True)
  d = wx.MessageDialog(self.session.frame, _("Are you sure you want to delete %d items from %s?") % (len(buffer), buffer.display_name), _("Clear buffer"), wx.YES|wx.NO|wx.ICON_WARNING)
  self.session.frame.Raise()
  if d.ShowModal() != wx.ID_YES:
   self.session.frame.Show(False)
   return output.speak(_("Canceled."), True)
  buffer.clear()
  self.session.announce_buffer()

 @buffer_defaults
 def JumpToPost(self, buffer=None):
  """Moves you to the item of the specified index in the current buffer."""

  new = modal_dialog(gui.JumpToPostDialog, parent=self.session.frame, buffer=buffer)
  num = int(new.number.GetValue())
  if num > len(buffer):
   output.speak(_("Item number too high."), True)
   return self.JumpToPost(buffer=buffer)
  num = num-1
  index = len(buffer)-1 - num
  buffer.index = index
  buffer.speak_item()

 @buffer_defaults
 def ApplyFilter(self, buffer=None):
  """Display a buffer containing or excluding the items which contain the specified search criteria."""

  from core.sessions.buffers.buffers import Filtered
  if not buffer.get_flag('filterable'):
   logging.debug("Buffer %s is not filterable." % buffer.name)
   return output.speak(_("Buffer %s does not support filtration." % buffer.display_name), True)
  new = modal_dialog(gui.FilterDialog, parent=self.session.frame, buffer=buffer)
  output.speak(_("Processing.  Please wait."))
  filter_specs = new.get_filter_specs()
  for filter_spec in filter_specs:
   buftitle = Filtered.generate_filter_name(buffer, filter_spec)
   if filter_spec['replace']:
    replaces = buffer
   else:
    replaces = None
   filtered = self.session.register_buffer(buftitle, Filtered, replaces=replaces, source_name=buffer.name, **filter_spec)

 @buffer_defaults
 def CopyToClipboard(self, buffer=None, index=None):
  """Copies the current item to the clipboard."""

  if output.CopyPostToClipboard(buffer, index):
   output.speak(_("Item copied to clipboard."), True)

 @buffer_defaults
 def DeleteCurrent(self, buffer=None, index=None):
  """Removes the current item from the active buffer."""

  buffer.remove_item(index)
  buffer.speak_item(interrupt=False)
 
 @buffer_defaults
 def MoveBufferLeft(self, buffer=None):
  """Moves the current buffer one slot to the left."""

  self.session.move_buffer(buffer, -1)
  output.speak(_("Moved"), True)

 @buffer_defaults
 def MoveBufferRight(self, buffer=None):
  """Moves the current buffer one slot to the right."""

  self.session.move_buffer(buffer, 1)
  output.speak(_("Moved"), True)

 def export(self, dlg=None):
  """Writes items in a buffer to an external file."""
  if dlg is None:
   dlg = modal_dialog(gui.export.MainExportDialog, parent=self.session.frame, id=wx.ID_ANY)
  if not dlg.IsExportAvailable():
   output.speak(_("The export function is not available."), True)
  else:
    output.speak(_("Export started, please wait."), True)
    try:
     exporter = dlg.GetExporter()
     exporter.Run()
     output.speak(_("Export complete"), False)
     if dlg.format.exportMore.GetValue():
      index = dlg.items.get_buffer_index()
      if index != wx.NOT_FOUND:
       index += 1
      if dlg.items.buffer.GetCount() > 0 and (index == wx.NOT_FOUND or index >= dlg.items.buffer.GetCount()):
       index = 0
      dlg.items.set_bufferIndex(index)
      dlg.format.filename.SetValue("")
      return wx.CallAfter(self.export, dlg=dlg)
    except:
     logging.exception("Export failed.")
     output.speak(_("Export failed."), False)
     return wx.CallAfter(self.export, dlg = dlg)

 def BufferConfigDialog(self):
  """Displays a dialog in which you can set buffer speciffic properties."""

  if not hasattr(self.session, 'buffers') or len(self.session.buffers)==0:
   return output.speak(_("No buffers in this session."), 1)
  frame = self.session.frame
  #FIXME!
  try:
   if self.session.kind == "twitter":
    new = gui.configuration.twitter.BufferConfigDialog(self.session, frame, wx.ID_ANY, title=_("%s Buffer Configuration") % self.session.name)
   elif self.session.kind == "solona":
    new = core.gui.solona.buffers.BufferConfigDialog(self.session, frame, wx.ID_ANY, title=_("%s Buffer Configuration") % self.session.name)
   elif self.session.kind == "facebook":
    new = core.gui.facebook.buffers.BufferConfigDialog(self.session, frame, wx.ID_ANY, title=_("%s Buffer Configuration") % self.session.name)
   elif self.session.kind == "bing":
    new = core.gui.bing.buffers.BufferConfigDialog(self.session, frame, wx.ID_ANY, title=_("%s Buffer Configuration") % self.session.name)
   elif self.session.kind == "rss":
    new = core.gui.rss.buffers.BufferConfigDialog(self.session, frame, wx.ID_ANY, title=_("%s Buffer Configuration") % self.session.name)
   else:
    new = ThrowException
  except:
   return logging.exception("%s: Failure in buffer configuration in session" % self.session.name)
  new.SetDefaultValues()
  if new.ShowModal() == wx.ID_OK:
   new.SetNewConfigValues()
   output.speak(_("Configuration saved."), 1)
   dispatcher.send(sender=self.session, signal=signals.config_saved)
  else:
   output.speak(_("Configuration canceled."), True)
  self.session.frame.Show(False)
  new.Destroy()

 @buffer_defaults
 def UpdateCurrentBuffer (self, buffer=None):
  """Check for, and retrieve any new data in the current buffer."""

  if not buffer.get_flag('updatable'):
   return output.speak(_("Forcing updates is not permitted in this buffer."), True)
  call_threaded(buffer.update, update_type=buffer._update_types['forced'])

 @buffer_defaults
 def ViewItem(self, buffer=None, index=None):
  dlg = modal_dialog(gui.ViewItemDialog, parent=self.session.frame, label=_("Item text:"), title=_("View item"), text=buffer.format_item(index))

 @buffer_defaults
 def Interact(self, buffer=None, index=None):
  """Perform the default action with the item focused in the current buffer."""
  if not hasattr(buffer, 'interact'):
   return output.speak(_("Interaction is not enabled in this buffer."), True)
  buffer.interact(index)

 def buffer (self):
  return self.session.current_buffer

 @buffer_defaults
 def ToggleBufferMute(self, buffer=None):
  """Mutes and unmutes the current buffer."""

  buffer.toggle_buffer_mute()
  buffer.announce_buffer_mute()

interface = BuffersInterface
