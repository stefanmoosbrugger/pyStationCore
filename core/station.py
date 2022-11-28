
class Station:
    # ctor 
    def __init__(self,sid,name,longi,lat,alt,region):
        self.id = str(sid)
        self.name = str(name)
        self.long = round(float(longi),3)
        self.lat = round(float(lat),3)
        self.altitude = int(alt)
        self.region = region
        self.data = []

    def meta_as_dict(self):
        d = {
            "internalid": self.id,
            "name": self.name,
            "latitude": self.lat,
            "longitude": self.long,
            "altitude": self.altitude,
            "region": str(self.region)
        }
        return d

    def measurements_as_list(self):
        l = []
        for d in self.data:
            l.append(d.measurement_as_dict())
        return l

    def __str__(self):
        retStr = "~~~~ " + str(self.name) + "@["+str(self.lat)+"°N,"+str(self.long)+"°E,"+str(self.altitude)+"] (" + str(self.region) + ")~~~~\n"
        for d in self.data[-3:]:
            retStr += str(d)
        return retStr        
