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

# get all weather data for aosta region
proc_ao = Processor.get_processor(Region.Aosta,c)
stations_ao = proc_ao.get_stations()
for station_ao in stations_ao:
   proc_ao.get_data_for(station_ao)
   print("write "+station_ao.name)
   station_ao.id = get_internal_id(station_ao.name,station_ao.lat,station_ao.long)
   d.write_station_data(station_ao)
   stationmetadb.write_station_metadata(station_ao)

