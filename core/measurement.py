class Measurement:
    # this class represents a measurement unit.
    # a measurement consists of the following entries:
    # time: unix epoch timestamp
    # hs: snow height
    # hs24h: snow height 24h
    # ta: air temp
    # tss: surface temp
    # vw: velocity wind
    # vwmax: velocity wind max
    # dw: direction wind
    # not all values must be filled as it is usual that stations
    # do not cover all metrics.
    def __init__(self):
        self.timestamp = None              # timestamp value []            
        self.hs = None                     # snow height [cm]
        self.hs24h = None                  # snow height difference 24h [cm]
        self.ta = None                     # air temperature [°C]
        self.tss = None                    # surface temperature [°C]
        self.td = None                     # dew point temperature [°C]
        self.vw = None                     # velocity wind [km/h]
        self.vwmax = None                  # velocity wind max [km/h]
        self.dw = None                     # direction wind [°]
        self.igr = None                    # incoming global radiation [W/m2]
        self.ogr = None                    # reflected global radiation [W/m2]
        self.rh = None                     # relative humidity [%]

    def measurement_as_dict(self):
        d = {}
        if self.timestamp:
            d["timestamp"] = int(self.timestamp)
        if self.hs:
            d["hs"] = round(float(self.hs),2)
        if self.hs24h:
            d["hs24h"] = round(float(self.hs24h),2)
        if self.ta:
            d["ta"] = round(float(self.ta),2)
        if self.tss:
            d["tss"] = round(float(self.tss),2)
        if self.td:
            d["td"] = round(float(self.td),2)
        if self.vw:
            d["vw"] = int(self.vw)
        if self.vwmax:
            d["vwmax"] = int(self.vwmax)
        if self.dw:
            d["dw"] = int(self.dw)
        if self.igr:
            d["igr"] = int(self.igr)
        if self.ogr:
            d["ogr"] = int(self.ogr)
        if self.rh:
            d["rh"] = round(float(self.rh),2)
        return d

    def __str__(self):
        retStr = " -> measurement@" + str(self.timestamp) + "\n"
        if self.hs:
            retStr += "snow height: " + str(self.hs) + "cm \n"
        if self.hs24h:
            retStr += "snow height difference 24h: " + str(self.hs24h) + "cm \n"
        if self.ta:
            retStr += "air temperature: " + str(self.ta) + "°C \n"
        if self.tss:
            retStr += "surface temperature: " + str(self.tss) + "°C \n"
        if self.td:
            retStr += "dew point temperature: " + str(self.td) + "°C \n"
        if self.vw:
            retStr += "wind speed: " + str(self.vw) + "km/h \n"
        if self.vwmax:
            retStr += "wind gust speed: " + str(self.vwmax) + "km/h \n"
        if self.dw:
            retStr += "direction wind " + str(self.dw) + "° \n"
        if self.igr:
            retStr += "incoming radiation: " + str(self.igr) + "W/m2 \n"
        if self.ogr:
            retStr += "outgoing radiation: " + str(self.ogr) + "W/m2 \n"
        if self.rh:
            retStr += "relative humidity: " + str(self.rh) + "% \n"
        return retStr
