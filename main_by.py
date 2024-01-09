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

# get all weather data for bavaria region
proc_by = Processor.get_processor(Region.Bayern,c)
stations_by = proc_by.get_stations()
for station_by in stations_by:
   proc_by.get_data_for(station_by)
   print("write "+station_by.name)
   station_by.id = get_internal_id(station_by.name,station_by.lat,station_by.long)    
   d.write_station_data(station_by)
   stationmetadb.write_station_metadata(station_by)

