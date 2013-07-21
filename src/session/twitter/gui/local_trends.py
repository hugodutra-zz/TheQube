from logger import logger
logging = logger.getChild("sessions.twitter.gui.local_trends")

import output
import sessions
import wx

from core.gui import SquareDialog

class LocalTrendsDialog (SquareDialog):

 def __init__(self, locations_tree={}, *args, **kwargs):
  self.locations_tree = locations_tree
  logging.debug("Locations tree: %s" % str(self.locations_tree))
  self.location_types = sorted(locations_tree.keys())
  super(LocalTrendsDialog, self).__init__(title=_("Location Selection"), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, *args, **kwargs)
  #First Row
  self.location_type = wx.RadioBox(self.pane, -1, _("Select type of location:"), wx.DefaultPosition, wx.DefaultSize, self.location_types)
  self.location_type.Bind(wx.EVT_RADIOBOX, self.change_type)
  self.locations_list = self.labeled_control(_("Select location:"), wx.ListBox, choices=locations_tree[self.location_type.GetStringSelection()], style = wx.LB_SINGLE)
  self.locations_list.Bind(wx.EVT_SET_FOCUS, self.locations_list_on_focus)
  self.locations_list.SetSizerProps(expand=True)
  self.finish_setup()

 def change_type(self, evt):
  evt.Skip()
  self.locations_list.SetItems(self.locations_tree[self.location_type.GetStringSelection()])
  self.Fit()

 def locations_list_on_focus(self, evt):
  evt.Skip()
  if self.locations_list.GetSelection() == wx.NOT_FOUND:
   self.locations_list.SetSelection(0)
