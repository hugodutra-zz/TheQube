from core.gui import SelectableMessageDialog

class SMSDialog (SelectableMessageDialog):

 def __init__ (self, max_length=160, *args, **kwargs):
  super(SMSDialog, self).__init__(max_length=max_length, *args, **kwargs)
