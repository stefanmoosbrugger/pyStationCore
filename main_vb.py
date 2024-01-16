# This script fetches the latest values for the region listed below. The 
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

c = Connection.get_connection(ConnectionType.Default)
d = Database.get_database(DatabaseType.InfluxDb)
d.open(conf.INFLUX_HOST,conf.INFLUX_STATION_API_KEY,conf.INFLUX_ORG,conf.INFLUX_STATION_BUCKET)
stationmetadb = Database.get_database(DatabaseType.InfluxDb)
stationmetadb.open(conf.INFLUX_HOST,conf.INFLUX_METADATA_API_KEY,conf.INFLUX_ORG,conf.INFLUX_METADATA_BUCKET)

# get all weather data for tirol region
proc_vb = Processor.get_processor(Region.Vorarlberg,c)
stations_vb = proc_vb.get_stations()
for station_vb in stations_vb:
   proc_vb.get_data_for(station_vb)
   print("write "+station_vb.name)
   station_vb.id = get_internal_id(station_vb.name,station_vb.lat,station_vb.long)
   d.write_station_data(station_vb)
   stationmetadb.write_station_metadata(station_vb)
