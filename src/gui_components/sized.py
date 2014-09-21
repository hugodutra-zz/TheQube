from logging import getLogger
logger = getLogger('gui_components.sized')

import wx
from wx.lib import sized_controls as sc
import controls
__all__ = ['SizedDialog', 'SizedFrame', 'SizedPanel']


LABELED_CONTROLS = (wx.Button, wx.CheckBox, wx.Panel) #Controls that have their own labels
UNFOCUSABLE_CONTROLS = (wx.StaticText, wx.Gauge, wx.Panel)
CALLBACK_TYPES = {
 wx.Button: wx.EVT_BUTTON,
 wx.CheckBox: wx.EVT_CHECKBOX,
 wx.CheckListBox: wx.EVT_CHECKLISTBOX,
 wx.ScrollBar: wx.EVT_SCROLLBAR,
 wx.Slider: wx.EVT_SLIDER,
 controls.VerticalSlider: wx.EVT_SLIDER,
 wx.ListView: wx.EVT_LIST_ITEM_ACTIVATED,
 wx.RadioBox: wx.EVT_RADIOBOX,
}


def do_fit(instance):
 "a generic function that several classes use."""
 instance.Fit()
 instance.SetMinSize(instance.GetSize())
 instance.Center()


class SizedPanel(sc.SizedPanel):
 LABEL_TYPES = (wx.StaticText,)
 
 def __init__(self, *args, **kwargs):
  super(SizedPanel, self).__init__(*args, **kwargs)
  self.row = 0
  self.column = 0
  self.sizerType = "form"
  self._SetNewSizer(wx.GridBagSizer(4, 4))

 def AddChild(self, child):
  wx.PyPanel.AddChild(self, child)
  span = (1, 1)
  position = (self.row, self.column)
  if isinstance(child, self.LABEL_TYPES):
   self.column = 1
  else:
   if self.column == 0:
    span = (1, 2)
   else:
    self.column = 0
   self.row += 1
  sizer = self.GetSizer()
  if isinstance(sizer, wx.GridBagSizer):
   sizer.Add(child, position, span=span)
  else:
   sizer.Add(child)

 do_fit = do_fit

class SizedMixin(object):
 default_size_percent = 20 #Amount of the display

 def __init__(self, parent=None, size=None, *args, **kwargs):
  if size is None:
   size = get_display_dimensions_by_percentage(self.default_size_percent)
  self.SetSize(size)
  if hasattr(parent, 'Raise'):
   parent.Raise()
  self.Raise()
  self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
  self.borderLen = 12
  self.mainPanel = SizedPanel(self, -1)
  root_sizer = wx.BoxSizer(wx.VERTICAL)
  root_sizer.Add(self.mainPanel, 1, wx.EXPAND | wx.ALL)
  self.SetSizer(root_sizer)
  self.SetAutoLayout(True)
  self.pane = self.GetContentsPane()


 def finish_setup (self, set_focus=True):
  """Called once all controls have been setup."""
  if set_focus:
   self.set_default_focus()
  self.do_fit()

 do_fit = do_fit
 

class SizedDialog(SizedMixin, sc.SizedDialog):

 def __init__(self, parent=None, id=wx.ID_ANY, *args, **kwargs):
  wx.Dialog.__init__(self, parent=parent, id=id, *args, **kwargs)
  SizedMixin.__init__(self, *args, **kwargs)
  self.SetLayoutAdaptationMode(wx.DIALOG_ADAPTATION_MODE_ENABLED)
  self.EnableLayoutAdaptation(True)

 def finish_setup (self, create_buttons=True, *args, **kwargs):
  """Called once all controls have been setup.
  If create_buttons is true, will add standard ok/cancel  buttons.  """
  if create_buttons:
   self.create_buttons()
  super(SizedDialog, self).finish_setup(*args, **kwargs)

 def create_buttons (self):
  #Adds standard ok and cancel buttons in their own sizer.
  self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL))
  self.SetEscapeId(wx.ID_CANCEL)


class SizedFrame(SizedMixin, sc.SizedFrame):
 default_size_percent = 30

 def __init__(self, parent=None, id=wx.ID_ANY, *args, **kwargs):
  wx.Frame.__init__(self, parent=parent, id=id, *args, **kwargs)
  SizedMixin.__init__(self, *args, **kwargs)


###Generic functions used by all custom sized Widgets

def create_control(instance, control, parent=None, callback=None, _expand=True, skip_event=True, *args, **kwargs):
 parent = determine_parent(instance, parent)
 new_control = control(parent=parent, *args, **kwargs)
 if callback is not None:
  new_callback = callback   
  if skip_event:
   def new_callback(evt, *args, **kwargs):
    evt.Skip()
    return callback(*args, **kwargs)
  def final_callback(*args, **kwargs):
   try:
    new_callback(*args, **kwargs)
   except:
    logger.exception("Error in GUI callback %r" % callback)
    raise
  new_control.Bind(callback_event_type(control), final_callback)
 if _expand and not isinstance(instance, SizedPanel):
  new_control.SetSizerProps(expand=True)
 return new_control

def callback_event_type(control):
 for k, v in CALLBACK_TYPES.iteritems():
  if control is k:
   return v
  elif issubclass(control, k):
   return v  
 raise NotImplementedError('Unknown callback event type for %r' % control)
  
def labeled_control(instance, label, control, parent=None, *args, **kwargs):
 """ Create a control which has an associated label.  
  The label is hidden and shown when the control is hidden or shown, as well as   when   it is disabled and enabled, respectively. """

 ###Replacement methods for controls.
 def Hide(cls, *a, **k):
  if hasattr(cls, 'label'):
   cls.label.Hide(*a, **k)
  super(type(cls), cls).Hide(*a, **k)
 def Show(cls, *a, **k):
  if hasattr(cls, 'label'):
   cls.label.Show(*a, **k)
  super(type(cls), cls).Show(*a, **k)
 def Disable(cls, *a, **k):
  if hasattr(cls, 'label'):
   cls.label.Hide()
  super(type(cls), cls).Disable(*a, **k)
 def Enable(cls, *a, **k):
  if hasattr(cls, 'label'):
   cls.label.Show(True)
  super(type(cls), cls).Enable(*a, **k)

 if control in LABELED_CONTROLS:
  return instance.create_control(control, parent=parent, label=label, *args, **kwargs)
 parent = determine_parent(instance, parent)
 control.Hide = Hide
 control.Show = Show
 control.Disable = Disable
 control.Enable = Enable
 new_label = wx.StaticText(parent=parent, label=label)
 new_control = instance.create_control(control, parent=parent, *args, **kwargs)
 new_control.label = new_label
 return new_control

def focusable_controls(instance):
 """A generator which yields controls which can be safely-focused"""
 for i in instance.pane.GetChildren():
  if hasattr(i, "focusable_controls"):
   for focusable in i.focusable_controls():
    yield focusable
  if not isinstance(i, UNFOCUSABLE_CONTROLS):
   yield i

def set_default_focus(instance):
 """Set focus to the first really focusable control in this dialog"""
 instance.focusable_controls().next().SetFocus()

def _patch_classes(func):
 for c in SizedPanel, SizedDialog, SizedFrame:
  setattr(c, func.func_name, func)

def determine_parent(instance, parent=None):
 if parent is not None:
  return parent
 try:  
  parent = instance.pane
 except AttributeError:
  parent = instance
 return parent

_patch_classes(create_control)
_patch_classes(labeled_control)
_patch_classes(set_default_focus)
_patch_classes(focusable_controls)
def get_display_dimensions_by_percentage(percentage):
 percentage *= 0.01
 return [int(i * percentage) for i in wx.Display().GetGeometry()[-2:]]
