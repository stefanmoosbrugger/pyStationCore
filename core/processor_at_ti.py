import json
import time
import datetime
import warnings
from utils.connection import *
from common.region import *
from core.station import *
from core.measurement import *

class ProcessorTI:

    def __init__(self,conn):
        self.conn = conn
        self.baseUri = "https://static.avalanche.report/weather_stations/stations.geojson"
        self.response = None

    def retrieve_data(self):
        # tirol only requires a single request. all 
        # the data is contained in the response.
        # in order to renew the response retrieve_data can be called.
        self.response = self.conn.get_request(str(self.baseUri))

    def get_stations(self):
        # get stations of Tirol using the given conn
        if self.response is None:
            self.retrieve_data()
        decoded_response = json.loads(self.response)
        stations = []
        for f in decoded_response["features"]:
            # for each station entry fetch the relevant data
            if not "geometry" in f or not "properties" in f:
                continue
            # get geometry and properties
            geo = f["geometry"]
            prop = f["properties"]
            # in geo we're only interested in the coordinates.
            # if not existant, continue
            if not "coordinates" in geo:
                continue
            coord = geo["coordinates"]
            # in prop we're interested in the id, label and type.
            # if one is not existant, continue
            if not "name" in prop:
                continue
            # fetch id, name and
            regi = Region.Tirol
            if not "LWD-Region" in prop or not "AT-07" in prop["LWD-Region"]:
                if not "Warth" in prop["name"]:
                    continue
                else:
                    regi = Region.Vorarlberg
            # skip non tirol stations (except Warth. this is bad hack and 
            # we should get rid of that.)
            sid = f["id"]
            name = prop["name"]
            # only use the automatic weather stations
            stations.append(Station(sid,name,coord[0],coord[1],coord[2],regi))
        return stations

    def get_data_for(self, station):
        # get data for a specific station of that region and store the time series
        # as a list of measurements objects in the station object.
        # get stations of Tirol using the given conn
        if not station.region is Region.Tirol and not "Warth" in station.name:
            warnings.warn("Cannot use given processor (Tirol) for station in region "+str(station.region))
            return
        if self.response is None:
            self.retrieve_data()
        decoded_response = json.loads(self.response)
        for f in decoded_response["features"]:
            if "id" in f and f["id"]==station.id:
                me = Measurement()
                prop = f["properties"]
                # get timestamp
                if prop.get("date") is None:
                    return # if there is not date value return (non automatic measurement)
                unixepochts = datetime.datetime.fromisoformat(prop.get("date")).timestamp()
                me.timestamp = unixepochts
                # get incoming global radiation param
                me.igr = prop.get("GS_O")
                # get reflected global radiation param
                me.ogr = prop.get("GS_U")
                # get snow height
                me.hs = prop.get("HS")
                # get snow difference 24h
                me.hs24h = prop.get("HSD24")
                # get air temp
                me.ta = prop.get("LT")
                # get surface temp
                me.tss = prop.get("OFT")
                # get dewpoint temp
                me.td = prop.get("TD")
                # get relative humidity
                me.rh = prop.get("RH")
                # get windspeed
                me.vw = prop.get("WG")
                # get wind gust speed
                me.vwmax = prop.get("WG_BOE")
                # get wind direction
                me.dw = prop.get("WR")
                # append the measurement
                if not me.empty():
                    station.data.append(me)
                
                
