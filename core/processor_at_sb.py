import json
import time
import datetime
import warnings
from utils.connection import *
from common.region import *
from core.station import *
from core.measurement import *

class ProcessorSBG:

    def __init__(self,conn):
        self.conn = conn
        self.baseUri = "https://www.salzburg.gv.at/lawine/"
        self.metricsWithName = ["Schneehöhe", "Lufttemperatur", "relative Feuchte", 
            "Windgeschwindigkeit", "Globalstrahlung (oben)", "Globalstrahlung (unten)"]

    def get_stations(self):
        # get stations of Tirol using the given conn
        uri = str(self.baseUri)+str("Station.js")
        response = self.conn.get_request(uri)[14:]
        decoded_response = json.loads(response)
        stations = []
        for region in decoded_response:
            for station in decoded_response[region]:
                # get station data
                if not "longitude" in station or not "latitude" in station or not "altitude" in station:
                    continue
                longi = str(station["longitude"])
                lati = str(station["latitude"])
                alti = float(str(station["altitude"]))
                i = 0
                # check if the station is a multi-station (e.g., snow + wind) 
                # if yes, separate the station into multiple stations. 
                if "title" in station:
                    for stn in station["title"].split("–"):
                        substationname = stn[:stn.rfind(" (")].strip()
                        # remove height indication as it is given in the coords 
                        if i>0:
                            for coord in station["geometry"]["coordinates"]:
                                if len(coord)>1 and str(int(coord[2])) in stn:
                                    longi = str(coord[0])
                                    lati = str(coord[1])
                                    alti = float(str(coord[2]))
                        # if additional station coordinates are given. find the 
                        # right ones (according to what is given as height and
                        # replace if possible
                        sid = "sb-"+str(station["name"])+"-"+str(station["id"])+"-"+str(i)
                        i = i+1
                        stations.append(Station(sid,substationname,longi,lati,alti,Region.Salzburg))
        return stations

    def get_data_for(self, station):
        # get data for a specific station of that region and store the time series
        # as a list of measurements objects in the station object.
        # get stations of Salzburg using the given conn
        if not station.region is Region.Salzburg:
            warnings.warn("Cannot use given processor (Salzburg) for station in region "+str(station.region))
            return
        name = station.id.split("-")[1]
        uri = str(self.baseUri)+str("grafiken/800/standard/7/"+name+str(".json"))
        response = self.conn.get_request(uri)
        decoded_response = json.loads(response)
        if not "data" in decoded_response:
            return
        record = False
        measurements = {}
        for f in decoded_response["data"]:
            # get data parameter from json and extract the name
            paramName = f["name"]
            # check if this param name is a named parameter (e.g., Schneehöhe Wasserfallboden)
            for namedParam in self.metricsWithName:
                if namedParam in paramName:
                    # it is a named parameter, replace it and see what is left
                    strippedParam = paramName.replace(namedParam,"").strip()
                    if strippedParam.endswith(station.name):
                        # the given station name matches the named param remainings.
                        # this means we record this and maybe the following params.
                        record = True
                    else:
                        # the given station name does not match the named param remainings.
                        # stop recording until the next named param appears
                        record = False
            if not record:
                # skip if the metric does not belong to the given station 
                continue
            for i in range(len(f["x"])):
                # iterate all timestamps in the data array 
                if i >= len(f["x"]):
                    # no value for the given timestamp 
                    continue
                ts = f["x"][i]
                val = f["y"][i]
                me = 0
                if ts in measurements:
                    # measurement exists for given ts 
                    me = measurements[ts]
                else:
                    # no measurement exists for given ts 
                    me = Measurement()
                    me.timestamp = str(ts)
                if "Schneehöhe" in paramName:
                    me.hs = val
                if "Lufttemperatur" in paramName:
                    me.ta = val
                if "Taupunkt" in paramName:
                    me.td = val
                if "Oberflächentemperatur" in paramName:
                    me.tss = val
                if "relative Feuchte" in paramName:
                    me.rh = val
                if "Windgeschwindigkeit" in paramName:
                    me.vw = val
                if "Windböe" in paramName:
                    me.vwmax = val
                if "Windrichtung" in paramName:
                    me.dw = val
                if "Globalstrahlung (unten)" in paramName:
                    me.ogr = val
                if "Globalstrahlung (oben)" in paramName:
                    me.igr = val
                measurements[ts] = me
        for ts in measurements:
            # adapt the timestamp as it has a non-standard format
            # and attach the measurement to the station 
            me = measurements[ts]
            me.timestamp = me.timestamp[:-3] 
            station.data.append(me)
            
