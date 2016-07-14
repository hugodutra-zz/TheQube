# -*- coding: utf-8 -*-

from logger import logger
logging = logger.getChild('core.end')

import config
import os
import win32api
import win32con

def end(pid):
 ACCESS_LEVEL = win32con.PROCESS_QUERY_INFORMATION|win32con.PROCESS_VM_READ
 if pid != 0:
  logging.debug("Ending pid: %d" % pid)
  try:
   handle = win32api.OpenProcess(ACCESS_LEVEL, False, pid)
   win32api.TerminateProcess(handle, -1)
   win32api.CloseHandle(handle)
  except Exception as e:
   logging.exception("Process terminating failed on pid {0}: {1}".format(pid, e))

def cend(pid):
 import ctypes
 ACCESS_LEVEL = win32con.PROCESS_QUERY_INFORMATION|win32con.PROCESS_VM_READ
 handle = ctypes.windll.kernel32.OpenProcess(ACCESS_LEVEL, False, pid)
 ctypes.windll.kernel32.TerminateProcess(handle, -1)
 ctypes.windll.kernel32.CloseHandle(handle)

def setup():
 try:
  end(config.main['client']['pid'])
 except Exception as exc:
  logging.exception("Ending failed: {0}".format(exc))
  # pass # This is by design for now, otherwise errors are logged on app startup
 #Save the current pid in the config
 config.main['client']['pid'] = os.getpid()
 config.main.write()
 logging.info("Client PID: %d" % config.main['client']['pid'])
