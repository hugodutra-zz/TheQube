import logging as original_logging
logging = original_logging.getLogger('core.sessions.buffers.exporter')

import config
import win32com.client
import os

class ExporterObject (object):
 def __init__ (self, format, filename, path, rate, volume, voice):
  self.format = format
  self.filename = filename
  self.path = path
  self.rate = rate
  self.volume = volume
  self.voice = voice
  logging.debug("Created exporter object.  Output path: %s.  Output file: %s in %s format." % (self.path, self.filename, self.format))

 def exportPost (self, buffer, index=None, close=True):
  if not index and index != 0:
   index = buffer.GetIndex()
  post = self.FormatExported(buffer, index)
  if self.format == 'wav':
   return self.writeAudio(post, close)
  else:
   return self.writeExport(post, close)

 def exportBuffer (self, buffer):
  try:
   posts= [ ]
   max = buffer.GetMaxIndex()
   for i in xrange(1, max):
    posts.append(self.FormatExported(buffer, i))
   if self.format == 'wav':
    return self.writeAudio(posts, close)
   else:
    return self.writeExports(posts)
  except:
   logging.exception("Error with mass export.")
   return False

 def exportRange(self, buffer, min=1, max=0):
  try:
   posts = []
   if not max:
    max = buffer.GetMaxIndex()
   for i in xrange(min, max):
    posts.append(self.FormatExported(buffer, i))
   if self.format == 'wav':
    return self.writeAudio(posts, close)
   else:
    return self.writeExports(posts)
  except:
   logging.exception("Error with range export.")
   return False

 def writeExport (self, post, close=True):
  try:
   f=open(os.path.join(self.path, self.filename), 'a')
   f.write(post)
   if close:
    f.close()
   return True
  except:
   logging.exception("Failed to export.")
   return False

 def writeExports (self, posts, close=True):
  try:
   f=open(os.path.join(self.path, self.filename), 'a')
   f.writelines(posts)
   if close:
    f.close()
   return True
  except:
   logging.exception("Failed to export.")
   return False

 def FormatExported (self, buffer, index):
  post = buffer.FormatPost(index)

  #Insert special cases for different formats.
  if self.format == "txt" or self.format == "wav":
   post = "%s\n" % post
  return post

 def writeAudio(self, post, sampling_rate=16, bits=8, channels=2, close=True):
  try:
   tts = win32com.client.Dispatch("SAPI.SPVoice")
   prev_stream = tts.AudioOutputStream.Format.Type
   stream = win32com.client.Dispatch("SAPI.SPFileStream")
   stream.Format.Type = win32com.client.constants('SAFT%dkHz%dBit%s' % (rate, bits, (None, 'Mono', 'Stereo')[channels]))
   stream.open(os.path.join(self.path, self.fileName), win32com.client.constants.SSFMCreateForWrite, True)
   tts.Rate = self.rate
   tts.Volume = self.volume
   #tts.voice = self.voice
   tts.AudioOutputStream = stream
   tts.AllowAudioOutputFormatChangesOnNextSet = False
   tts.speak(post)
   if close:
    stream.close()
   tts.AudioOutputStream = prev_stream
   return True
  except:
   return False

