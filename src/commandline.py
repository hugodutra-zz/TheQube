import global_vars
from optparse import OptionParser
#Mongoose command line parser

parser = OptionParser()

parser.add_option("-p", "--portable", help="Run in Portable mode to keep all data files in the application's current directory.", action="store_true", dest="portable")
parser.add_option("-d", "--debug", help="Generate and log extra debugg data.", action="store_true",dest="debug")
parser.add_option("-r", "--remote", help="Allow remote access to debug terminal", action="store_true",dest="remote")

(options, args) = parser.parse_args()
global_vars.portable = options.portable
global_vars.debug = options.debug
global_vars.remote_access = options.remote
