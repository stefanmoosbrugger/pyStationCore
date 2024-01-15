# This script fetches the latest values for the regions listed below. The 
# fetched data is pushed into the station database and the metadata database 
# is updated (lastseen, etc.). This script is executed periodically to keep 
# the data in the database up to date.

import common.config as conf
from common.connection import *
from common.region import *
from core.processor import *
from utils.connection import *
from utils.database import *
from utils.idhash import *
from utils.location import *

c = Connection.get_connection(ConnectionType.Default)
d = Database.get_database(DatabaseType.InfluxDb)
d.open(conf.INFLUX_HOST,conf.INFLUX_STATION_API_KEY,conf.INFLUX_ORG,conf.INFLUX_STATION_BUCKET)
stationmetadb = Database.get_database(DatabaseType.InfluxDb)
stationmetadb.open(conf.INFLUX_HOST,conf.INFLUX_METADATA_API_KEY,conf.INFLUX_ORG,conf.INFLUX_METADATA_BUCKET)
stations = d.get_all_stations("-7d","-0m")

def get_station_data_for(region,exclude = None):
   # get all weather data for region
   proc = ProcessorHistoricalZAMG(c,region)
   # get all stations
   stations_cur = proc.get_stations()
   for station_cur in stations_cur:
      # get data for each station
      proc.get_data_for(station_cur)
      # if not data contained make an early continue      
      if not len(station_cur.data):
         continue
      if exclude and exclude(station_cur):
         continue
      station_cur.id = get_internal_id(station_cur.name,station_cur.lat,station_cur.long)
      station_found = None
      for station_db in stations:
         # check if the given station is known or might be covered by
         # some other data source (e.g., wiski tirol and zamg)
         if (not station_found) and are_stations_locations_approximately_same(station_cur,station_db):
            # station is known. use given station and transfer the data
            station_found = station_db
            station_found.data = station_cur.data
      if not station_found:
         station_found = station_cur
      # write data and metadata
      print("write "+str(station_found.region)+" "+station_found.name)
      d.write_station_data(station_found)
      stationmetadb.write_station_metadata(station_found)

def main():
   # fetch all Vorarlberg stations except Warth and Valluga as they are covered by Tirol processor
   get_station_data_for(Region.Vorarlberg,lambda s: "Warth" in s.name or "Valluga" in s.name)
   # fetch all Kaernten stations except Katschberg as this one is covered by Salzburg processor
   get_station_data_for(Region.Kaernten,lambda s: "Katschberg" in s.name)
   # fetch all Steiermark stations 
   get_station_data_for(Region.Steiermark)

if __name__ == "__main__":
    main()   