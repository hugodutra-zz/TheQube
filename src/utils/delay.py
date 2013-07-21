import misc
import output
import threading

delayed = []

def delay(interval, function, premessage=None, postmessage=None, _extra_kwargs=dict(), *args, **kwargs):
 global delayed
 kwargs.update(_extra_kwargs)
 if premessage:
  output.speak(premessage, True)
 current_timer = threading.Timer(interval, function, args, kwargs)
 delayed.append(current_timer)
 current_timer.start()
 return len(delayed)

def delay_action(interval, function, action=None, *args, **kwargs):
 if not action:
  action = _("action")
 output.speak(_("Delaying %s for %s.") % (action, misc.SecondsToString(interval)))
 delay(interval, function, *args, **kwargs)
