
class Station:
    # ctor 
    def __init__(self,sid,name,longi,lat,alt,region):
        self.id = sid
        self.name = name
        self.long = longi
        self.lat = lat
        self.altitude = alt
        self.region = region
        self.data = []

    def __str__(self):
        retStr = "~~~~ " + str(self.name) + "@["+str(self.lat)+"°N,"+str(self.long)+"°E,"+str(self.altitude)+"] (" + str(self.region) + ")~~~~\n"
        for d in self.data[-3:]:
            retStr += str(d)
        return retStr        