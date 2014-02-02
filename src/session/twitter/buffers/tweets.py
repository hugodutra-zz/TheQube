from main import Twitter
from core.sessions.buffers import field_metadata as meta
from core.sessions.buffers.buffer_defaults import buffer_defaults

class Tweets (Twitter):
 """Base class for all Twitter tweet buffers."""

 primary_key = 'id'

 def __init__(self, *args, **kwargs):
  super(Tweets, self).__init__(*args, **kwargs)
  self.set_field('from', _("Tweet Source"), 'source', processor=self.process_source)
  self.set_field('geo', _("Geo Tagged"), 'geo', field_type=meta.FT_BOOL)
  self.set_field('message', _("Message Text"), self.get_text)
  self.set_field('name', _("Name"), ('user', 'name'))
  self.set_field('screen_name', _("Screen Name"), ('user', 'screen_name'))
  self.set_field('location', _("Location"), ('user', 'location'))
  self.set_field('retweet_count', _("Retweet count"), None, field_type=meta.FT_NUMERIC)
  self.set_field('favorited', _("Favorited"), None, field_type=meta.FT_BOOL)
  self.set_field('retweeted', _("Retweeted"), None, field_type=meta.FT_BOOL)
  #And the template:
  self.default_template = 'default_template'
  
 def compare_items(self, item1, item2):
  return item1['id'] == item2['id']

 def get_index_by_tweet_id(self, tweet_id):
  #Given a tweet id, looks it up in the database and returns the index of the item or None if the item can't be found.
  return self.get_index_from_rapid_cache('id', tweet_id)

 def get_index_by_reply_id(self, reply_id):
  #Given a reply id, looks it up in the database and returns the index of the item or None if the item isn't in this database
  return self.get_index_from_rapid_cache('in_reply_to_status_id', reply_id)

 def get_max_twitter_id (self):
  """Retrieves the highest stored twitter ID."""
  if not len(self):
   return 1
  else:
   return self[-1]['id']
   
 @buffer_defaults
 def get_urls(self, index=None, item=None):
  if 'entities' not in item:
   return super(Tweets, self).get_urls(index=index, item=item)
  answer = []
  if 'media' in item['entities']:
   item['entities']['urls'] = item['entities']['media']
  else:
   item['entities']['urls'] = item['entities']['urls']
  for u in item['entities']['urls']:
   if u['expanded_url'] is not None:
    answer.append(u['expanded_url'])
   else:
    answer.append(u['url'])
  return answer

 def process_update(self, update, *args, **kwargs):
  for item in update:
   if 'retweeted_status' in item:
    item = item['retweeted_status']
   else:
    item = item 
   if 'entities' not in item:
    continue
   if 'media' in item['entities']:
    item['entities']['urls'] = item['entities']['media']
   else:
    item['entities']['urls'] = item['entities']['urls']
   for url in item['entities']['urls']:
    if url['expanded_url'] is not None:
     item['text'] = item['text'].replace(url['url'], url['expanded_url'])
  return super(Tweets, self).process_update(update, *args, **kwargs)

