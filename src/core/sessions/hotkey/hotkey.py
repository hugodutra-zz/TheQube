# -*- coding: utf-8 -*-

from logger import logger
logging = logger.getChild('core.sessions.hotkey')

import application
from keyboard_handler.wx_handler import WXKeyboardHandler
from functools import partial, update_wrapper
import config as configuration
import global_vars
import output
from utils.wx_utils import WXDialogCanceled, always_call_after

from core.sessions.interface.main import Interface
from core.sessions.gui.gui import Gui
from core.sessions.configuration.configuration import Configuration

class Hotkey (Configuration, Interface, Gui):
 """A generic session providing global hotkey support"""

 def __init__(self, keymap={}, *args, **kwargs):
  super(Hotkey, self).__init__(*args, **kwargs)
  if 'keymap' not in self.config:
   self.config['keymap'] = dict()
  self.keymap = self.config['keymap']
  #Load any keys passed in.
  self.update_dict(self.keymap, keymap)
  #Load default app-wide keystrokes.
  self.update_dict(self.keymap, configuration.main['keymap'])
  self.keyboard_handler = WXKeyboardHandler(application.main_frame)  
  new = self.keyboard_handler.standardize_keymap(self.keymap)
  self.keymap.clear()
  self.keymap.update(new)
  self.active_keymap = dict()
  self.replaced_keys = {}
  self.modifiers_locked = False

 def activate(self):
  if self.active: return
  self.set_active_keymap(self.keymap)
  super(Hotkey, self).activate()

 def deactivate (self):
  self.unlock_modifiers()
  self.unregister_hotkeys()
  super(Hotkey, self).deactivate()

 def set_active_keymap(self, keymap):
  working = dict(keymap)
  keymap = {}
  for func in working:
   try:
    function = self._find_interface_function(func)
   except NotImplementedError:
    continue
   key = working[func]
   keymap[key] = function
  self.register_hotkeys(keymap)

 @always_call_after
 def register_hotkeys(self, keymap):
  self.keyboard_handler.register_keys(keymap)
  self.active_keymap = keymap

 def _find_interface_function(self, func):
  function = getattr(self.interface, func, None)
  if function is None:
   raise NotImplementedError
  new_func = partial(self.call_interface_function, function)
  return new_func

 @always_call_after
 def unregister_hotkeys(self):
  self.keyboard_handler.unregister_all_keys()

 def call_interface_function(self, function):
  if not self.active:
   return
  if global_vars.KeyboardHelp:
   try:
    output.speak(function.__doc__)
   finally:
    if function.func_name == "ToggleKeyboardHelp":
     self.execute_interface_function(function)
  else:
   self.execute_interface_function(function)
 
 def execute_interface_function(self, func):
  func()

 def key_description(self, func):
  return getattr(getattr(self.interface, func, None), '__doc__', None)
  
 def replace_active_keymap(self, new_keymap):
  self.unregister_hotkeys()
  self.register_hotkeys(new_keymap)

 def lock_modifiers(self, modifiers='control+win'):
  new_keymap = {}
  if not modifiers.endswith('+'):
   modifiers = '%s+' % modifiers
  for key in self.active_keymap:
   if modifiers in key:
    new_key = key.replace(modifiers, "")
    new_keymap[new_key] = self.active_keymap[key]
   else:
    new_keymap[key] = self.active_keymap[key]
  self.replace_active_keymap(new_keymap)
  self.modifiers_locked = True

 def unlock_modifiers(self):
  self.unregister_hotkeys()
  self.set_active_keymap(self.keymap)
  self.modifiers_locked = False
