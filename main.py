from common.connection import *
from common.region import *
from core.processor import *
from utils.connection import *

c = Connection.get_connection(ConnectionType.Default)

# get all weather data for switzerland region
#proc_ch = Processor.get_processor(Region.Schweiz,c)
#stations_ch = proc_ch.get_stations()
#for station_ch in stations_ch:
#   proc_ch.get_data_for(station_ch)
#   print(station_ch)

# get all weather data for bavaria region
#proc_by = Processor.get_processor(Region.Bayern,c)
#stations_by = proc_by.get_stations()
#for station_by in stations_by:
#   proc_by.get_data_for(station_by)
#   print(station_by)

# get all weather data for tirol region
#proc_ti = Processor.get_processor(Region.Tirol,c)
#stations_ti = proc_ti.get_stations()
#for station_ti in stations_ti:
#   proc_ti.get_data_for(station_ti)
#   print(station_ti)