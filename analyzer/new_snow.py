from analyzer.event import *

def getLevel(hsdiff):
   if hsdiff<=3:
      return 0
   if hsdiff>3 and hsdiff<=20:
      return 1
   if hsdiff>20 and hsdiff<=50:
      return 2
   if hsdiff>50:
      return 3

def get_next_hs(station,i):
   for m in station.data[i:]:
      if not None is m.hs:
         return m.hs
   return 0

def has_hs(station):
   for m in station.data:
      if not None is m.hs:
         return True
   return False

def checkForNewSnow(station,timestamp):
   # check if given station data contains a new snow pattern.
   # this means that the station must have hs value. all 
   # hs increases are accumulated. following levels are distinguished:
   # -1: no hs measurement
   # [-inf,5]: level 0 (no new snow pattern)
   # (5,20]: level 1
   # (20,50]: level 2
   # (50,inf]: level 3
   # the maximum level is returned
   endLevel = -1
   if not has_hs(station):
      # has no has value. no reasoning possible.
      return Event(timestamp,"new_snow",endLevel)
   endLevel = 0
   station.data.sort(key=lambda x: x.timestamp)

   accHs = 0
   for i in range(0,len(station.data)-1):
      if not None is station.data[i].hs:
         accHs += max(0,get_next_hs(station,i+1)-station.data[i].hs)
   return Event(timestamp,"new_snow",getLevel(accHs))

