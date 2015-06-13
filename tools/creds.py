# -*- coding: utf-8 -*-

import io
import sys
from json import dumps
from base64 import b64encode as encode, b64decode as decode
from string import maketrans

def main():
	if len(sys.argv) < 3 or len(sys.argv) >4:
		print("Usage: creds.py <key> <secret> [<fileToWrite>]")
		sys.exit(1)
	data = [sys.argv[1], sys.argv[2]]
	mCreds = dumps(data)
	trans = maketrans("+/=", "-_~")
	mCreds = encode(mCreds)
	mCreds = mCreds.translate(trans)
	creds = unicode(mCreds)
	if len(sys.argv) == 4:
		with io.open(sys.argv[3], "w", encoding="utf-8") as f:
			f.write(creds)
	else: # File is not provided
		print(creds)

if __name__ == "__main__": main()