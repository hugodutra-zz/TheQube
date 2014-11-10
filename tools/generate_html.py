# -*- coding: utf-8 -*-

from glob import glob
import os
import txt2tags
from subprocess import check_call

def main():
 print "Generating documentation..."
 olddocfiles1 = glob(r"..\documentation\*\*.t2t")
 olddocfiles2 = glob(r"..\documentation\*.t2t")
 olddocfiles = olddocfiles1 + olddocfiles2
 for f in olddocfiles:
  print f
  # txt2tags.exec_command_line(['-t', 'html', '--encoding=UTF-8', '--toc', f])
 docfiles1 = glob(r"..\documentation\*\*.textile")
 docfiles2 = glob(r"..\documentation\*.textile")
 docfiles = docfiles1 + docfiles2
 for ff in docfiles:
  print ff
  outfile = os.path.splitext(ff)[0] + '.html'
  args = ['pandoc', '--from', 'textile', '--to', 'html5', '--standalone', '--toc', ff, '-o', outfile]
  check_call(args)
 print "Done!"

if __name__=="__main__": main()