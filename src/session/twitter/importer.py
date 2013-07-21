import db
import rfc822
import time

class Importer (object):
 def __init__ (self, filename):
  self.filename = filename

 def convert_tweet (self, tweet):
  screen_name = tweet[1]
  name = tweet[2]
  created_at = self.convert_time(tweet[3])
  id = tweet[4]
  text = tweet[5]
  if len(tweet) <> 6:
   in_reply_to_status_id = tweet[6]
  else:
   in_reply_to_status_id = None
  user = dict(name=name, screen_name=screen_name)
  answer = dict(id=id, user=user, text=text, created_at=created_at, in_reply_to_status_id=in_reply_to_status_id, source='imported database')
  return answer

 def convert_dm (self, tweet):
  screen_name = tweet[1]
  name = tweet[2]
  created_at = self.convert_time(tweet[3])
  id = tweet[4]
  text = tweet[5]
  sender = dict(name=name, screen_name=screen_name)
  answer = dict(id=id, sender=sender, text=text, created_at=created_at)
  return answer

 @staticmethod
 def convert_time (val):
  return rfc822.formatdate(float(val))

 def load_table (self, table):
  db.NewConnection(self.filename)
  cur = db.NewCursor()
  cur.execute("select * from %s" % table)
  answer = cur.fetchall()
  cur.close()
  return answer

 def convert_table (self, table):
  answer = []
  for item in table:
   if len(item) == 7:
    answer.append(self.convert_tweet(item))
   else:
    answer.append(self.convert_dm(item))
  return answer

