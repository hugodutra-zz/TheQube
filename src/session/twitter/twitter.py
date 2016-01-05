# -*- coding: utf-8 -*-

from logger import logger
logging = logger.getChild('sessions.twitter.main')

from pydispatch import dispatcher
from utils.thread_utils import call_threaded
from utils.wx_utils import always_call_after

import application
import config
import global_vars
import interface
import core.gui
import misc
import oauth2
import output
import buffers
import gui
import sessions
import signals
import stream
import time
import wx
import BaseHTTPServer
import webbrowser
from base64 import b64encode, b64decode
from urlparse import urlparse, parse_qs
from string import maketrans
from json import dumps
from ast import literal_eval
from core.sessions.buffers  import Buffers
from session import Login
from core.sessions.hotkey.hotkey import Hotkey
from session import SpeechRecognition
from session import WebService
from twython import Twython, TwythonError

logged = False
verifier = None

class Handler(BaseHTTPServer.BaseHTTPRequestHandler):

 def do_GET(self):
  global logged
  self.send_response(200)
  self.send_header("Content-type", "text/html")
  self.end_headers()
  logged = True
  params = parse_qs(urlparse(self.path).query)
  global verifier
  verifier = params.get('oauth_verifier', [None])[0]
  self.wfile.write(_("You have successfully logged in to Twitter! Now please close this window and happy tweeting!"))
  self.wfile.close()

class Twitter (Buffers, Login, Hotkey, SpeechRecognition, WebService):

 def __init__(self, *args, **kwargs):
  super(Twitter, self).__init__(*args, **kwargs)
  self.users = {}

 def register_default_buffers(self):
  if not self.online and not self.config['security']['workOffline']:
   return logging.debug("Avoiding buffer registration as offline mode is currently disabled.")
  logging.info("%s: Registering default buffers..." % self.name)  
  super(Twitter, self).register_default_buffers()
  #Hold buffer names in strings for translators
  [_('Mentions'), _('Home'), _('Direct Messages'), _('Sent')]
  self.register_buffer("Mentions", buffers.Mentions, announce=False, set_focus=False)
  self.register_buffer("Home", buffers.Home, announce=False, set_focus=False)
  self.register_buffer("Direct Messages", buffers.Directs, announce=False, set_focus=False)
  self.register_buffer("Sent", buffers.Sent, set_focus=False, announce=False, mute=True)
  self.default_buffer = self.get_buffer_by_name('Home')
  if not self.buffer_metadata.has_key('current'):
   self.buffer_metadata['current'] = 1
  if self.buffer_metadata['current'] >= len(self.buffers):
   self.buffer_metadata['current'] = 1
  self.set_buffer(self.buffer_metadata['current'], False)

 @always_call_after #madness
 def finish_initialization (self):
  twitterDataOrig = str(self.config['oauth']['twitterData'])
  trans = maketrans("-_~", "+/=")
  twitterDataTrans = twitterDataOrig.translate(trans)
  twitterData = b64decode(twitterDataTrans)
  twitterData = literal_eval(twitterData)
  self.auth_handler = Twython(twitterData[0], twitterData[1])
  logging.info("%s: Initializing Twitter API" % self.name)
  self.login()
  super(Twitter, self).finish_initialization()

 # @always_call_after
 def retrieve_access_token (self):
  output.speak(_("Please wait while an access token is retrieved from Twitter."), True)
  httpd = BaseHTTPServer.HTTPServer(('127.0.0.1', 8080), Handler)
  twitterDataOrig = str(self.config['oauth']['twitterData'])
  trans = maketrans("-_~", "+/=")
  twitterDataTrans = twitterDataOrig.translate(trans)
  twitterData = b64decode(twitterDataTrans)
  twitterData = literal_eval(twitterData)
  tw = Twython(twitterData[0], twitterData[1], auth_endpoint='authorize')
  try:
   auth = tw.get_authentication_tokens("http://127.0.0.1:8080")
  except SSLError:
   output.speak(_("Sorry, we can't connect to Twitter. You may want to adjust your firewall or antivirus software appropriately"), True)
  webbrowser.open_new_tab(auth['auth_url'])
  global logged, verifier
  logged = False
  while logged == False:
   httpd.handle_request()
  self.auth_handler = Twython(twitterData[0], twitterData[1], auth['oauth_token'], auth['oauth_token_secret'])
  token = self.auth_handler.get_authorized_tokens(verifier)
  output.speak(_("Retrieved access token from Twitter."), True)
  httpd.server_close()
  data = [token['oauth_token'], token['oauth_token_secret']]
  eData = dumps(data)
  trans = maketrans("+/=", "-_~")
  eData = b64encode(eData)
  eData = eData.translate(trans)
  self.config['oauth']['userData'] = eData
  self.login()
  del (httpd, auth, tw, token, logged, verifier, twitterData, twitterDataOrig, data, edata, self.auth_handler)


 login_required = retrieve_access_token 
 
 def do_login (self, *args, **kwargs):
  if self.is_login_required():
   self.retrieve_token()  
  self.save_config()
  twitterDataOrig = str(self.config['oauth']['twitterData'])
  trans = maketrans("-_~", "+/=")
  twitterDataTrans = twitterDataOrig.translate(trans)
  twitterData = b64decode(twitterDataTrans)
  twitterData = literal_eval(twitterData)
  userDataOrig = str(self.config['oauth']['userData'])
  userDataTrans = userDataOrig.translate(trans)
  userData = b64decode(userDataTrans)
  userData = literal_eval(userData)
  self.TwitterApi = Twython(twitterData[0], twitterData[1], userData[0], userData[1])
  self.check_twitter_connection()
  resp =  self.api_call('verify_credentials', _("verifying Twitter credentials"), report_success=False, login=True)
  self.username = resp['screen_name']
  return True

 def login_succeeded (self):
  self.save_config()
  output.speak(_("Logged into Twitter as %s") % self.username)
  self.API_initialized()
  self.setup_stream()
  if self.config['UI']['autoLoadSearches']:
   call_threaded(self.load_saved_searches)
  if self.config['UI']['autoLoadLists']:
   call_threaded(self.load_lists)

 def login_failed (self):
  output.speak(_("Login failed!"), True)
  self.login_required()

 def is_login_required (self):
  return not self.config['oauth']['userData']
 
 def load_saved_searches(self):
  searches = self.api_call('get_saved_searches', report_success=False)
  if not searches:
   return
  s = ""
  if len(searches) > 1:
   s = 'es'
  logging.info("Loading %d saved search%s from twitter." % (len(searches), s))
  output.speak(_("Loading %d saved search%s from twitter.") % (len(searches), s))
  for i in searches:
   try:
    buf = self.register_buffer(_("Search for %s") % i['query'], buffers.Search, store=True, term=i['query'], saved_id=i['id'], announce=False, set_focus=False)
   except:
    logging.exception("%s: Building buffer for saved search %s failed." % (self.name, i))

 def retrieve_lists(self, user = None, include_subscribed = False):
  if user is None:
   user = self.username
   output.speak(_("Retrieving lists"), True)
  else:
   output.speak(_("Retrieving lists for %s") % user, True)
  lists = []
  value = self.TwitterApi.show_lists(screen_name=user)
  lists.extend(value)
  if include_subscribed:
   lists.extend(self.retrieve_subscribed_lists(user))
  return lists

 def retrieve_subscribed_lists(self, user = None):
  lists = []
  nextCursor = -1
  while nextCursor:
   value = self.TwitterApi.get_list_subscriptions(screen_name=user, cursor=nextCursor)
   nextCursor = value['next_cursor']
   lists.extend(value['lists'])
  return lists

 def load_lists (self):
  all_lists = self.retrieve_lists()
  if not all_lists:
   return
  s = ""
  if len(all_lists) > 1:
   s = 's'
  logging.info("Retrieving %d list timeline%s from twitter." % (len(all_lists), s))
  output.speak(_("Retrieving %d list timeline%s from twitter.") % (len(all_lists), s))
  for i in all_lists:
   try:
    self.spawn_list_buffer(i, set_focus=False)
   except:
    logging.exception("Building buffer %s failed." % i)

 def spawn_list_buffer(self, owner = None, which = None, set_focus=True):
  self.register_buffer(_("List timeline for %s") % which['name'], buffers.ListTimeline, owner = owner, list=which, announce=True, set_focus=set_focus)

 def show_configuration_dialog(self):
  new = gui.configuration.TwitterConfigDialog(self, sessions.current_session.frame, wx.ID_ANY, config=self.config)
  new.SetDefaultValues()
  if new.ShowModal() != wx.ID_OK:
   logging.debug("User canceled configuration. Exitting.")
   return output.speak(_("Configuration canceled."), 1)
  new.SetNewConfigValues()
  with self.storage_lock:
   self.config.update(new.config)
   self.config['isConfigured'] = True
  #self.sync()
  output.speak(_("Configuration saved."), 1)
  dispatcher.send(sender=self, signal=signals.config_saved)

 def config_required (self):
  return self.show_configuration_dialog()

 def relationship_status (self, buffer=None, index=None ):
  try:
   name = buffer.get_name(index)
  except:
   name = buffer.get_screen_name(index)
  r = self.api_call('show_friendship', _("retrieving relationship status for %s") % name, report_success=False, target_screen_name=buffer.get_screen_name(index))
  message = ""
  if r['relationship']['source']['following']:
   message += _("You are following %s.  ") % name
  if r['relationship']['source']['followed_by']:
   message += _("%s is following you.  ") % name
  if not message:
   message = _("No relationship exists between yourself and %s.") % name
  output.speak(message, True)

 def relationship_status_between(self, user1, user2):
  r = self.api_call('show_friendship', _("retrieving relationship status between %s and %s") % (user1, user2), report_success=False, source_screen_name=user1, target_screen_name=user2)
  message = ""
  if r['relationship']['source']['following']:
   message += _("%s is following %s.  ") % (user1, user2)
  if r['relationship']['source']['followed_by']:
   message += _("%s is following %s.  ") % (user2, user1)
  if not message:
   message = _("No relationship exists between %s and %s.") % (user1, user2)
  output.speak(message, True)

 def follow (self, screen_name, updates=False):
  already = self.api_call('lookup_friendships', screen_name=screen_name, report_success=False)
  if len(already) > 0:
   conns = already[0]['connections']
   if 'following' in conns:
    output.speak(_("You already follow %s" % screen_name), True)
   elif 'following_requested' in conns:
    output.speak(_("You have already sent a request to follow %s" % screen_name), True)
   elif 'blocking' in conns:
    output.speak(_("You can't follow %s because you blocked this user" % screen_name), True)
   else: # Not following, so proceeding to follow
    if not updates:
     self.api_call('create_friendship', _("following %s") % screen_name, screen_name=screen_name)
    else:
     self.api_call('create_friendship', _("following %s") % screen_name, screen_name=screen_name, updates=updates)
  else: # `already` is empty, so the user doesn't exist
   output.speak(_("User %s does not exist." % screen_name), True)

 def do_unfollow (self, screen_name, action):
  already = self.api_call('lookup_friendships', screen_name=screen_name, report_success=False)
  if len(already) > 0:
   conns = already[0]['connections']
   if action == 0: # Unfollowing
    if 'following' not in conns:
     output.speak(_("You are not following %s" % screen_name), True)
    else: # Proceeding to unfollow
     self.api_call('destroy_friendship', _("unfollowing %s") % screen_name, screen_name=screen_name)
   elif action == 1: # Blocking
    if 'blocking' in conns:
     output.speak(_("You have already blocked %s" % screen_name), True)
    else:
     self.api_call('create_block', _("blocking %s") % screen_name, screen_name=screen_name)
   elif action == 2: # Reporting for spam
    self.api_call('report_spam', _("reporting %s as spam") % screen_name, screen_name=screen_name)
  else: # `already` is empty, so the user doesn't exist
   output.speak(_("User %s does not exist." % screen_name), True)

 def check_twitter_connection (self):
  #Block until we can connect to Twitter.
  #self.wait_for_availability(url='http://api.twitter.com/', message=_("Unable to connect to twitter.  %s will retry until connection is established.") % application.name)
  pass

 def post_update (self, text=u"", buffer=None, index=None):
  try:
   self.api_call('update_status', _("Update"), status=text.encode("UTF-8"))
   self.play(self.config['sounds']['tweetSent'])
  except:
   return wx.CallAfter(self.interface.NewTweet, buffer=buffer, index=index, text=text)

 def post_retweet(self, id):
  self.api_call('retweet', _("Retweet"), id=id)
  self.play(sessions.current_session.config['sounds']['tweetSent'])

 def post_reply (self, buffer=None, index=None, text="", id=0):
  if not id and 'id' in buffer[index].keys() and 'text' in buffer[index].keys() and 'source' in buffer[index].keys():
   id = buffer[index]['id']
  try:
   self.api_call('update_status', _("Reply"), status=text.encode("UTF-8"), in_reply_to_status_id=id)
  except:
   text = text.replace(text.split(' ')[0]+' ', "")
   return wx.CallAfter(self.interface.NewReply, text=text, buffer=buffer, index=index)
  self.play(self.config['sounds']['replySent'])

 def post_dm (self, user=None, text="", *args, **kwargs):
  try:
   self.api_call('send_direct_message', _("Sending dm"), user=user.encode("UTF-8"), text=text.encode("UTF-8"))
  except:
   return    wx.CallAfter(self.interface.NewDm, user=user, text=text, *args, **kwargs)
  self.play(self.config['sounds']['dmSent'])

 @always_call_after
 def _add_user_to_list (self, buffer=None, index=None):
  try:
   who = [buffer.get_screen_name(index)]
  except:
   who = [""]
  if who == [None]:
   who = [""]
  if hasattr(buffer, "get_mentions"):
   who.extend(buffer.get_mentions())
  dlg = gui.UserListDialog(parent=self.frame, title=_("Select user to add"), users=who)
  dlg.setup_users()
  dlg.finish_setup()
  if dlg.ShowModal() != wx.ID_OK:
   return output.speak(_("Canceled."), True)
  user = dlg.users.GetValue()
  output.speak(_("Retrieving lists, please wait."), True)
  lists = self.TwitterApi.lists()[0]['lists']
  dlg = wx.SingleChoiceDialog(parent=self.frame, caption=_("Select list"), message=_("Please select a list to add %s to?") % user, choices=[i['name'] for i in lists])
  if dlg.ShowModal() != wx.ID_OK:
   return output.speak(_("Canceled."), True)
  which = lists[dlg.GetSelection()]
  self.api_call('add_list_member', _("adding user %s to list %s") % (user, which['name']), id=user, slug=which['slug'])

 @always_call_after
 def update_profile (self):
  userName = self.username
  output.speak(_("Please wait while your profile is retrieved."), True)
  info = self.api_call('show_user', _("Retrieving profile to edit"), report_success=False, screen_name=userName)
  new = gui.UpdateProfileDialog(parent=sessions.current_session.frame, user=info)
  if new.ShowModal() != wx.ID_OK:
   return output.speak(_("Canceled."), True)
  name=new.name.GetValue()
  url=new.url.GetValue()
  location=new.location.GetValue()
  description=new.description.GetValue()
  self.api_call('update_profile', _("updating profile"), name=name, url=url, location=location, description=description)

 def is_list_loaded (self, which):
  for i in self.buffers:
   if hasattr(i, 'list') and i.list['slug'] == which['slug']:
    return True

 def list_members(self, owner, lst):
  self.register_buffer(_("List members for %s" % lst['name']), buffers.ListMembers, owner = owner, list=lst)

 def list_subscribers(self, owner, lst):
  self.register_buffer(_("List subscribers for %s" % lst['name']), buffers.ListSubscribers, owner = owner, list=lst)

 def list_manager(self, screen_name = None):
  #Is this the current user?
  if self.is_current_user(screen_name):
   lists = None
  else:
   lists = self.retrieve_lists(screen_name)
   if not lists:
    return output.speak(_("%s has no lists.") % screen_name, True)
  #Now pass it off to the dialog.
  self.interface.ListManager(screen_name, lists)

 def api_call(self, call_name, action="", report_success=True, report_failure=True, wait_for_connection=False, preexec_message="", login=False, *args, **kwargs):
  #Make a call to twitter
  if not login:
   self.API_initialized_event.wait()
  if wait_for_connection:
   self.check_twitter_connection()
  if preexec_message:
   output.speak(preexec_message, True)
  try:
   val = getattr(self.TwitterApi, call_name)(*args, **kwargs)
  except TwythonError as e:
   logging.exception("%s: Error making call to twitter API function %s: %s" % (self.name, call_name, e.message))
   if report_failure and hasattr(e, 'reason'):
    output.speak(_("%s failed.  Reason: %s") % (action, e.reason))
   raise e
  if report_success:
   output.speak(_("%s succeeded.") % action)
  return val

 def remaining_api_calls(self):
  hits = self.api_call('rate_limit_status', _("Retrieving API calls"), report_success=False)
  resetTime = misc.SecondsToString(hits['reset_time_in_seconds'] - round(time.time()))
  output.speak(_("You have %s API calls left.  They will reset to %d calls in %s.") % (hits['remaining_hits'], hits['hourly_limit'], resetTime), True)

 def favorite_tweet(self, buffer=None, index=None):
  twitter_id = buffer[index]['id']
  post_type = buffer.get_item_type(index)
  if post_type != _("tweet"):
   return output.speak(_("You can only favorite a tweet."), True)
  output.speak(_("Marking as favorite"), True)
  self.api_call('create_favorite', action=_("marking as favorite"), id=twitter_id)

 def unfavorite_tweet(self, buffer=None, index=None):
  twitter_id = buffer[index]['id']
  self.api_call('destroy_favorite', action=_("marking as favorite"), id=twitter_id)
  output.speak(_("Tweet removed from favorites."), 1)

 def toggle_device_notifications(self, buffer=None, index=None):
  username = buffer.get_screen_name(index)
  status = self.api_call("get_user", preexec_message=_("Toggling device notifications"), action=_("retrieving user details for %s") % username, report_success=False, screen_name=username)
  if not status['notifications']:
   logging.info("User wants to turn on device updates for %s." % username)
   self.api_call("enable_notifications", action=_("enabling device notifications for %s") % username, screen_name=username)
  elif status['notifications']:
   logging.info("User doesn't want device notifications for %s." % username)
   self.api_call("disable_notifications", action=_("disabling device notifications for %s") % username, screen_name=username)

 def setup_stream(self):
  twitterDataOrig = str(self.config['oauth']['twitterData'])
  trans = maketrans("-_~", "+/=")
  twitterDataTrans = twitterDataOrig.translate(trans)
  twitterData = b64decode(twitterDataTrans)
  twitterData = literal_eval(twitterData)
  userDataOrig = str(self.config['oauth']['userData'])
  userDataTrans = userDataOrig.translate(trans)
  userData = b64decode(userDataTrans)
  userData = literal_eval(userData)
  consumer = oauth2.Token(key=twitterData[0], secret=twitterData[1])
  token = oauth2.Token(key=userData[0], secret=userData[1])
  self.streamer = stream.UserStreamer(consumer=consumer, token=token, callback=self.stream_callback, reconnected_callback=self.update_all_buffers())
  logging.debug("Twitter user stream created.")
  self.daemon_stream = call_threaded(self.streamer.stream)
  logging.debug("Twitter user Stream connected.")

 def stream_callback(self, data):
  #Given a dictionary representing data returned from the stream, decides what to do with it.
  for b in self.buffers:
   if hasattr(b, 'handles_post') and b.handles_post(data):
    try:
     b.handle_pushed_item(data)
    except:
     logging.exception("Unable to push data to buffer")
  if 'friends' in data:
   self.friends_list = data['friends']
  else:
   self.last_stream = data

 def is_current_user(self, username):
  #Returns a bool representing if the passed in username is the same as the current twitter username.
  return username.lower() == self.username.lower()

 def update_all_buffers(self):
  for i in self.buffers:
   call_threaded(i.update, update_type=i._update_types['initial'])
