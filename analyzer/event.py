class Event:
    # this class represents a weather event (e.g., strong wind) + level.
    def __init__(self,ts,name,threshold):
        self.timestamp = ts                # timestamp value []            
        self.name = name                   # event name
        self.level = threshold             # severity level

    def measurement_as_dict(self):
        d = {}
        if not self.timestamp is None:
            d["timestamp"] = int(self.timestamp)
        if not self.name is None:
            d["name"] = str(self.name)
        if not self.level is None:
            d["level"] = int(self.level)
        return d

    def __str__(self):
        retStr = " -> event@" + str(self.timestamp) + "\n"
        if not self.name is None:
            retStr += "event name: " + str(self.name) + " \n"
        if not self.level is None:
            retStr += "severity level: " + str(self.level) + " \n"
        return retStr
