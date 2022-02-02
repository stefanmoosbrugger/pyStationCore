import pymongo

class MongoDbClient:
    def open(self,host,port,db):
        self.client = pymongo.MongoClient(str("mongodb://"+str(host)+":"+str(port)"/"))
        self.db = self.client[str(db)]
        self.stations = self.db["stations"]

    def write_station_data(self,station):
        dbStation = { "name": station.name, "region": str(station.region) }
        dbObj = 0
        dbStationQ = self.stations.find(dbStation)
        if len(dbStationQ)==0:
            # insert station object
            dbObj = self.stations.insert_one(station.meta_as_dict())
        else:
            # use existing
            dbObj = dbStationQ[0]
        mlist = station.measurements_as_list()
        for m in mlist:
            p = self.stations.find({"some": "condition", "comments.type": "image"})            
