# -*- coding: utf-8 -*-

from core.sessions.hotkey.gui.main import KeymapDialog
import global_vars
import output
import wx
from utils.wx_utils import modal_dialog, always_call_after

from core.sessions.interface.interface import Interface

class HotkeyInterface (Interface):

 def ChangeKeymap(self):
  """Allows you to change the keystrokes used to control TheQube."""

  @always_call_after
  def replace_keymap(new):
   self.session.unregister_hotkeys()
   self.session.keymap.clear()
   self.session.keymap.update(new)
   self.session.set_active_keymap(self.session.keymap)
   self.session.save_config()
   output.speak(_("Keymap saved."), True)

  dlg = modal_dialog(KeymapDialog, parent=self.session.frame)
  replace_keymap(dlg.new_keymap)

 def ToggleKeyboardHelp(self):
  if not global_vars.KeyboardHelp:
   output.speak(_("Keyboard help on."), True)
  else:
   output.speak(_("Keyboard help off."), True)
  global_vars.KeyboardHelp = not global_vars.KeyboardHelp

 def ToggleModifierLock(self):
  if self.session.modifiers_locked:
   self.session.unlock_modifiers()
   output.speak(_("Modifiers unlocked."), True)
  else:
   self.session.lock_modifiers()
   output.speak(_("Modifiers locked."), True)


interface = HotkeyInterface
