from analyzer.event import *

def checkForStrongWind(station,timestamp):
   # check if given station data contains a strong wind pattern.
   # this means that the station must have vw value. for each 
   # vw measurement it is checked if the wind is strong. 
   # the following levels are distinguished:
   # no vw measurement: level -1
   # [-inf,20): level 0 (no strong wind pattern)
   # [20,45): level 1
   # [45,70): level 2
   # [70,inf]: level 3
   # the maximum level is returned   
   endLevel = 0
   hasVw = False
   for m in station.data:
      if not m.vw is None:
         hasVw = True
         val = float(m.vw)
         if val>=20 and val<45:
            endLevel = max(1,endLevel)
         if val>=45 and val<70:
            endLevel = max(2,endLevel)
         if val>=70:
            endLevel = max(3,endLevel)
   if not hasVw:
      endLevel = -1
   return Event(timestamp,"strong_wind",endLevel)
