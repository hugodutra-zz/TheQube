#Basic base64 encoding of stuff to keep people from stealing twitter passwords
from binascii import a2b_base64, b2a_base64

def encrypt (data):
 return b2a_base64(data)[:-1]


def decrypt (data):
 return a2b_base64(data)
