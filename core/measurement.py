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
        if not self.timestamp is None:
            d["timestamp"] = int(self.timestamp)
        if not self.hs is None:
            d["hs"] = round(float(self.hs),2)
        if not self.hs24h is None:
            d["hs24h"] = round(float(self.hs24h),2)
        if not self.ta is None:
            d["ta"] = round(float(self.ta),2)
        if not self.tss is None:
            d["tss"] = round(float(self.tss),2)
        if not self.td is None:
            d["td"] = round(float(self.td),2)
        if not self.vw is None:
            d["vw"] = int(self.vw)
        if not self.vwmax is None:
            d["vwmax"] = int(self.vwmax)
        if not self.dw is None:
            d["dw"] = int(self.dw)
        if not self.igr is None:
            d["igr"] = int(self.igr)
        if not self.ogr is None:
            d["ogr"] = int(self.ogr)
        if not self.rh is None:
            d["rh"] = round(float(self.rh),2)
        return d

    def empty(self):
        return len(self.measurement_as_dict())<=1

    def __str__(self):
        retStr = " -> measurement@" + str(self.timestamp) + "\n"
        if not self.hs is None:
            retStr += "snow height: " + str(self.hs) + "cm \n"
        if not self.hs24h is None:
            retStr += "snow height difference 24h: " + str(self.hs24h) + "cm \n"
        if not self.ta is None:
            retStr += "air temperature: " + str(self.ta) + "°C \n"
        if not self.tss is None:
            retStr += "surface temperature: " + str(self.tss) + "°C \n"
        if not self.td is None:
            retStr += "dew point temperature: " + str(self.td) + "°C \n"
        if not self.vw is None:
            retStr += "wind speed: " + str(self.vw) + "km/h \n"
        if not self.vwmax is None:
            retStr += "wind gust speed: " + str(self.vwmax) + "km/h \n"
        if not self.dw is None:
            retStr += "direction wind " + str(self.dw) + "° \n"
        if not self.igr is None:
            retStr += "incoming radiation: " + str(self.igr) + "W/m2 \n"
        if not self.ogr is None:
            retStr += "outgoing radiation: " + str(self.ogr) + "W/m2 \n"
        if not self.rh is None:
            retStr += "relative humidity: " + str(self.rh) + "% \n"
        return retStr
