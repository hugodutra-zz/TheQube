import re
from core.sessions.storage.storage_migration import MigrationBase

ESCAPED = r"(?P<escaped>\$)"
CONDITION = r'\?(?P<condition>[_a-z][_a-z0-9<>=" ]*)\?(?P<true>[^?]*)\?(?P<false>[^?]*)\?'
NAMED = r"(?P<name>[_a-z][_a-z0-9]*)"
BRACED = r"\{(?P<braced>[_a-z][_a-z0-9]*)\}"
INVALID = r"(?P<invalid>)"
PATTERN = r"\$(?:" + u"|".join((ESCAPED, CONDITION, NAMED, BRACED, INVALID)) + ")"
TRUE_TEST = r'(?P<name>[_a-z][_a-z0-9]*) *(== *"yes"|<> *"no")'
FALSE_TEST = r'(?P<name>[_a-z][_a-z0-9]*) *(== *"no"|<> *"yes")'

class Migration (MigrationBase):
 def _Convert(self, old_template):
  new_template = []
  last = 0
  for m in re.finditer(PATTERN, old_template, re.I):
   if m.start() > last:
    new_template.append(old_template[last:m.start()].replace("{", "${{").replace("}", "$}}"))
   if m.group("escaped") is not None:
    new_template.append("$$")
   elif m.group("name") is not None:
    new_template.append("$" + m.group("name"))
   elif m.group("braced") is not None:
    new_template.append("${" + m.group("braced") + "}")
   elif m.group("condition") is not None:
    condition = m.group("condition")
    condition_match = re.match(TRUE_TEST, condition, re.I)
    if condition_match:
     condition = condition_match.group("name")
    else:
     condition_match = re.match(FALSE_TEST, condition, re.I)
     if condition_match:
      condition = "not " + condition_match.group("name")
    true_part = m.group("true").replace("{", "${{").replace("}", "$}}")
    false_part = m.group("false").replace("{", "${{").replace("}", "$}}")
    if not false_part or false_part.isspace():
     new_template.append("$if(" + condition + "){" + true_part + "}")
    else:
     new_template.append("$if(" + condition + "){" + true_part + "}{" + false_part + "}")
   elif m.group("invalid") is not None:
    new_template.append("$$")
   last = m.end()
  if last < len(old_template):
   new_template.append(old_template[last:].replace("{", "${{").replace("}", "$}}"))
  return u"".join(new_template)

 def forwards(self):
  root = self.session.connection.get_root()
  if 'config' not in root:
   return
  if 'templateSystemVersion' in root['config'] and root['config']['templateSystemVersion'] >= 1:
   return
  if 'templates' in root['config']:
   templates = root['config']['templates']
   for name in ('countdown', 'timer'):
    if name in templates:
     templates[name] = self._Convert(templates[name])
  root['config']['templateSystemVersion'] = 1
