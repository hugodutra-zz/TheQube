# -*- coding: utf-8 -*-

from logger import logger
logging = logger.getChild('sessions.twitter.interface')

from importer import Importer
from durus_importer import SessionImporter
from core.sessions.buffers.buffer_defaults import buffer_defaults
from utils.delay import delay_action
from utils.thread_utils import call_threaded
from utils.wx_utils import modal_dialog, question_dialog
from geopy.geocoders import GoogleV3

import config
import calendar
import core.gui
import global_vars
import misc
import os
import output
import paths
import rfc822
import buffers
import gui
import sessions
import templates
import time
import wx
import traceback
from core.sessions.buffers.interface import BuffersInterface
from core.sessions.hotkey.interface import HotkeyInterface
from meta_interface import MetaInterface

class TwitterInterface (BuffersInterface, HotkeyInterface, MetaInterface):

 @buffer_defaults
 def NewTweet(self, buffer=None, index=None, text="", title=None, retweet=False):
  """Allows you to post a new tweet.
"""
  new = gui.NewTweetDialog(parent=self.session.frame, text=text, title=title)
  new.retweet.Show(retweet)
  new.message.SetInsertionPoint(0)
  val=new.ShowModal()
  if val==wx.ID_OK:
   if new.retweet.GetValue():
    return self.Retweet(buffer, index)
   else:
    text = new.message.GetValue()
  else:
   logging.debug("User canceled post.")
   return output.speak(_("Canceled."), True)
  if len(text) > self.session.config['lengths']['tweetLength']:
   logging.info("Tweet too long.  Forcing edit.")
   return self.NewTweet(buffer, index, text)
  if new.delay:
   delay_action(new.delay, self.session.post_update, text=text, action=_("tweet"))
  else:
   call_threaded(self.session.post_update, text=text)

 @buffer_defaults
 def NewDm(self, buffer=None, index=None, user="", text=""):
  """Allows you to send a new direct message to a user."""

  who = buffer.get_all_screen_names(index)
  new = modal_dialog(gui.NewDirectDialog, parent=self.session.frame, default=who[0], selection=who, title=_("Direct message"), text=text)
  user = new.selection.GetValue()
  text = new.message.GetValue()
  if len(text) > self.session.config['lengths']['dmLength']:
   logging.info("Direct message too long.  Forcing edit.")
   return self.NewDm (buffer, index, user, text)
  if new.delay:
   delay_action(new.delay, self.session.post_dm, text=text, buffer=buffer, index=index, user=user, action=_("dm"))
  else:
   call_threaded(self.session.post_dm, buffer=buffer, index=index, user=user, text=text)

 @buffer_defaults
 def NewReply(self, buffer=None, index=None, text="", user=None):
  """Allows you to post a reply to a tweet."""

  default = user
  users = buffer.get_all_screen_names(index)
  if 'source' not in buffer[index] and 'text' in buffer[index] and self.session.config['UI']['DMSafeMode']:
   return self.NewDm(buffer, index, text)
  if not self.session.config['UI']['replyToSelf']:
   for n, u in enumerate(users):
    if self.session.is_current_user(u):
     users.remove(users[n])
  if default:
   users.insert(0, default)
  if not users:
   return output.speak(_("Unable to detect a user to reply to."), True)
  new = modal_dialog(gui.NewReplyDialog, parent=self.session.frame, default=users[0], selection=users, title=_("Reply"), text=text)
  user = new.selection.GetValue()
  fulltext = templates.replyTemplate(user, new.message.GetValue())
  if len(fulltext) > self.session.config['lengths']['tweetLength']:
   i = fulltext.index(" ") + 1
   return self.NewReply(buffer, index, fulltext[i:])
  if new.delay:
   delay_action(new.delay, self.session.post_reply, buffer=buffer, index=index, text=fulltext, action=_("reply"))
  else:
   call_threaded(self.session.post_reply, buffer=buffer, index=index, text=fulltext)

 @buffer_defaults
 def ViewItem(self, buffer=None, index=None):
  """Allows you to view the current tweet in a dialog."""

  title = _("view item")
  try:
   text = buffer.get_text(index)
  except:
   text = buffer.format_item(index)
  try:
   title = _("View Tweet From %s") % buffer.get_screen_name(index)
  except:
   logging.exception("ViewItem: Unable to obtain screen name")
  self.NewTweet(text=text, title=title, retweet=True)

 @buffer_defaults
 def Retweet (self, buffer=None, index=None):
  """Allows you to retweet (RT) the current tweet."""

  try:
   user = buffer.get_screen_name(index)
   text = templates.retweetTemplate(user, buffer.get_text(index))
   if 'retweeted_status' not in buffer[index]:
    id = buffer[index]['id']
   else:
    id = buffer[index]['retweeted_status']['id']
  except:
   logging.debug("Retweeter: Unable to retrieve post to reply to.")
   return output.speak(_("Item is not a post."), True)
  if self.session.config['UI']['DMSafeMode'] and 'source' not in buffer[index]:
   logging.debug("Retweeter: Preventing retweet of direct message in DM safe mode...")
   return output.speak(_("Cannot retweet a direct message while DM safe mode is enabled."), True)
  if self.session.is_current_user(user):
   logging.debug("Retweeter: Preventing retweet of user's own tweet...")
   return output.speak(_("Cannot retweet your own tweet."), True)
  title="Retweet"
  choice = 0
  if self.session.config['UI']['RTStyle'] == 0 and 'source' in buffer[index]:
   choice = question_dialog(caption=_("Retweet"), message=_("Would you like to add a comment?"))
   if choice == wx.ID_CANCEL:
    return output.speak(_("Canceled."), True)
   elif choice == wx.ID_NO:
    return call_threaded(self.session.post_retweet, id)
   else:
    return   self.NewTweet(buffer, index, text, title)
  elif self.session.config['UI']['RTStyle'] == 1:
   logging.debug("Retweeter: Automatically retweeting...")
   call_threaded(self.session.post_retweet, id)
  elif self.session.config['UI']['RTStyle'] == 2 or 'source' not in buffer[index]:
   self.NewTweet(buffer, index, text, title)

 @buffer_defaults
 def Follow(self, buffer=None, index=None):
  """Allows you to follow the specified user."""

  who = buffer.get_all_screen_names(index)
  if not who:
   output.speak(_("No users to follow detected in current post."), True)
   return logging.debug("No users to follow detected in current post.")
  new = modal_dialog(gui.FollowDialog, parent=self.session.frame, users=who)
  who = new.users.GetValue()
  updates = new.updates.GetValue()
  call_threaded(self.session.follow, who, updates)

 @buffer_defaults
 def Unfollow(self, buffer=None, index=None):
  """Allows you to unfollow, block, or report the specified user as a spammer."""

  who = buffer.get_all_screen_names(index)
  if not who:
   output.speak(_("No users to unfollow detected in current post."), True)
   return logging.debug("No users to unfollow detected in current post.")
  new = modal_dialog(gui.UnfollowDialog, parent=self.session.frame, users=who)
  who = new.users.GetValue()
  action = new.action.GetSelection()
  call_threaded(self.session.do_unfollow, who, action)

 @buffer_defaults
 def ListUrls(self, buffer=None, index=None):
  """List any URLs or mentions of a twitter screen name in a dialog."""

  urls = []
  try:
   urls.extend(buffer.get_urls(index))
  except:
   pass
  try:
   urls.extend(["@%s" % i for i in buffer.get_mentions(index)])
  except:
   pass
  try:
   urls.extend(["@%s" % buffer.get_screen_name(index)])
  except:
   pass
  urls = misc.RemoveDuplicates(urls)
  if not urls:
   logging.debug("No web addresses or usernames in current tweet.")
   return output.speak(_("No URLs detected in current post."), 1)
  logging.debug("Launching URL choice dialog.")
  dlg = modal_dialog(core.gui.ListURLsDialog, parent=self.session.frame, urls=urls)
  url = dlg.urls_list.GetStringSelection().replace("@","http://ww	w.twitter.com/")
  logging.debug("Opening URL: %s " % url)
  misc.open_url_in_browser(url)

 def TwitterSearch (self, text=None):
  """Allows you to search twitter for the specified term."""

  if not text:
   text = self.buffer().get_hash_tags(self.buffer().index)
  text.extend(self.buffer().get_mentions(self.buffer().index))
  new = modal_dialog(gui.TwitterSearchDialog, parent=self.session.frame, title=_("Twitter search"), text=text)
  term = unicode(new.term.GetValue())
  save = new.save.GetValue()
  store = new.store.GetValue()
  count = new.retrieveCount.GetValue()
  maxAPIPerUpdate = new.maxAPIPerUpdate.GetValue()
  if count == 100 and maxAPIPerUpdate > 1:
   count = 200
  if not term:
   output.speak(_("Please enter a term to search for."), True)
   return self.TwitterSearch()
  title = _("Search for %s") % term
  search = self.session.register_buffer(title, buffers.Search, store=store, term=term, saved=save, count=count, maxAPIPerUpdate=maxAPIPerUpdate)

 def TwitterTrends(self):
  """Creates a buffer containing the top trends on twitter."""

  self.session.register_buffer(_("Trending: Worldwide"), buffers.TopTrends)

 def Favorites(self):
  """Creates a buffer containing the tweets you have favorited."""

  self.session.register_buffer(_("Favorites"), buffers.Favorites, prelaunch_message=_("Loading favorites"))

 @buffer_defaults
 def FavoritesFor(self, buffer=None, index=None):
  """Creates a buffer containing the tweets the specified user has favorited."""

  who = buffer.get_all_screen_names(index)
  new = modal_dialog(gui.FavoritesDialog, parent=self.session.frame, users=who, results_per_api=200)
  who = new.users.GetValue()
  name = _("%s's favorites") % who
  self.session.register_buffer(name, buffers.Favorites, username=who, count=new.retrieveCount.GetValue(), maxAPIPerUpdate=new.maxAPIPerUpdate.GetValue(), prelaunch_message=_("Loading favorites for %s.") % who)

 @buffer_defaults
 def FavoriteTweet(self, buffer=None, index=None):
  """Add the current tweet to your favorites on twitter."""

  call_threaded(self.session.favorite_tweet, buffer, index)

 @buffer_defaults
 def UnfavoriteTweet(self, buffer=None, index=None):
  """If possible, removes the current tweet from your favorites."""

  call_threaded(self.session.unfavorite_tweet, buffer, index)

 def Followers(self):
  """Creates a buffer containing the people who are following you."""

  self.session.register_buffer(_("Followers"), buffers.Followers, prelaunch_message=_("Loading followers list."))

 def Friends (self):
  """Creates a buffer containing the people you are following."""

  self.session.register_buffer(_("Friends"), buffers.Friends, prelaunch_message=_("Loading friends list."))

 def FollowersAnalysis(self):
  """Analyzes your followers list to determine your new followers and those who have stopped following you."""

  followers = None
  for i in self.session.buffers:
   if hasattr(i, 'is_followers_buffer') and i.is_followers_buffer:
    followers = i
    break
  if not followers:
   return output.speak(_("Please launch your followers buffer before attempting to perform analysis."), 1)
  elif not len(followers):
   return output.speak(_("Cannot perform analysis on an empty followers buffer."), 1)
  which = self.session.register_buffer(name=_("Followers Analysis"), type=buffers.FollowersAnalysis, prelaunch_message=_("Performing followers analysis, please wait..."), mute=True)

 def BlockedUsers(self):
  """Creates a buffer containing the people whom you have blocked."""

  self.session.register_buffer(_("Blocked Users"), buffers.Blocked, prelaunch_message=_("Loading blocked users."))

 '''
 def GetRateLimitStatus(self):
  """Reports the number of calls you can make to twitter  as well as how long you have until they reset."""

  output.speak(_("Checking current API call count..."), True)
  call_threaded(self.session.remaining_api_calls)
'''

 @buffer_defaults
 def DeviceNotifications(self, buffer=None, index=None):
  """Toggles whether or not device notifications will be sent to your mobile device. Your device must be configured on twitter first."""

  call_threaded(self.session.toggle_device_notifications, buffer, index)

 def UpdateProfile(self):
  """Update the information displayed on your twitter profile for other people to view."""

  call_threaded(self.session.update_profile)

 @buffer_defaults
 def ViewUserTimeline(self, buffer=None, index=None):
  """Creates a buffer containing the timeline of the specified user."""

  who = buffer.get_all_screen_names(index)
  new = modal_dialog(gui.IndividualDialog, parent=self.session.frame, users=who)
  who = new.users.GetValue()
  self.session.register_buffer(_("%s's timeline") % who, buffers.Individual, username=who, count = new.retrieveCount.GetValue(), maxAPIPerUpdate = new.maxAPIPerUpdate.GetValue(), prelaunch_message=_("Loading timeline for %s.") % who)

 @buffer_defaults
 def FriendSound(self, buffer=0, index=None):
  """Lets you define a specific sound to be played for incoming tweets from a particular user."""

  screen_name = buffer.get_screen_name(index)
  dlg = wx.FileDialog(None, message="Define a sound for %s" % screen_name, wildcard="WAV files (*.wav)|*.wav|" \
 "OGG Files (*.ogg)|*.ogg|" \
 "MP3 Files (*.mp3)|*.mp3|" \
 "FLAC Files (*.flac)|*.flac|" \
 "AIFF Files (*.aiff)|*.aiff|" \
 "MOD Files (*.mod)|*.mod|" \
 "S3M (*.s3m)|*.s3m|" \
 "XM Files (*.xm)|*.xm|" \
 "IT Files (*.it)|*.it",
 style=wx.OPEN)
  dlg.Raise()
  if dlg.ShowModal() == wx.ID_OK:
   path = dlg.GetDirectory()
   filename = dlg.GetFilename()
   self.session.config['sounds'][screen_name] = os.path.join(path, filename)
  else:
   self.session.frame.Show(false)

 @buffer_defaults
 def inReplyTo(self, buffer=None, index=None):
  """Moves to the tweet that is a reply to the current tweet."""

  self.session.navigate_to_item_matching('id', buffer[index]['in_reply_to_status_id'])

 @buffer_defaults
 def inReplyFrom(self, buffer=None, index=None):
  """Moves to the tweet that the current tweet is a reply to."""

  self.session.navigate_to_item_matching('in_reply_to_status_id', buffer[index]['id'])

 @buffer_defaults
 def followersFor(self, buffer=None, index=None):
  """Creates a buffer containing the people that are following the specified user."""

  who = buffer.get_all_screen_names(index)
  new = modal_dialog(gui.FollowersDialog, parent=self.session.frame, users=who)
  who = new.users.GetValue()
  retrieveCount = new.retrieveCount.GetValue()
  maxAPIPerUpdate = new.maxAPIPerUpdate.GetValue()
  name = _("%s's followers") % who
  self.session.register_buffer(name, buffers.Followers, username=who, count = retrieveCount, maxAPIPerUpdate = maxAPIPerUpdate, prelaunch_message=_("Loading friends for %s.") % who)

 @buffer_defaults
 def friendsFor (self, buffer=None, index=None):
  """Creates a buffer containing the people the specified user is following."""

  who = buffer.get_all_screen_names(index)
  new = modal_dialog(gui.FriendsDialog, parent=self.session.frame, users=who)
  who = new.users.GetValue()
  retrieveCount = new.retrieveCount.GetValue()
  maxAPIPerUpdate = new.maxAPIPerUpdate.GetValue()
  name = _("%s's friends") % who
  self.session.register_buffer(name, buffers.Friends, username=who, count = retrieveCount, maxAPIPerUpdate = maxAPIPerUpdate, prelaunch_message=_("Loading friends for %s.") % who)

 def RetweetsBuffer(self):
  """Creates a buffer containing your tweets that were retweeted by others."""

  method = "retweets_of_me"
  self.session.register_buffer(_("%s" % method), buffers.Retweets, method=method)

 '''
 def RetweetsBuffer(self):
  """Creates a buffer containing either your friends retweets, your retweets, or your retweets that were retweeted by others."""

  dlg = wx.SingleChoiceDialog(None, _("Select which type of retweets to display:"), _("Select type"), [_("My friends' retweets"), _("My retweets"), _("My tweets that have been retweeted by others")])
  dlg.Raise()
  if dlg.ShowModal() == wx.ID_OK:
   method = dlg.GetStringSelection()
   if method == _("My friends' retweets"):
    method = "retweeted_to_me"
   elif method == _("My retweets"):
    method = "retweeted_by_me"
   else:
    method = "retweets_of_me"
   self.session.register_buffer(_("%s" % method), buffers.Retweets, method=method)
'''

 @buffer_defaults
 def UserInfo(self, buffer=None, index=None):
  """Speaks information about the sender of the current tweet depending on the value of the template set in the configuration dialog."""

  formatted = buffer.format_user_info(index)
  if formatted == None:
   if 'from_user' in buffer[index]:
    output.speak(_("This command is not supported from within a search buffer."), 1)
   else:
    output.speak(_("No user detected in current item."), 1)
  else:
   output.speak(formatted, 1)

 @buffer_defaults
 def UserInfoDialog(self, buffer=None, index=None):
  """Displays a dialog containing information such as the screen name, real name, whether or not tweets are protected, etc, for the specified user."""

  who = buffer.get_all_screen_names(index)
  new = modal_dialog(gui.UserInfoDialog, parent=self.session.frame, users=who)
  who = new.users.GetValue()
  output.speak(_("Loading profile for %s") % who, True)
  user_ptr = self.session.TwitterApi.show_user(screen_name=who)
  logging.debug("UserInfoDialog: Twitter returned user profile for %s as \n%s" % (who, user_ptr))
  new = gui.TwitterProfileDialog(parent=self.session.frame, id=wx.ID_ANY, user=user_ptr)
  new.ShowModal()

 def ListManager(self, screen_name = None, lists = None):
  """"Allows you to manage or create new lists."""

  dlg = gui.list_manager.ListManagerDialog(parent=self.session.frame, screen_name=screen_name, lists=lists)
  dlg.ShowModal()

 def LocalTrends(self):
  """Creates a buffer containing the trends for the specified location."""

  output.speak(_("Retrieving locations."), True)
  try:
   locations = self.session.TwitterApi.get_available_trends()
   logging.debug("Raw locations: %s" % str(locations))
  except:
   logging.debug("Unable to obtain local trend locations.")
   return output.speak(_("Unable to retrieve local trend locations; please try again later."), True)
  locations.sort(key=lambda location: location['name'])
  locations_by_name = {}
  locations_tree = {}
  for location in locations:
   type = location['placeType']['name']
   place = location['name']
   if place == "Worldwide":
    continue
   locations_by_name[place] = location
   if type not in locations_tree.keys():
    locations_tree[type] = []
   locations_tree[type].append(place)
  dlg = modal_dialog(gui.LocalTrendsDialog, parent=self.session.frame, id=wx.ID_ANY, locations_tree=locations_tree)
  if dlg.locations_list.GetSelection() == wx.NOT_FOUND:
   choice = dlg.locations_list.GetItems()[0]
  else:
   choice = dlg.locations_list.GetStringSelection()
  location = locations_by_name[choice]
  self.session.register_buffer(_("Trending: %s" % location['name']), buffers.LocalTrends, woeid=location['woeid'])

 def ImportDatabase(self):
  """Import an old-style  .db qwitter database, or .session file into the current session's storage."""

  def import_buffer (tablename, buffername):
   table = new.load_table(tablename)
   newtable = new.convert_table(table)
   buf = self.session.get_buffer_by_name(buffername)
   buf.storage.extend(newtable)
   buf.storage.sort(key=lambda a: calendar.timegm(rfc822.parsedate(a['created_at'])))
   buf.storage = misc.RemoveDuplicates(buf.storage, lambda x: x['id'])
  f = wx.Frame(None, wx.ID_ANY, "FileDialog")
  dlg = wx.FileDialog(f, message="Select Database", defaultDir=paths.data_path(), wildcard="Session files (*.session)|*.session|Qwitter Databases (*.DB)|*.db")
  f.Raise()
  if dlg.ShowModal() == wx.ID_OK:
   filename = dlg.GetPath()
   dlg.Destroy()
   f.Destroy()
  else:
   output.speak(_("Canceled"), True)
   dlg.Destroy()
   f.Destroy()
   return
  if filename.lower().endswith('.db'):
   new = Importer(filename)
   home = new.load_table("tweets")
   directs = new.load_table("directs")
   mentions = new.load_table("replies")
   sent = new.load_table("sent")
   total = len(home) + len(directs) + len(mentions) + len(sent)
   yesno = wx.MessageBox(_("Are you sure you want to import %d items from old database?") % total, _("Are you sure?"), style=wx.YES|wx.NO)
   if yesno == wx.YES:
    output.speak(_("Importing, please wait."), True)
   else:
    return output.speak(_("Canceled."), True)
   for i in [("tweets", "Home"), ("replies", "Mentions"), ("directs", "Direct Messages"), ("sent", "Sent")]:
    import_buffer(*i)
  elif filename.lower().endswith('.session'):
   try:
    new = SessionImporter(filename)
   except TypeError:
    return output.speak(_("Session type mismatch."))
   new.do_import()
  wx.MessageBox(_("Import completed successfully."), _("Import complete."))

 def ShowConfigurationDialog(self):
  self.session.show_configuration_dialog()

 @buffer_defaults
 def GeoLocation(self, buffer=None, index=None):
  """Reports the geo location info of the tweet, if available."""

  if 'geo' not in buffer[index] or not buffer[index]['geo']:
   output.speak(_("No geo location info present in this tweet."), 1)
  else:
   output.speak(_("Retrieving geo location info..."), 1)
   coordinates = (buffer[index]['geo']['coordinates'][0], buffer[index]['geo']['coordinates'][1])
   try:
    geolocator = GoogleV3()
   except Exception as glexc:
    logging.exception("Geolocator exception: {0}". format(glexc))
   try:
    location = geolocator.reverse(coordinates, True, None, config.main['languages']['current'])
   except Exception as geoexc:
    logging.exception("Unable to retrieve geolocation info, coordinates: {0}, error: {1}".format(str(coordinates), geoexc))
    return output.speak(_("Error determining location."), True)
  if location.address is not None:
   return output.speak(location.address, True)
  else:
   return output.speak(_("Sorry, geo locator didn't provide an address."))

 @buffer_defaults
 def GeoLocationDialog(self, buffer=None, index=None):
  """Places geo location info, if available, of the current tweet into a dialog with text fields."""

  if 'geo' not in buffer[index] or not buffer[index]['geo']:
   output.speak(_("No geo location info present in this tweet."), 1)
  else:
   output.speak(_("Retrieving geo location info..."), 1)
   coordinates = (buffer[index]['geo']['coordinates'][0], buffer[index]['geo'] ['coordinates'][1])
   try:
    geolocator = GoogleV3()
   except Exception as glexc:
    logging.exception("Geolocator exception: {0}". format(glexc))
   try:
    location = geolocator.reverse(coordinates, True, None, config.main['languages']['current'])
   except Exception as geoexc:
    logging.exception("Unable to retrieve geolocation info, coordinates: {0}, error: {1}".format(str(coordinates), geoexc))
    return output.speak(_("Error determining location."), True)
   if location.address is not None:
    dlg = gui.GeoLocationDialog(parent=self.session.frame, id=wx.ID_ANY,  coordinates=coordinates, location=location.address)
    dlg.ShowModal()
    dlg.Destroy()
   else:
    return output.speak(_("Sorry, geo locator didn't provide an address."))

 @buffer_defaults
 def GeoLocationInput(self, buffer=None, index=None):
  """Allows you to specify coordinates  for which you want geo location info."""

  if 'geo' not in buffer[index] or not buffer[index]['geo']:
   lat = long = None
  else:
   lat = str(buffer[index]['geo']['coordinates'][0])
   long = str(buffer[index]['geo']['coordinates'][1])
  f = wx.Frame(None, wx.ID_ANY, "")
  f.Show(True)
  dlg = gui.GeoLocationInputDialog(parent=f, lat=lat, long=long)
  if dlg.ShowModal() == wx.ID_CANCEL:
   f.Destroy()
   return output.speak(_("Canceled."), True)
  output.speak(_("Retrieving geo location info..."), 1)
  coordinates = (float(dlg.lat.GetValue()), float(dlg.long.GetValue()))
  try:
   geolocator = GoogleV3()
  except Exception as glexc:
   logging.exception("Geolocator exception: {0}". format(glexc))
  try:
   location = geolocator.reverse(coordinates, True, None, config.main['languages']['current'])
  except Exception as geoexc:
   logging.exception("Unable to retrieve geolocation info, coordinates: {0}, error: {1}".format(str(coordinates), geoexc))
   output.speak(_("Error determining location."), True)
   f.Destroy()
   return
  if location.address is not None:
   dlg = gui.GeoLocationDialog(parent=f, id=wx.ID_ANY, coordinates=coordinates, location=location.address)
   dlg.ShowModal()
  else:
   return output.speak(_("Sorry, geo locator didn't provide an address."))
  f.Destroy()

 def UserSearch(self):
  """Allows you to search for a user by name on Twitter"""

  dlg = wx.TextEntryDialog(self.session.frame, _("Enter a name to search for:"), _("User search"))
  dlg.Raise()
  if dlg.ShowModal() != wx.ID_OK:
   dlg.Destroy()
   return output.speak(_("Canceled"), True)
  q = dlg.GetValue()
  self.session.register_buffer(_("User search for %s") % q, buffers.UserSearch, query=q)
  dlg.Destroy()

 @buffer_defaults
 def RelationshipStatus(self, buffer=None, index=None):
  """Retrieve and speak the current relationship between yourself and the user associated with the focused item"""

  try:
   name = buffer.get_screen_name(index)
  except:
   output.speak(_("No user detected in current item."), 1)
   return
  try:
   name = buffer.get_name(index)
  except:
   pass
  output.speak(_("Retrieving relationship status for %s") % name, True)
  call_threaded(self.session.relationship_status, buffer=buffer, index=index)

 @buffer_defaults
 def RelationshipStatusBetween(self, buffer=None, index=None):
  """Determine the relationship status between any two users"""

  username = self.session.username
  who = buffer.get_all_screen_names(index)
  if len(who) > 1 or who[0] != "":
   try:
    who.remove(username)
   except:
    pass
   who.append(username)
  new = modal_dialog(gui.RelationshipStatusDialog, parent=self.session.frame, users=who)
  user1 = new.users.GetValue()
  user2 = new.users2.GetValue()
  output.speak(_("Retrieving relationship status between %s and %s") % (user1, user2), True)
  call_threaded(self.session.relationship_status_between, user1, user2)

 @buffer_defaults
 def AddToList(self, buffer=None, index=None):
  """Add a user to a list"""

  who = buffer.get_all_screen_names(index)
  dlg = gui.UserListDialog(parent=self.session.frame, title=_("Select user to add"), users=who)
  dlg.setup_users()
  dlg.finish_setup()
  if dlg.ShowModal() != wx.ID_OK:
   return output.speak(_("Canceled."), True)
  user = dlg.users.GetValue()
  output.speak(_("Retrieving lists, please wait."), True)
  lists = self.session.TwitterApi.show_lists()
  if not lists:
   return output.speak(_("No lists defined.  Please create a list with the list manager before performing this action."), True)
  dlg = wx.SingleChoiceDialog(parent=self.session.frame, caption=_("Select list"), message=_("Please select a list to add %s to?") % user, choices=[i['name'] for i in lists])
  if dlg.ShowModal() != wx.ID_OK:
   return output.speak(_("Canceled."), True)
  which = lists[dlg.GetSelection()]
  self.session.api_call('add_list_member', action=_("adding %s to list %s.") % (user, which['name']), screen_name=user, list_id=which['id'])

 @buffer_defaults
 def RemoveFromList(self, buffer=None, index=None):
  """Remove a user from a list"""

  who = buffer.get_all_screen_names(index)
  dlg = gui.UserListDialog(parent=self.session.frame, title=_("Select user to remove"), users=who)
  dlg.setup_users()
  dlg.finish_setup()
  if dlg.ShowModal() != wx.ID_OK:
   return output.speak(_("Canceled."), True)
  user = dlg.users.GetValue()
  output.speak(_("Retrieving lists, please wait."), True)
  lists = self.session.TwitterApi.show_lists()
  if not lists:
   return output.speak(_("No lists defined.  Please create a list with the list manager before performing this action."), True)
  dlg = wx.SingleChoiceDialog(parent=self.session.frame, caption=_("Select list"), message=_("Please select a list to remove %s from?") % user, choices=[i['name'] for i in lists])
  if dlg.ShowModal() != wx.ID_OK:
   return output.speak(_("Canceled."), True)
  which = lists[dlg.GetSelection()]
  self.session.api_call('delete_list_member', action=_("removing %s from list %s.") % (user, which['name']), screen_name=user, list_id=which['id'])

 def ListMembers(self):
  """Creates a buffer containing the users that the current list buffer is following."""

  buffer = self.session.current_buffer
  if not hasattr(buffer, 'list'):
   return output.speak(_("Please change to a list buffer before using this command."), True)
  owner = buffer.owner
  lst = buffer.list
  self.session.list_members(owner, lst)

 def SocialNetwork(self):
  """Creates a buffer containing your social network based on the choice selected."""

  dlg = wx.SingleChoiceDialog(None, _("Choose your social network:"), _("Social Network"), [_("Users whom I follow and who also follow me"), _("Users whom I follow but who do not follow me"), _("Users who follow me but whom I do not follow")])
  dlg.Raise()
  if dlg.ShowModal() == wx.ID_OK:
   followers = None
   friends = None
   for i in self.session.buffers:
    if hasattr(i, 'is_followers_buffer') and i.is_followers_buffer:
     followers = i
    if hasattr(i, 'is_friends_buffer') and i.is_friends_buffer:
     friends = i
    if followers and friends:
     break
   if not (followers and friends):
    return output.speak(_("Please launch both your followers and friends buffers before attempting to create a social network."), 1)
   elif not (len(followers) and len(friends)):
    return output.speak(_("Cannot create social network from an empty followers or friends buffer."), 1)
   choice = dlg.GetStringSelection()
   if choice == _("Users whom I follow and who also follow me"):
    method = 'intersection'
   elif choice == _("Users whom I follow but who do not follow me"):
    method = 'friend_but_not_follower'
   else:
    method = 'follower_but_not_friend'
   self.session.register_buffer(_("Social Network: %s") % choice, buffers.SocialNetwork, prelaunch_message=_("Creating social network, please wait..."), method=method, mute=True)

 def ListSubscribers(self):
  """Creates a buffer containing the users that follow the current list buffer."""

  buffer = self.session.current_buffer
  if not hasattr(buffer, 'list'):
   return output.speak(_("Please change to a list buffer before using this command."), True)
  owner = buffer.owner
  lst = buffer.list
  self.session.list_subscribers(owner, lst)

 @buffer_defaults
 def TranslateTweet(self, buffer=None, index=None):
  """Translate the current tweet into another language with Google Translate service."""

  try:
   text_to_translate = buffer.get_text(index).encode("UTF-8")
  except:
   text_to_translate = buffer.format_item(index).encode("UTF-8")
  dlg = modal_dialog(core.gui.TranslateDialog, parent=self.session.frame)
  source = dlg.langs_keys[dlg.source_lang_list.GetSelection()]
  target = dlg.langs_keys[dlg.target_lang_list.GetSelection()]
  try:
   translated_text = dlg.t.translate(text_to_translate, target, source)
  except Exception as e:
   logging.exception("Translation error: {0}".format(e))
   output.speak(_("Translation process has failed."), True)
  self.NewTweet(text=translated_text, title=_("Translation from %s to %s") % (dlg.langs_values[dlg.source_lang_list.GetSelection()], dlg.langs_values[dlg.target_lang_list.GetSelection()]), retweet=True)

 @buffer_defaults
 def ViewUserLists(self, buffer = None, index = None):
  """View the public lists a user has created."""

  who = buffer.get_all_screen_names(index)
  dlg = gui.UserListDialog(parent = self.session.frame, title = _("Select user"), users = who)
  dlg.setup_users()
  dlg.finish_setup()
  if dlg.ShowModal() != wx.ID_OK:
   return output.speak(_("Canceled."), True)
  user = dlg.users.GetValue()
  dlg.Destroy()
  call_threaded(self.session.list_manager(screen_name = user))

interface = TwitterInterface
