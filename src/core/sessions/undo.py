from collections import deque

from core.sessions.session import Session

class Undo (Session):
 def __init__ (self, undo_stack_size=100, *args, **kwargs):
  self.undo_stack = deque(maxlen=undo_stack_size)
  super(Undo, self).__init__(*args, **kwargs)

 def push(self, item):
  return self.undo_stack.append(item)

 def pop(self):
  return self.undo_stack.pop()

 def shutdown (self, *args, **kwargs):
  self.undo_stack.clear()
  super(Undo, self).shutdown(*args, **kwargs)
