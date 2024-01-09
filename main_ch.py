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

# get all weather data for switzerland region
proc_ch = Processor.get_processor(Region.Schweiz,c)
stations_ch = proc_ch.get_stations()
for station_ch in stations_ch:
   proc_ch.get_data_for(station_ch)
   print("write "+station_ch.name)
   station_ch.id = get_internal_id(station_ch.name,station_ch.lat,station_ch.long)    
   d.write_station_data(station_ch)
   stationmetadb.write_station_metadata(station_ch)
