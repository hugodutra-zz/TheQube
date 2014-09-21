#gui_components Menu
#Making it easier than using the really awful wx.Menu, etc, etc

import wx

class MenuBar(object):
 def __init__(self, frame, *args, **kwargs):
  self.menu_bar = wx.MenuBar()
  self.frame = frame
  for x in args:
   setattr(self, mangle_name(x.title.encode('utf-8')), x)
   setattr(x, 'wx_obj', x.menu)
   self.menu_bar.Append(x.menu, x.title)
   for item in x.menu_items:
    if isinstance(item, MenuItem):
     frame.Bind(wx.EVT_MENU, item.callback, item.wx_obj)
    #Sub-menu's
    if isinstance(item, Submenu):
     for mitem in item.menu_items:
      frame.Bind(wx.EVT_MENU, mitem.callback, mitem.wx_obj)

  frame.SetMenuBar(self.menu_bar)
  


class Menu(object):

 def __init__(self, title, *args):
  self.menu = wx.Menu()
  self.title = title
  self.menu_items = args
  for x in args:
   if x is not None and isinstance(x, MenuItem):
    self.menu.Append(x.id, x.title)
    menu_item = wx.MenuItem(self.menu, x.id, x.title)
    menu_item.Enable(x.enabled)
    setattr(x, 'wx_obj', menu_item)
    setattr(self, mangle_name(x.title.encode('utf-8')), x)
   elif x is not None and isinstance(x, Submenu):
    for looper in x.menu_items:
     menu_item = wx.MenuItem(self.menu, looper.id, looper.title)
     setattr(looper, 'wx_obj', menu_item)
    self.menu.AppendSubMenu(x.menu, x.title)
    setattr(self, mangle_name(x.title.encode('utf-8')), x)
   else:
    self.menu.AppendSeparator()
  

class MenuItem(object):

 def __init__(self, title, callback=None, hotkey=None, enabled=True, skip_event=True):
  self.title = title
  if hotkey is not None:
   #Instead of accel. tables, using a \t trick found on wiki.wxpython.org/SmallApp
   self.title = self.title + "\t" + hotkey
  self.enabled = enabled
  if skip_event:  
   def new_callback(evt):
    evt.Skip()
    callback()
  else:
   new_callback = callback
  self.callback = new_callback
  self.id = wx.NewId()


class Submenu(object):
 
 def __init__(self, title, *args):
  self.menu = wx.Menu()
  self.title = title
  self.menu_items = args
  for x in args:
   if x is not None:
    self.menu.Append(x.id, x.title)
    setattr(self, mangle_name(x.title.encode('utf-8')), x)
   else:
    self.menu.AppendSeparator()

def mangle_name(name):
 if name.find('\t') != -1:
  name = name[:name.index('\t')]
 name = name.replace('&', '')
 name = name.lower()
 name = name.replace(' ', '_')
 name = name.replace('.', '')
 return name
