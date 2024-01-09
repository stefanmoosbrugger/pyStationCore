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
proc_ti = Processor.get_processor(Region.Tirol,c)
stations_ti = proc_ti.get_stations()
for station_ti in stations_ti:
   proc_ti.get_data_for(station_ti)
   print("write "+station_ti.name)
   station_ti.id = get_internal_id(station_ti.name,station_ti.lat,station_ti.long)   
   d.write_station_data(station_ti)
   stationmetadb.write_station_metadata(station_ti)

