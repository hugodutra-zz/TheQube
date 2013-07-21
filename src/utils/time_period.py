from collections import OrderedDict

class TimePeriod (object):
 @staticmethod
 def get_units():
  units = OrderedDict()
  units['decades'] = (_("a decade"), _("{0} decades"))
  units['years'] = (_("a year"), _("{0} years"))
  units['months'] = (_("a month"), _("{0} months"))
  units['weeks'] = (_("a week"), _("{0} weeks"))
  units['days'] = (_("a day"), _("{0} days"))
  units['hours'] = (_("an hour"), _("{0} hours"))
  units['minutes'] = (_("a minute"), _("{0} minutes"))
  units['seconds'] = (_("a second"), _("{0} seconds"))
  return units
 
 def __init__(self, seconds):
  self.seconds = int(seconds)
  self.minutes = self.seconds / 60
  self.hours = self.minutes / 60
  self.days = self.hours / 24
  self.weeks = self.days / 7
  self.years = int(self.days / 365.25)
  self.months = int(self.years * 12 + (self.days - self.years * 365.25) / 30)
  self.decades = self.years / 10
  self.units = self.get_units()
 
 def __repr__(self):
  return "TimePeriod(" + repr(self.seconds) + ")"
 
 def __str__(self):
  return str(self.__unicode__())
 
 def __unicode__(self):
  for unit in self.units.keys():
   value = getattr(self, unit, 0)
   if value == 1:
    return self.units[unit][0].format(value)
   elif value > 1:
    return self.units[unit][1].format(value)
  return self.units['seconds'][1].format(self.seconds)
