# -*- coding: utf-8 -*-

import pycurl
import sys
import threading
import time
import wx
import os
from gui_components.sized import SizedDialog
from logger import logger
logging = logger.getChild('transfer_dialogs')

__all__ = ['TransferDialog', 'DownloadDialog', 'UploadDialog']

class TransferDialog(SizedDialog):

 def __init__(self, url=None, filename=None, follow_location=True, completed_callback=None, verbose=False, *args, **kwargs):
  self.url = url
  self.filename =  filename
  self.curl = pycurl.Curl()
  self.start_time = None
  self.completed_callback = completed_callback
  self.background_thread = None
  self.transfer_rate = 0
  self.curl.setopt(self.curl.PROGRESSFUNCTION, self.progress_callback)
  try:
   self.curl.setopt(self.curl.URL, url)
  except:
   logging.exception("URL error: %s" % self.curl.errstr())
  self.curl.setopt(self.curl.NOPROGRESS, 0)
  self.curl.setopt(self.curl.HTTP_VERSION, self.curl.CURL_HTTP_VERSION_1_0)
  self.curl.setopt(self.curl.FOLLOWLOCATION, int(follow_location))
  self.curl.setopt(self.curl.VERBOSE, int(verbose))
  super(TransferDialog, self).__init__(*args, **kwargs)
  self.progress_bar = wx.Gauge(parent=self.pane)
  self.file = self.labeled_control("Filename:", wx.TextCtrl, value=filename, style=wx.TE_READONLY|wx.TE_MULTILINE, size=(200, 100))
  self.current_amount = self.labeled_control("Currently transfered:", wx.TextCtrl, value='0', style=wx.TE_READONLY|wx.TE_MULTILINE)
  self.total_size = self.labeled_control("Total file size:", wx.TextCtrl, value='0', style=wx.TE_READONLY|wx.TE_MULTILINE)
  self.speed = self.labeled_control("Transfer rate:", wx.TextCtrl, style=wx.TE_READONLY|wx.TE_MULTILINE, value="0 Kb/s")
  self.eta = self.labeled_control("ETA:", wx.TextCtrl, style=wx.TE_READONLY|wx.TE_MULTILINE, value="Unknown", size=(200, 100))
  self.finish_setup()#create_buttons=False)

 def elapsed_time(self):
  if not self.start_time:
   return 0
  return time.time() - self.start_time

 def progress_callback(self, down_total, down_current, up_total, up_current):
  if down_total:
   total, current = down_total, down_current
  elif up_total:
   total, current = up_total, up_current
  else:
   return
  self.transfer_rate = current / self.elapsed_time()
  percent = int((float(current) / total) * 100)
  speed = '%s/s' % convert_bytes(self.transfer_rate)
  if self.transfer_rate:
   ETA = (total - current) / self.transfer_rate
  else:
   ETA = 0
  wx.CallAfter(self.progress_bar.SetValue, percent)
  wx.CallAfter(self.current_amount.SetValue, '%s (%d%%)' % (convert_bytes(current), percent))
  wx.CallAfter(self.total_size.SetValue, convert_bytes(total))
  wx.CallAfter(self.speed.SetValue, speed)
  if ETA:
   wx.CallAfter(self.eta.SetValue, seconds_to_string(ETA))

 def perform_transfer(self):
  self.start_time = time.time()
  try:
   self.curl.perform()
  except:
   logging.exception("CURL error: %s" % self.curl.errstr())
  self.curl.close()
  wx.CallAfter(self.complete_transfer)

 def perform_threaded(self):
  self.background_thread = threading.Thread(target=self.perform_transfer)
  self.background_thread.daemon = True
  self.background_thread.start()

 def complete_transfer(self):
  if callable(self.completed_callback):
   self.completed_callback()

 def create_buttons(self):
  self.cancel_button = wx.Button(parent=self.pane, id=wx.ID_CANCEL)
  self.cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel)

 def on_cancel(self, evt):
  evt.Skip()
  self.curl.close()


class UploadDialog(TransferDialog):

 def __init__(self, field=None, filename=None, *args, **kwargs):
  super(UploadDialog, self).__init__(filename=filename, *args, **kwargs)
  self.response = dict()
  self.curl.setopt(self.curl.POST, 1)
  if isinstance(filename, unicode):
   local_filename = filename.encode(sys.getfilesystemencoding())
  else:
   local_filename = filename
  self.curl.setopt(self.curl.HTTPPOST, [(field, (self.curl.FORM_FILE, local_filename, self.curl.FORM_FILENAME, filename.encode("utf-8")))])
  self.curl.setopt(self.curl.HEADERFUNCTION, self.header_callback)
  self.curl.setopt(self.curl.WRITEFUNCTION, self.body_callback)

 def header_callback(self, content):
  self.response['header'] = content

 def body_callback(self, content):
  self.response['body'] = content

class DownloadDialog(TransferDialog):

 def __init__(self, follow_location=True, *args, **kwargs):
  super(DownloadDialog, self).__init__(*args, **kwargs)
  self.download_file = open(self.filename, 'wb')
  self.curl.setopt(self.curl.WRITEFUNCTION, self.download_file.write)

 def complete_transfer(self):
  self.download_file.close()
  super(DownloadDialog, self).complete_transfer()


def convert_bytes(n):
 K, M, G, T, P = 1 << 10, 1 << 20, 1 << 30, 1 << 40, 1 << 50
 if   n >= P:
  return '%.2fPb' % (float(n) / T)
 elif   n >= T:
  return '%.2fTb' % (float(n) / T)
 elif n >= G:
  return '%.2fGb' % (float(n) / G)
 elif n >= M:
  return '%.2fMb' % (float(n) / M)
 elif n >= K:
  return '%.2fKb' % (float(n) / K)
 else:
  return '%d' % n

def seconds_to_string(seconds, precision=0):
 day = seconds // 86400
 hour = seconds // 3600
 min = (seconds // 60) % 60
 sec = seconds - (hour * 3600) - (min * 60)
 sec_spec = "." + str(precision) + "f"
 sec_string = sec.__format__(sec_spec)
 string = ""
 if day == 1:
  string += "%d day, " % day
 elif day >= 2:
  string += "%d days, " % day
 if (hour == 1):
  string += "%d hour, " % hour
 elif (hour >= 2):
  string += "%d hours, " % hour
 if (min == 1):
  string += "%d minute, " % min
 elif (min >= 2):
  string += "%d minutes, " % min
 if sec >= 0 and sec <= 2:
  string += "%s second" % sec_string
 else:
  string += "%s seconds" % sec_string
 return string

