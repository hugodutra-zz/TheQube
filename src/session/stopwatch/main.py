from logger import logger
logging = logger.getChild('sessions.stopwatch.main')

import output
import time
import buffers
from threading import Timer

from core.sessions.hotkey.hotkey import Hotkey
from core.sessions.buffers import Buffers

class Stopwatch (Hotkey, Buffers):
 """A Qwitter session to provide a few simple stopwatch functions such as timing an event or setting an alarm x minutes into the future."""

 def __init__ (self, *args, **kwargs):
  self.countdowns = list()
  self.timers = list()
  super(Stopwatch, self).__init__(*args, **kwargs)

 def register_default_buffers (self):
  (_("Countdowns"), _("Timers"))
  b = self.register_buffer("Countdowns", buffers.Countdowns, announce=False)
  b = self.register_buffer("Timers", buffers.Timers, announce=False, set_focus=False)
  self.create_stopwatch(_("default"))

 def create_countdown (self, name=None, interval=0):
  if not name:
   name = self._new_name(self.countdowns)
  timer = Countdown(name=name, session=self, total_time=interval)
  self.countdowns.append(timer)
  timer.start()

 def create_stopwatch(self, name=None):
  if not name:
   name = self._new_name(self.timers)
  timer = StopwatchTimer(name=name)
  self.timers.append(timer)

 @staticmethod
 def _new_name (lst):
  name = key = "unnamed"
  suffix = 0
  names = []
  for counter, i in enumerate(lst):
   names.append(lst[counter]['name'])
  while key in names:
   suffix += 1
   key = "%s%s" % (name, suffix)
  return key

 def shutdown (self, *args, **kwargs):
  [i.timer.cancel() for i in self.countdowns]
  [i.stop() for i in self.timers]
  return super(Stopwatch, self).shutdown(*args, **kwargs)

class Countdown(object):
 def __init__ (self, session=None, name=None, start_time=0, total_time=0, sound=None):
  assert(total_time > 0)
  self.session = session
  self.name = name
  self.start_time = start_time or time.time()
  self.sound = sound or self.session.config['sounds']['countdownFinished']
  self.total_time = total_time
  self.timer = Timer(total_time, self.countdown_complete)

 def start (self):
  self.timer.start()

 def cancel (self):
  if self.timer.is_alive:
   self.timer.cancel()
 stop = cancel

 def remaining_time (self):
  return int(self.timer.is_alive()) and self.total_time - (time.time() - self.start_time)

 def countdown_complete (self):
  self.session.countdowns.remove(self)
  output.speak(_("Countdown %s complete.") % self.name, True)
  self.play(self.sound)

class StopwatchTimer(object):
 start_time = None
 stop_time = None
 running = False

 def __init__(self, name=None):
  self.name = name

 def start(self):
  self.start_time = time.time()
  self.running = True

 def reset(self):
  self.start_time = None
  self.stop_time = None
  self.running = False

 def elapsed_time(self):
  if not self.start_time:
   return 0.0
  if self.stop_time:
   return self.stop_time - self.start_time
  return time.time() - self.start_time

 def stop(self):
  self.stop_time = time.time()
  self.running = False
