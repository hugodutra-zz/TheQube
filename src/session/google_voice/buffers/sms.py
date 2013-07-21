import BeautifulSoup #Because retrieving sms messages isn't officially supported, we'll do it ourselves!
from core.sessions.buffers.buffer_defaults import buffer_defaults
import threading
from .. import pygooglevoicepatches

from main import GoogleVoice
from core.sessions.sound.buffers.audio import Audio

class Sms(Audio, GoogleVoice):

 def __init__(self, *args, **kwargs):
  self.init_done_event = threading.Event()
  super(Sms, self).__init__(*args, **kwargs)
  self.default_template = 'sms'
  self.set_field('from', _("Message sender"), self.get_from)
  self.set_field('message', _("Message text"), "text")
  self.init_done_event.set()

 def retrieve_update(self, *args, **kwargs):
  sms = self.paged_update('sms')
  inbox = self.paged_update('inbox')
  results = sms[1]
  for r in results:
   if r['id'] in sms[0]:
    r.update(sms[0][r['id']])
   elif r['id'] in inbox[0]:
    r.update(inbox[0][r['id']])
  return results

 @staticmethod
 def extract_sms(htmlsms):
  """
 extract_sms  --  extract SMS messages from BeautifulSoup tree of Google Voice SMS HTML.

 Output is a list of dictionaries, one per message.
  """
  msgitems = []										# accum message items here
  #	Extract all conversations by searching for a DIV with an ID at top level.
  tree = BeautifulSoup.BeautifulSoup(htmlsms)			# parse HTML into tree
  conversations = tree.findAll("div",attrs={"id" : True},recursive=False)
  for conversation in conversations :
   #	For each conversation, extract each row, which is one SMS message.
   rows = conversation.findAll(attrs={"class" : "gc-message-sms-row"})
   for row in rows :								# for all rows
    #	For each row, which is one message, extract all the fields.
    msgitem = {"id" : conversation["id"]}		# tag this message with conversation ID
    spans = row.findAll("span",attrs={"class" : True}, recursive=False)
    for span in spans :							# for all spans in row
     cl = span["class"].replace('gc-message-sms-', '')
     msgitem[cl] = (" ".join(span.findAll(text=True))).strip()	# put text in dict
    msgitems.append(msgitem)					# add msg dictionary to list
  return msgitems


 def paged_update(self, folder_name):
  PAGE_LENGTH = 10 #How many items per page
  pages = 2
  page_num = 1
  response = [dict(), list()]
  while page_num <= pages:
   parser  = pygooglevoicepatches.fetchfolderpage(self.session.gv, folder_name, page_num)()
   folder = parser.folder
   pages = len(folder) / PAGE_LENGTH + len(folder) % PAGE_LENGTH
   response[0].update(folder['messages'])
   response[1].extend(self.extract_sms(parser.html))
   page_num += 1
  return response

 def item_exists(self, item):
  for item in self:
   if item['text'] == item['text'] and item['from'] == item['from']:
    return True

 @buffer_defaults
 def get_text(self, index=None):
  return self[index]['text']

 @buffer_defaults
 def get_from(self, index=None, item=None):
  return item['from'].replace(':', '')
