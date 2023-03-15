from analyzer.event import *

def checkForColdTemp(station,timestamp):
   # check if given station data contains a cold temp pattern.
   # this means that the station must have ta value. for each 
   # ta measurement it is checked if the temp is below a threshold. 
   # if 1/3 of all data points is below the threshold a temp
   # pattern is detected.
   # the following levels are distinguished:
   # no temp measurement: level -1 
   # >-5: level 0 (no cold temp pattern)
   # <=-5: level 1
   # <=-10: level 2
   # <=-20: level 3
   # the maximum level is returned
   level = -1
   endLevel = [0,0,0]
   datapoints = 0
   for m in station.data:
      if not m.ta is None:
         level = 0
         val = float(m.ta)
         datapoints += 1
         if val>-5:
            continue
         if val<=-5:
            endLevel[0] += 1
         if val<=-10:
            endLevel[1] += 1
         if val<=-20:
            endLevel[2] += 1
   if datapoints>0:
      # only compute temp indicator if ta exists
      threshold = datapoints/3
      if endLevel[0]>=threshold:
         level = 1
      if endLevel[1]>=threshold:
         level = 2
      if endLevel[2]>=threshold:
         level = 3
   return Event(timestamp,"cold_temp",level)

