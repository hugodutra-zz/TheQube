from audio_services import matches_url
import json
import re
import urllib

@matches_url('http://boo.fm')
def convert_boo(url):
 if not re.findall ("^https?://boo.fm/[a-zA-Z]+\d+/?$", url.lower()):
  raise TypeError('%r is not a valid URL' % url)
 audio_id = url.split('.fm/')[-1][1:]
 return 'http://audioboo.fm/boos/%s.mp3' % audio_id

@matches_url('http://audioboo.fm')
def convert_audioboo(url):
 if not re.findall ("^https?://audioboo.fm/boos/[a-zA-Z0-9]", url.lower()):
  raise TypeError('%r is not a valid URL' % url)
 url = url.split('?')[0]
 return url + ".mp3"

@matches_url('https://audioboo.fm')
def convert_secure_audioboo(url):
 if not re.findall ("^https?://audioboo.fm/boos/[a-zA-Z0-9]", url.lower()):
  raise TypeError('%r is not a valid URL' % url)
 url = url.split('?')[0]
 return url + ".mp3"

@matches_url('https://audioboom.com')
def convert_audioboom(url):
 if not re.findall ("^https?://audioboom.com/(boos|posts)/[a-zA-Z0-9]", url.lower()):
  raise TypeError('%r is not a valid URL' % url)
 url = url.split('?')[0]
 return url + ".mp3"

@matches_url ('http://soundcloud.com/')
def convert_soundcloud (url):
 client_id = "df8113ca95c157b6c9731f54b105b473"
 permalink = urllib.urlopen ('http://api.soundcloud.com/resolve.json?client_id=%s&url=%s' %(client_id, url))
 if permalink.getcode () == 404:
  permalink.close ()
  raise TypeError('%r is not a valid URL' % url)
 else:
  resolved_url = permalink.geturl ()
  permalink.close ()
 track_url = urllib.urlopen (resolved_url)
 track_data = json.loads (track_url.read ())
 track_url.close ()
 if track_data ['streamable']:
  return track_data ['stream_url'] + "?client_id=%s" %client_id
 else:
  raise TypeError('%r is not streamable' % url)

@matches_url('http://twup.me')
def convert_twup(url):
 result = re.match("^http://twup.me/(?P<audio_id>[A-Za-z0-9]+/?)$", url, re.I)
 if not result or result.group("audio_id") is None:
  raise TypeError('%r is not a valid URL' % url)
 audio_id = result.group("audio_id")
 return 'http://twup.me/%s' % audio_id

@matches_url('http://sndup.net')
def convert_sndup(url):
 result = re.match("^http://sndup.net/(?P<audio_id>[a-z0-9]+/?)(|d|l|a)/?$", url, re.I)
 if not result or result.group("audio_id") is None:
  raise TypeError('%r is not a valid URL' % url)
 audio_id = result.group("audio_id")
 return 'http://sndup.net/%s' % audio_id

def convert_generic_audio(url):
 from urlparse import urlparse
 urlpath = urlparse(url).path
 if not urlpath.lower().endswith((".mp3", ".wav", ".ogg", ".wma")):
  raise TypeError('%r is not a valid URL' % url)
 return url
