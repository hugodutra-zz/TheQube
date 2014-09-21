"""
Easy creation of list views.
Just create an instance of ListView class, giving the arguments for columns and items while instantiating or later, and then call finish_setup method.
Columns and items should be specified from within lists. When specifying items, each list item must be a tuple with labels for each column.
You can also append new items later, by calling add_items method.
Example:
from gui_components.listviews import ListView
my_list = ListView(parent=None, columns=['Name', 'Age', 'Gender'], items=[('John', '24', 'Male'), ('Mary', '25', 'Female')])
my_list.finish_setup()
"""

from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
#from sys import maxint
import wx

class ListView (object):

 def __init__ (self,columns=[], items=[], *args, **kwargs):
  self.list = AutoWidthListCtrl(*args, **kwargs)
  self.columns = columns
  self.items = items
  
 def finish_setup (self):
  """Creates a list view with all specified columns and items."""

  self.insert_columns(self.columns)
  self.add_items(self.items)
  self.list.Show(True)

 def insert_columns (self, columns):
  """Inserts columns into the list view."""

  for col, label in enumerate(columns):
   self.list.InsertColumn(col, label)

 def add_items (self, items):
  """Adds new items to a list view."""
  for number, data in enumerate(items):
   index = self.list.InsertStringItem(number, items[number][0])
   for col, label in enumerate(items[number]):
    self.list.SetStringItem(index, col, label)


class AutoWidthListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, *args, **kwargs):
        wx.ListCtrl.__init__(self, style=wx.LC_REPORT, *args, **kwargs)
        ListCtrlAutoWidthMixin.__init__(self)
