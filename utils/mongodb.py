import pymongo

class MongoDbClient:
    def open(self,host,port,db):
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
        # fetch station
        dbObj = self.stations.find_one(dbStation)
        # get all measurements
        mlist = station.measurements_as_list()
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
