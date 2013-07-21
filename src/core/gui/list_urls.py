from logger import logger
logging = logger.getChild('core.gui.list_urls')

import misc
import output
import sessions
import url_shortener
import wx

from core.gui import SquareDialog

class ListURLsDialog (SquareDialog):

 def __init__(self, urls=[], *args, **kwargs):
  super(ListURLsDialog, self).__init__(title=_("URL Selection"), *args, **kwargs)
  if not urls:
   urls = [""]
  self.no_shorten = []
  self.urls_list = self.labeled_control(_("Select URL to open"), wx.ListBox, choices=urls, style = wx.LB_SINGLE)
  self.urls_list.SetSelection(0)
  self.urls_list.Bind(wx.EVT_LISTBOX, self.change_selection)
  self.btn_unshorten = self.labeled_control(control=wx.Button, label=_("&Unshorten URL"))
  self.btn_unshorten.Bind(wx.EVT_BUTTON, self.unshorten_click)
  self.set_unshorten_button_status()
  self.btn_copy = self.labeled_control(control=wx.Button, label=_("&Copy URL"))
  self.btn_copy.Bind(wx.EVT_BUTTON, self.onCopy)
  self.finish_setup()

 def change_selection(self, evt):
  evt.Skip()
  self.set_unshorten_button_status()

 def unshorten_click(self, evt):
  evt.Skip()
  self.btn_unshorten.Disable()
  show_error_dialog = False
  url = self.urls_list.GetStringSelection()
  i = self.urls_list.GetSelection()
  try:
   unshortened = url_shortener.unshorten_any(url)
  except:
   logging.exception("Error in unshortening URL:  %s" % url)
   self.btn_unshorten.Enable()
   unshortened = url
   show_error_dialog = True
  try:
   self.urls_list.SetString(i, unshortened)
   self.no_shorten.append(unshortened)
   output.speak(_("URL expanded."))
  except:
   logging.debug("Error in unshortened URL:  %s" % unshortened)
   output.speak(_("Unable to expand URL"))
   self.btn_unshorten.Enable()
  self.Fit()
  self.urls_list.SetFocus()

 def set_unshorten_button_status(self):
  url = self.urls_list.GetStringSelection()
  if url not in self.no_shorten and not url.startswith('@'):
   self.btn_unshorten.Enable()
  else:
   self.btn_unshorten.Disable()

 def onCopy (self, evt):
  evt.Skip()
  output.Copy(self.urls_list.GetStringSelection().replace("@","http://www.twitter.com/"))
  output.speak(_("URL copied to clipboard."), 1)
