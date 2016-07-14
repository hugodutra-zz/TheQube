# -*- coding: utf-8 -*-

import sys
import os
from platform_utils import blackhole, paths
os.chdir(paths.app_path())
from logger import logger as logging
import commandline
import application
import config
import end
import global_vars
import gui
import i18n
import output
import sessions
import update_manager

"""
TheQube
An accessible social networking client

Licensed under the MIT license, see documentation/license.txt in this distribution.
"""

stdout=sys.stdout
stderr=sys.stderr
sys.stdout = open(os.path.join(os.getenv("temp"), "stdout.log"), "w")
sys.stderr = open(os.path.join(os.getenv("temp"), "stderr.log"), "w")

def main():
 try:
  config.setup()
  i18n.setup()
 except:
  logging.exception("Error in startup process.")
  #i18n isn't setup yet so we can't localize this error message.
  return output.speak("There was an error in the startup process.  We appologize for this.")
 try:
  end.setup()
  if global_vars.portable:
   logging.debug("%s is currently running in portable mode." % application.name)
  gui.setup()
  output.setup()
  output.speak(_("Welcome to %s") % application.name, 1)
  sessions.setup()
  update_manager.setup()
 except:
  logging.exception("Error in startup process.")
  output.speak(_("There was an error in the startup process.  We appologize for this."))
  return
 logging.info("Startup sequence complete.")
 application.wx_app.MainLoop()

def setup():
 global_vars.setup()


if __name__ == '__main__':
 setup()
 try:
  main()
 except:
  logging.exception("Uncaught exception")
