# -*- coding: utf-8 -*-

# TheQube New Message dialog
# A part of TheQube accessible social networking client
# Copyright © Andre Polykanine A.K.A. Menelion Elensúlë, 2014

from logger import logger
logging = logger.getChild('core.gui.new_message')

import config
import json
import misc
import url_shortener
import sessions
import output
import wx
import wx.lib.sized_controls as sc

from core.transfer_dialogs import UploadDialog

from core.gui import SquareDialog
from recording import RecordingDialog
from schedule import ScheduleDialog
from translate import TranslateDialog


class NewMessageDialog(SquareDialog):

 def __init__ (self, title="", max_length=0, *args, **kwargs):
  self.base_title = title
  self.max_length = max_length
  super(NewMessageDialog, self).__init__(*args, title=title, **kwargs)

 def textUpdated(self, evt):
  try:
   evt.Skip()
   self.Fit()
   self.update_title()
   length = self.getMessageLength()
   if hasattr(sessions.current_session, 'play'):
    if length > self.max_length:
     sessions.current_session.play(sessions.current_session.config['sounds']['maxLength'])
   # Only enable the shorten button and unshorten button if there is text.
   self.update_url_buttons()
  except Exception as tuexc:
   logging.exception("Error updating text: {0}".format(tuexc))

 def update_url_buttons (self):
  if hasattr(self, 'shorten') and hasattr(self,'unshorten'):
   if misc.find_urls(self.message.GetValue()):
    self.shorten.Enable()
    self.unshorten.Enable()
   else:
    self.shorten.Disable()
    self.unshorten.Disable()

 def update_title (self):
  length = self.getMessageLength()
  self.SetTitle(_("%s - %d of %d Characters") % (self.base_title, length, self.max_length))

 def GetURLList(self):
  urls = []
  tweet = self.message.GetValue()
  # If there is a reasonable selection of no more than 1 word, add it to the urls list.
  # selecting sometimes includes prior or subsequent spaces; remove.
  sel = self.message.GetStringSelection().strip()
  logging.debug("len sel: %s, len tweet: %s, sel: %s, tweet: %s" % (len(sel), len(tweet), sel, tweet))
  # useful selection, not multi-word
  if len(sel) > 3 and " " not in sel:
   logging.debug("Adding selection as URL: %s" % (sel))
   urls.append(sel)
  # Find URLs from tweet.
  urls.extend(misc.find_urls(tweet))
  return urls

 def shorten_click (self, evt):
  logging.debug("URL Shorten button activated.")
  urls = self.GetURLList()
  if not urls:
   logging.debug("No URLs found in tweet. Nothing to shorten.")
   dlg_title = _('URL Shortener - No URLs')
   dlg_text = _('No URLs were found to shorten. If there is one, select the URL and click this button again.')
   dlg = wx.MessageDialog(self, dlg_text, dlg_title, wx.OK |  wx.ICON_INFORMATION)
   dlg.ShowModal()
   dlg.Destroy()
   # Set focus to the edit field by default
   self.message.SetFocus()
   #Deselect any current text.
   self.message.SetSelection(len(self.message.GetValue()),len(self.message.GetValue()))
   return 0
  logging.debug("Found at least 1 URL. Showing selection dialog.")
  if len(urls) == 1:
   url=urls[0]
  else:
   # Adapted from interface.py.
   dlg_title = _('URL Shortener - Select URL')
   dlg_text = _('Select URL to shorten.')
   dlg = wx.SingleChoiceDialog(None, dlg_title, dlg_text, urls, wx.CHOICEDLG_STYLE)
   dlg.Raise()
   if dlg.ShowModal() == wx.ID_OK:
    url = dlg.GetStringSelection()
  logging.debug("User selected URL to shorten: %s" % (url))
  clean = misc.url_cleanup(url)
  logging.debug("Clean URL (what will be replaced) is: %s" % (clean))
  surl = clean # URL to shorten
  if "://" not in surl:
   surl = "http://" + surl
  logging.debug("URL sent to shortener: %s" % (surl))
  short = url_shortener.shorten(surl, service=config.main['shortener']['urlShortener'])
  if short:
   logging.debug("Started with %s, will replace %s, shortening %s, shortened as %s" % (url, clean, surl, short))
   self.message.SetValue(self.message.GetValue().replace(clean, short))
   output.speak(_("URL Shortened."), True)
  else:
   logging.debug("Shorten failed: started with %s, will replace %s, tried shortening %s" % (url, clean, surl))
   dlg_title = _('URL Shortener - Problem')
   dlg_text = _('There was a problem shortening the selected URL.')
   dlg = wx.MessageDialog(self, dlg_text, dlg_title, wx.OK |   wx.ICON_INFORMATION)
   dlg.ShowModal()
   dlg.Destroy()
#Set focus to the edit field by default
  self.message.SetFocus()
#Deselect any current text.
  self.message.SetSelection(len(self.message.GetValue()),len(self.message.GetValue()))

 def unshorten_click (self, evt):
  logging.debug("URL Unshorten button activated.")
  urls = self.GetURLList()
  if not urls:
   logging.debug("No URLs found in tweet. Nothing to unshorten.")
   dlg_title = _('URL Unshortener - No URLs')
   dlg_text = _('No URLs were found to unshorten. If there is one, select the URL and click this button again.')
   dlg = wx.MessageDialog(self, dlg_text, dlg_title, wx.OK |  wx.ICON_INFORMATION)
   dlg.ShowModal()
   dlg.Destroy()
   # Set focus to the edit field by default
   self.message.SetFocus()
   #Deselect any current text.
   self.message.SetSelection(len(self.message.GetValue()),len(self.message.GetValue()))
   return 0
  logging.debug("Found at least 1 URL. Showing selection dialog.")
  if len(urls) == 1:
   url=urls[0]
  else:
   # Adapted from interface.py.
   dlg_title = _('URL Unshortener - Select URL')
   dlg_text = _('Select URL to unshorten.')
   dlg = wx.SingleChoiceDialog(None, dlg_title, dlg_text, urls, wx.CHOICEDLG_STYLE)
   dlg.Raise()
   if dlg.ShowModal() == wx.ID_OK:
    url = dlg.GetStringSelection()
  logging.debug("User selected URL to unshorten: %s" % (url))
  clean = misc.url_cleanup(url)
  logging.debug("Clean URL (what will be replaced) is: %s" % (clean))
  surl = clean # URL to unshorten
  if "://" not in surl:
   surl = "http://" + surl
  logging.debug("URL being unshortened: %s" % (surl))
  try:
   unshortened = url_shortener.unshorten(surl)
  except:
   logging.exception("Error in unshortening URL:  %s" % surl)
   unshortened = None
  if unshortened:
   logging.debug("Started with %s, will replace %s, unshortening %s, unshortened as %s" % (url, clean, surl, unshortened))
   self.message.SetValue(self.message.GetValue().replace(clean, unshortened))
   output.speak(_("URL expanded."), True)
  else:
   logging.debug("Unshorten failed: started with %s, will replace %s, tried unshortening %s" % (url, clean, surl))
   dlg_title = _('URL Unshortener - Problem')
   dlg_text = _('There was a problem unshortening the selected URL.')
   dlg = wx.MessageDialog(self, dlg_text, dlg_title, wx.OK |   wx.ICON_INFORMATION)
   dlg.ShowModal()
   dlg.Destroy()
  #Set focus to the edit field by default
  self.message.SetFocus()
  #Deselect any current text.
  self.message.SetSelection(self.getMessageLength(), self.getMessageLength())

 def getMessageLength(self):
  return len(self.message.GetValue())

 def charPressed(self, evt):
  object = evt.GetEventObject()
  key = evt.GetKeyCode()
  modifiers = evt.GetModifiers()
  if config.main['UI']['stdKeyHandling'] and key in (wx.WXK_END, wx.WXK_HOME):
   evt.Skip()
  elif key == wx.WXK_HOME and not modifiers:
   object.SetInsertionPoint(0)
  elif key == wx.WXK_END and not modifiers:
   object.SetInsertionPointEnd()
  elif key == wx.WXK_HOME and modifiers == wx.MOD_SHIFT:
   object.SetSelection(object.GetInsertionPoint(), 0)
  elif key == wx.WXK_END and modifiers == wx.MOD_SHIFT:
   object.SetSelection(object.GetInsertionPoint(), len(object.GetValue()))
  elif key == 1 and modifiers == wx.MOD_CONTROL:
   object.SetInsertionPoint(0)
   object.SetSelection(0, len(object.GetValue()))
  elif key == wx.WXK_RETURN:
   if config.main['UI']['sendMessagesWithEnterKey']:
    evt.Skip()
    self.EndModal(wx.ID_OK)
   else:
    evt.Skip()
  elif key == 13 and modifiers == wx.MOD_CONTROL:
   if not config.main['UI']['sendMessagesWithEnterKey']:
    evt.Skip()
    self.EndModal(wx.ID_OK)
  else:
   evt.Skip()

 def finish_setup (self, *args, **kwargs):
  self.button_panel = sc.SizedPanel(self.pane, -1)
  self.button_panel.SetSizerType("horizontal")
  self.setup_attachment()
  self.setup_translation()
  self.setup_url_shortener_buttons()
  self.setup_schedule()
  self.update_title()
  super(NewMessageDialog, self).finish_setup(*args, **kwargs)

 def setup_message_field(self, text=""):
  self.message = self.labeled_control(_("Message:"), wx.TextCtrl, style=wx.TE_MULTILINE|wx.PROCESS_ENTER|wx.TE_RICH2|wx.WANTS_CHARS, size=(400, -1))
  self.message.Bind(wx.EVT_CHAR, self.charPressed)
  self.message.Bind(wx.EVT_TEXT, self.textUpdated)
  self.message.SetSizerProps(expand=True)
  self.message.SetValue(text)
  #Deselect any current text.
  self.message.SetSelection(len(self.message.GetValue()),len(self.message.GetValue()))


 def setup_url_shortener_buttons (self):
  logging.debug("Setting up URL buttons.")
  self.shorten = wx.Button(parent=self.button_panel, label=_("&Shorten URL"))
  self.shorten.Bind(wx.EVT_BUTTON, self.shorten_click, self.shorten)
  self.unshorten = wx.Button(parent=self.button_panel, label=_("&Unshorten URL"))
  self.unshorten.Bind(wx.EVT_BUTTON, self.unshorten_click, self.unshorten)

 def setup_attachment(self):
  self.attach_audio = wx.Button(parent=self.button_panel, label=_("Attach &Audio..."))
  self.attach_audio.Bind(wx.EVT_BUTTON, self.on_attach_audio)

 def setup_schedule(self):
  self.delay = 0
  self.schedule_message = self.labeled_control(parent=self.button_panel, label=_("S&chedule message..."), control=wx.Button, callback=self.on_schedule_message)

 def on_attach_audio(self, evt):
  evt.Skip()
  self.recording_dlg = dlg = RecordingDialog(parent=self.pane.Parent)
  if dlg.ShowModal() != wx.ID_OK:
   dlg.cleanup()
   return output.speak(_("Canceled."), True)
  try:
   dlg.postprocess()
   output.speak(_("Attaching..."), True)
   baseUrl = 'http://api.twup.me/post.json' if config.main['AudioServices']['service'] == 'twup.me' else 'http://sndup.net/post.php'
   if config.main['AudioServices']['service'] == 'sndup.net' and len(config.main['AudioServices']['sndUpAPIKey']) > 0:
    upload_url = baseUrl + '?apikey=' + config.main['AudioServices']['sndUpAPIKey']
   else:
    upload_url = baseUrl
   logging.debug("Upload URL: %s" % upload_url)
   self.upload_dlg = UploadDialog(parent=self, title=_("Upload in progress"), field='file', url=upload_url, filename=dlg.file, completed_callback=self.upload_completed)
   logging.debug("@Upload dialog: %s" % str(self.upload_dlg))
   self.upload_dlg.Show(True)
   try:
    self.upload_dlg.perform_threaded()
   except Exception as upldexc:
    logging.exception("Unable to perform upload: %s " % upldexc)
  except Exception as auexc:
   logging.exception("Unable to upload audio file to %s: %s" % (config.main['AudioServices']['service'], auexc))
   dlg.cleanup()
   return output.speak(_("There was an error attaching the file."), True)

 def upload_completed(self):
  url = json.loads(self.upload_dlg.response['body'])['url']
  logging.debug("Gotten URL: %s" % url)
  self.upload_dlg.Destroy()
  self.recording_dlg.cleanup()
  self.recording_dlg.Destroy()
  if url != 0:
   self.message.SetValue('%s %s #audio' % (self.message.GetValue(), url))
   output.speak(_("File attached."), True)
   self.message.SetFocus()
  else:
   error = json.loads(self.upload_dlg.response['body'])['error']
   logging.exception("Error getting URL to audio. Server response: {0}". format(error))
   output.speak(_(error), True)
   self.message.SetFocus()
  
 def on_schedule_message(self):
  if self.delay:
   output.speak(_("Resetting currently scheduled item."), True)
  dlg = ScheduleDialog(parent=self, title=_("Schedule message"))
  if dlg.ShowModal() != wx.ID_OK:
   return output.speak(_("Canceled."), True)
  self.delay = dlg.get_time()
  output.speak(_("Delaying for %s") % misc.SecondsToString(self.delay), True)
  self.message.SetFocus()

 def setup_translation(self):
  self.translate_message = wx.Button(parent=self.button_panel, label=_("&Translate Message..."))
  self.translate_message.Bind(wx.EVT_BUTTON, self.on_translate_message)

 def on_translate_message(self, evt):
  evt.Skip()
  dlg = TranslateDialog(parent=self.pane.Parent, title=_("Translate message"))
  if dlg.ShowModal() != wx.ID_OK:
   return output.speak(_("Canceled."), True)
  text_to_translate = self.message.GetValue().encode("UTF-8")
  source = dlg.langs_keys[dlg.source_lang_list.GetSelection()]
  target = dlg.langs_keys[dlg.target_lang_list.GetSelection()]
  try:
   translated_text = dlg.t.translate(text_to_translate, target, source)
  except Exception as e:
   logging.exception("Translation error: {0}".format(e))
   output.speak(_("Translation process has failed."), True)
  self.message.SetValue(translated_text)
  self.message.SetFocus()
  self.message.SetSelection(len(self.message.GetValue()),len(self.message.GetValue()))
