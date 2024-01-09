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

# get all weather data for south tirol region
proc_sti = Processor.get_processor(Region.Suedtirol,c)
stations_sti = proc_sti.get_stations()
for station_sti in stations_sti:
   proc_sti.get_data_for(station_sti)
   print("write "+station_sti.name)
   station_sti.id = get_internal_id(station_sti.name,station_sti.lat,station_sti.long)    
   d.write_station_data(station_sti)
   stationmetadb.write_station_metadata(station_sti)

