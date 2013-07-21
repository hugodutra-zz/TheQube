#!/usr/bin/env python

from glob import glob
import os
import sys
import txt2tags

def main():
 print "Generating documentation..."
 docfiles1 = glob(r"..\documentation\*\*.t2t")
 docfiles2 = glob(r"..\documentation\*.t2t")
 docfiles = docfiles1 + docfiles2
 for f in docfiles:
  print f
  txt2tags.exec_command_line(['-t', 'html', '--encoding=UTF-8', '--toc', f])
 print "Done!"

if __name__=="__main__": main()