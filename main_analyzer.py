
import common.config as conf
from common.connection import *
from common.region import *
from core.processor import *
from utils.connection import *
from utils.database import *
from analyzer.strong_wind import *
from analyzer.new_snow import *
from analyzer.cold_temp import *
import datetime
import time

stationdb = Database.get_database(DatabaseType.InfluxDb)
stationdb.open(conf.INFLUX_HOST,conf.INFLUX_EVENT_API_KEY,conf.INFLUX_ORG,conf.INFLUX_STATION_BUCKET)
eventdb = Database.get_database(DatabaseType.InfluxDb)
eventdb.open(conf.INFLUX_HOST,conf.INFLUX_EVENT_API_KEY,conf.INFLUX_ORG,conf.INFLUX_EVENT_BUCKET)


start_day = 1
# get the timestamp for now
now = datetime.datetime.now() 
nowts = now.timestamp()
# get the timestamp for today midnight (future midnight)
midnight = now.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
midnightts = midnight.timestamp()

# get all stations with some data form -start_day days to now
stations = stationdb.get_all_stations("-"+str(int(start_day)*24)+"h","-0m")

for i in range(0,start_day+1):
    # compute 24h intervals for each day (e.g. -8d to -7d, etc.)
    fromts = int(midnightts-(start_day-i)*86400)
    tots = int(midnightts-(start_day-i-1)*86400)
    # the timestamp for the event is always midnight from as
    # we don't want to have future time series entries.
    eventts = fromts
    # the latest (and probably incomplete day) uses the data from the latest 24h
    # but the event ts stays the same.
    if tots>int(nowts):
        fromts = int(nowts-86400)
        tots = int(nowts)

    n = 0
    for station in stations:
        # compute the events for each station and store in database.
        n = n+1
        #print("\t"+str(i)+" "+station.name+" ("+str(n)+"/"+str(len(stations))+")")
        station.data = []
        # get data for given time interval
        stationdb.get_station_data(station,fromts,tots)
        # check events for wind, snow and cold temp.
        sw = checkForStrongWind(station,eventts)
        eventdb.write_event(station,sw)
        ns = checkForNewSnow(station,eventts)
        eventdb.write_event(station,ns)
        ct = checkForColdTemp(station,eventts)
        eventdb.write_event(station,ct)
        

