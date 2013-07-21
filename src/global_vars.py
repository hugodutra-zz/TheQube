#Holds all universal variables
import sys

speaker = None
brailler = None
LogFile = "The Qube.log"
portable = False
from_source = None
Updating = False
platform = None
KeyboardHelp = False
remote = False

def setup():
 global from_source
 global platform
 from_source = sys.argv[0].endswith('.pyw')
 platform = sys.platform
