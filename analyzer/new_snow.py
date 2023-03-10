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

def checkForNewSnow(station,timestamp):
   # check if given station data contains a new snow pattern.
   # this means that the station must have hs value. for each 
   # hs measurement it is checked if the hs measurement 24h ago 
   # is >0. following levels are distinguished:
   # -1: no hs measurement
   # [-inf,3]: level 0 (no new snow pattern)
   # (3,20]: level 1
   # (20,50]: level 2
   # (50,inf]: level 3
   # the maximum level is returned
   endLevel = 0
   hasHs = False
   if len(station.data)==0:
      return Event(timestamp,"new_snow",-1)
   station.data.sort(key=lambda x: x.timestamp)
   if (station.data[-1].timestamp-station.data[0].timestamp)<=86400:
      if not station.data[-1].hs is None and not station.data[0].hs is None:
         hasHs = True
         endLevel = getLevel(station.data[-1].hs-station.data[0].hs)
   else:
      imax = len(station.data)
      for i in range(imax):
         jtouse = i
         for j in range(i+1,imax):
            if (station.data[j].timestamp-station.data[i].timestamp)>86400:
               jtouse = j
         if not station.data[jtouse].hs is None and not station.data[i].hs is None:
            hasHs = True
            endLevel = max(endLevel,getLevel(station.data[jtouse].hs-station.data[i].hs))
   if not hasHs:
      endLevel = -1
   return Event(timestamp,"new_snow",endLevel)
