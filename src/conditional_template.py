import string

ID_FIRST = frozenset("".join((string.ascii_letters, "_")))
ID_REST = frozenset("".join((string.ascii_letters, string.digits, "_")))
KEYWORDS = frozenset(("if", "not"))
(TKN_NAME, TKN_NUMBER, TKN_STRING, TKN_RELOP) = range(4)

class ConditionalTemplate (object):
 def __init__(self, pattern):
  self.vars = set()
  self.look = None
  self.pattern = pattern
  self.backouts = []
  self.pos = None
  self.len = len(self.pattern)
  self.last_match = None
  self._Next()
  self.template = self._Compile()
  self.vars = frozenset(self.vars)
  del self.look
  del self.pattern
  del self.backouts
  del self.pos
  del self.len
  del self.last_match
 
 def _Next(self):
  if self.pos is None:
   self.pos = 0
  elif self.pos < self.len:
   self.pos += 1
  if self.pos < self.len:
   self.look = self.pattern[self.pos]
  else:
   self.look = None
 
 def _SavePos(self):
  self.backouts.append(self.pos)
 
 def _RestorePos(self):
  self.pos = self.backouts.pop()
  if self.pos < self.len:
   self.look = self.pattern[self.pos]
  else:
   self.look = None
 
 def _KeepPos(self):
  self.backouts.pop()
 
 def _Match(self, token):
  if isinstance(token, basestring):
   self._SavePos()
   for i in xrange(len(token)):
    if self.look != token[i]:
     self._RestorePos()
     return False
    self._Next()
   self.last_match = token
   self._KeepPos()
   return True
  else:
   value = None
   if token == TKN_NAME:
    value = self._GetName()
   elif token == TKN_NUMBER:
    value = self._GetNumber()
   elif token == TKN_STRING:
    value = self._GetString()
   elif token == TKN_RELOP:
    value = self._GetRelationalOperator()
   if value is not None:
    self.last_match = value
   return value is not None
 
 def _Compile(self, nested=False):
  if nested:
   self._SavePos()
   if not self._Match("{"):
    self._RestorePos()
    return None
  template = []
  templateString = []
  while self.look is not None:
   if self._Match("$$"):
    templateString.append("$")
   elif self._Match("${{"):
    templateString.append("{{")
   elif self._Match("$}}"):
    templateString.append("}}")
   elif self._Match("{"):
    templateString.append("{{")
   elif self._Match("}"):
    if nested:
     break
    else:
     templateString.append("}}")
   else:
    node = self._GetNode()
    if node is None:
     node = self.look
     self._Next()
    if isinstance(node, basestring):
     templateString.append(node)
    else:
     if len(templateString) > 0:
      template.append(u"".join(templateString))
      templateString = []
     template.append(node)
  if nested:
   if self.last_match == "}":
    self._KeepPos()
   else:
    self._RestorePos()
    return None
  if len(templateString) > 0:
   template.append(u"".join(templateString))
  return tuple(template)
 
 def _GetNode(self):
  self._SavePos()
  if not self._Match("$"):
   self._RestorePos()
   return None
  elif self._Match("{"):
   if not self._Match(TKN_NAME):
    self._RestorePos()
    return None
   name = self.last_match
   if not self._Match("}"):
    self._RestorePos()
    return None
  elif self._Match(TKN_NAME):
   name = self.last_match
  else:
   self._RestorePos()
   return None
  if name in KEYWORDS and name != "if":
   self._RestorePos()
   return None
  if name != "if":
   self._KeepPos()
   self.vars.add(name)
   return u"".join(("{", name, "}"))
  condition = u""
  conditional_vars = set()
  TrueTemplate = None
  FalseTemplate = None
  if not self._Match("("):
   self._RestorePos()
   return None
  self._SkipSpace()
  if self._Match("not "):
   self._SkipSpace()
   if not self._Match(TKN_NAME):
    self._RestorePos()
    return None
   name = self.last_match
   condition += "not "
  elif self._Match(TKN_NAME):
   name = self.last_match
  else:
   self._RestorePos()
   return None
  if name in KEYWORDS:
   self._RestorePos()
   return None
  condition += name
  conditional_vars.add(name)
  self._SkipSpace()
  if self._Match(TKN_RELOP):
   condition += self.last_match
   self._SkipSpace()
   if self._Match(TKN_NAME) and self.last_match not in KEYWORDS:
    name = self.last_match
    conditional_vars.add(name)
    condition += name
   elif self._Match(TKN_STRING) or self._Match(TKN_NUMBER):
    condition += self.last_match
   else:
    self._RestorePos()
    return None
  if not self._Match(")"):
   self._RestorePos()
   return None
  TrueTemplate = self._Compile(nested=True)
  if TrueTemplate is not None:
   self._KeepPos()
   FalseTemplate = self._Compile(nested=True)
  else:
   self._RestorePos()
   return None
  for conditional_var in conditional_vars:
   self.vars.add(conditional_var)
  if FalseTemplate is None:
   return (condition, TrueTemplate, ())
  else:
   return (condition, TrueTemplate, FalseTemplate)
 
 def _GetRelationalOperator(self):
  if self._Match("<>"):
   return "!="
  for op in ("<=", "<", ">=", ">", "==", "!="):
   if self._Match(op):
    return op
  return None
 
 def _GetString(self):
  self._SavePos()
  if not self._Match('"'):
   self._RestorePos()
   return None
  parsedString = ['u"']
  while self.look is not None:
   if self._Match("\\"):
    parsedString.append(r"\\")
   elif self._Match('""'):
    parsedString.append(r'\"')
   elif self._Match('"'):
    parsedString.append('"')
    self._KeepPos()
    return u"".join(parsedString)
   else:
    parsedString.append(self.look)
    self._Next()
  self._RestorePos()
  return None
 
 def _GetNumber(self):
  self._SavePos()
  parsedNumber = []
  if self._Match("-"):
   parsedNumber.append("-")
  elif self._Match("+"):
   pass
  if self.look not in string.digits:
   self._RestorePos()
   return None
  if self._Match('0'):
   while self._Match('0'):
    pass
   if self.look not in string.digits:
    parsedNumber.append('0')
  while self.look in string.digits:
   parsedNumber.append(self.look)
   self._Next()
  self._KeepPos()
  self._SavePos()
  if self._Match("."):
   if self.look not in string.digits:
    self._RestorePos()
    return u"".join(parsedNumber)
   parsedNumber.append(".")
   while self.look in string.digits:
    parsedNumber.append(self.look)
    self._Next()
  self._KeepPos()
  return u"".join(parsedNumber)
 
 def _GetName(self):
  self._SavePos()
  if self.look not in ID_FIRST:
   self._RestorePos()
   return None
  name = [self.look]
  self._Next()
  while self.look in ID_REST:
   name.append(self.look)
   self._Next()
  self._KeepPos()
  return u"".join(name)
 
 def _SkipSpace(self):
  if self._Match(" "):
   while self.look == " ":
    self._Next()
   return True
  else:
   return False
 
 def Substitute(self, mapping, sub_template=None):
  data = None
  if sub_template is None:
   sub_template = self.template
   data = {}
   for var in self.vars:
    if var in mapping:
     data[var] = mapping[var]
    elif var == "nl":
     data['nl'] = u"\r\n"
    else:
     data[var] = u""
  else:
   data = mapping
  strings = []
  for i in sub_template:
   if isinstance(i, basestring):
    strings.append(i.format(**data))
   elif eval(i[0], data):
    strings.append(self.Substitute(data, i[1]))
   else:
    strings.append(self.Substitute(data, i[2]))
  return u"".join(strings)
