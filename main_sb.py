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

# get all weather data for salzburg region
proc_sbg = Processor.get_processor(Region.Salzburg,c)
stations_sbg = proc_sbg.get_stations()
for station_sbg in stations_sbg:
   proc_sbg.get_data_for(station_sbg)
   print("write "+station_sbg.name)
   station_sbg.id = get_internal_id(station_sbg.name,station_sbg.lat,station_sbg.long)      
   d.write_station_data(station_sbg)
   stationmetadb.write_station_metadata(station_sbg)

