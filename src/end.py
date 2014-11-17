# -*- coding: utf-8 -*-

from logger import logger
logging = logger.getChild('core.end')

import config
import os
import win32api

def end(pid):
 PROCESS_TERMINATE = 1
 if pid != 0:
  logging.debug("Ending pid: %d" % pid)
 handle = win32api.OpenProcess(PROCESS_TERMINATE, False, pid)
 win32api.TerminateProcess(handle, -1)
 win32api.CloseHandle(handle)

def cend(pid):
 import ctypes
 PROCESS_TERMINATE = 1
 handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
 ctypes.windll.kernel32.TerminateProcess(handle, -1)
 ctypes.windll.kernel32.CloseHandle(handle)

def setup():
 try:
  end(config.main['client']['pid'])
 except Exception as exc:
  pass # This is by design for now, otherwise errors are logged on app startup
#Save the current pid in the config
 config.main['client']['pid'] = os.getpid()
 config.main.write()
 logging.info("Client PID: %d" % config.main['client']['pid'])
