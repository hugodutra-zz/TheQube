# -*- coding: utf-8 -*-

# Global variables
# A part of TheQube, an accessible social networking client
# Copyright © TheQube Developers Team, 2015

#Holds all universal variables
import sys

speaker = None
brailler = None
LogFile = "TheQube.log"
portable = False
from_source = False
Updating = False
KeyboardHelp = False
debug = False

def setup():
 global from_source
 global debug
 from_source = sys.argv[0].endswith('.pyw') or sys.argv[0] == "pythonw.exe"
 debug = from_source or "-d" in sys.argv or "--debug" in sys.argv
