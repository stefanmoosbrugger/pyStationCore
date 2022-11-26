from common.connection import *
from common.region import *
from core.processor import *
from core.station import *
from utils.connection import *
from utils.database import *
from bson.objectid import ObjectId
import sys

c = Connection.get_connection(ConnectionType.Default)
d = Database.get_database(DatabaseType.MongoDb)
d.open("## IP ##","## PORT ##","## DB ##","## USER ##","## PWD ##")

def main(argv):
    if(len(sys.argv)!=2):
        print("Usage: "+str(sys.argv[0])+" <id>")
        sys.exit(-1)
    stationid = str(sys.argv[1])
    dbStation = { "_id": ObjectId(stationid) }
    if d.stations.count_documents(dbStation)==0:
        print("station not found "+stationid)
        sys.exit(-1)
    dbObj = d.stations.find_one(dbStation)
    if (not "internalid" in dbObj.keys()):
        print("internalid not found")
        sys.exit(-1)

    regionstr = dbObj["region"]
    region = 0
    if("Region.Schweiz" in regionstr):
       region = Region.Schweiz
    if("Region.Tirol" in regionstr):
       region = Region.Tirol
    if("Region.Bayern" in regionstr):
       region = Region.Bayern
    station = Station(dbObj["internalid"],dbObj["name"],dbObj["longitude"],dbObj["latitude"],dbObj["altitude"],region) 
    Processor.get_processor(region,c).get_data_for(station)
    d.write_station_data(station)
    sys.exit(0)

if __name__ == "__main__":
   main(sys.argv[1:])
