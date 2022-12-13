import pymongo
import sys

class MongoDbClient:
    def open(self,host,port,db,user="",passwd=""):
        if user!="" or passwd!="":
            self.client = pymongo.MongoClient(str("mongodb://"+str(user)+":"+str(passwd)+"@"+str(host)+":"+str(port)+"/?authSource="+str(db)))
        else:
            self.client = pymongo.MongoClient(str("mongodb://"+str(host)+":"+str(port)+"/"))
        self.db = self.client[str(db)]
        self.stations = self.db["stations"]
        self.measurements = self.db["measurements"]

    def write_station_data(self,station):
        dbStation = { "name": station.name, "region": str(station.region) }
        dbObj = 0
        if self.stations.count_documents(dbStation)==0:
            # insert station object
            self.stations.insert_one(station.meta_as_dict())
        #else:
        #    self.stations.update_one(
        #        { "name": station.name, "region": str(station.region) },
        #        { "$set": station.meta_as_dict() },
        #        upsert=True)
        # fetch station
        dbObj = self.stations.find_one(dbStation)
        # get all measurements
        mlist = station.measurements_as_list()
        if(len(mlist)==0):
            return
        print(station.name)
        # get affected measurements from database
        timestamps = [d["timestamp"] for d in mlist if "timestamp" in d]
        firstTimestamp = min(timestamps) 
        lastTimestamp = max(timestamps)
        print("\tfirst: "+str(firstTimestamp))
        print("\tlast:"+str(lastTimestamp))
        dbmlist = list(self.measurements.find({"stationId": dbObj["_id"], "timestamp":{"$gte":firstTimestamp,"$lte":lastTimestamp}}));
        print("\tgot: "+str(len(mlist)))
        print("\tgot from db: "+str(len(dbmlist)))
        # get all entries in the db
        [i.pop("stationId",None) for i in dbmlist]
        [i.pop("_id",None) for i in dbmlist]
        dbmlist = [dict(sorted(i.items())) for i in dbmlist]
        mlist = [dict(sorted(i.items())) for i in mlist]
        mlist = [i for i in mlist if i not in dbmlist]
        # only keep the entries that require an update/insert
        print("\twrite: "+str(len(mlist)))
        for m in mlist:
            m["stationId"] = dbObj["_id"]
            self.measurements.update_one(
                {"stationId":dbObj["_id"], "timestamp":m["timestamp"]},
                {"$set":m},
                upsert=True)

    def get_station_data(self,station):
        dbStation = { "name": station.name, "region": str(station.region) }
        if self.stations.count_documents(dbStation):
            dbObj = self.stations.find_one(dbStation)
            return list(self.measurements.find({"stationId":dbObj["_id"]}))
        else:
            return ""
