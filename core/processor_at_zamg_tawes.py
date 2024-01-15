import json
import re
import demjson
import time
import datetime
import warnings
from bs4 import BeautifulSoup
from utils.connection import *
from common.region import *
from core.station import *
from core.measurement import *

class ProcessorCurrentZAMG:

    def __init__(self,conn,subregion):
        self.conn = conn
        self.subreg = subregion
        self.baseUri = "https://dataset.api.hub.geosphere.at/v1/station/current/tawes-v1-10min"
        self.stations = []
        self.response = None

    def retrieve_data(self):
        # only make a single request. all 
        # the data is contained in the response.
        sids = ""
        if len(self.stations):
            sids = self.stations[0].id[5:]
        for station in self.stations[1:]:
            sids += ","
            sids += station.id[5:]
        uri = str(self.baseUri+"?parameters=DD&parameters=FFAM&parameters=FFX"+
            "&parameters=GLOW&parameters=RFAM"+
            "&parameters=SCHNEE&parameters=TL&parameters=TP"+
            "&station_ids="+str(sids)+
            "&output_format=geojson")        
        self.response = json.loads(self.conn.get_request(uri))
 
    def get_name_for_region(self):
      if self.subreg == Region.Vorarlberg:
         return "Vorarlberg"
      if self.subreg == Region.Tirol:
         return "Tirol"
      if self.subreg == Region.Salzburg:
         return "Salzburg"
      if self.subreg == Region.Steiermark:
         return "Steiermark"
      if self.subreg == Region.Kaernten:
         return "Kärnten"
      return "None"

    def get_stations(self):
        response = self.conn.get_request(str(self.baseUri)+"/filter?state="+self.get_name_for_region())
        decoded_response = json.loads(response)
        self.stations = []
        self.response = None

        if "matching_stations" in decoded_response:
            ms = decoded_response["matching_stations"]
            for f in ms:
                # get station data
                name = f["name"].title()
                sid = "zamg-"+str(f["id"])
                alt = f["altitude"]
                lat = f["lat"]
                lon = f["lon"]
                self.stations.append(Station(sid,name,lon,lat,alt,self.subreg))
        return self.stations

    def get_data_for(self,station):
        if self.get_name_for_region() == "None" or not station.region is self.subreg:
            warnings.warn("Cannot use given processor ("+self.get_name_for_region()+") for station in region "+str(station.region))
            return
        if not self.response:
            self.retrieve_data()
        
        decoded_response = self.response
        sid = station.id[5:]

        if not "features" in decoded_response:
            return

        i = 0
        for ts in decoded_response["timestamps"]:
            datetime_obj = datetime.datetime.fromisoformat(ts)
            epoch_timestamp = datetime_obj.replace(tzinfo=datetime.timezone.utc).timestamp()
            me = Measurement()
            me.timestamp = epoch_timestamp
            feat = None
            for f in decoded_response["features"]:
                if feat:
                    continue
                if not "properties" in f:
                    continue
                if not "station" in f["properties"]:
                    continue
                if f["properties"]["station"]==sid:
                    feat = f
            for param in feat["properties"]["parameters"]:
                val = feat["properties"]["parameters"][param]["data"][i]
                if val == None:
                    continue
                if "DD" in param:
                    me.dw = float(val)
                if "FFAM" in param:
                    me.vw = float(val)*3.6
                if "FFX" in param:
                	me.vwmax = float(val)*3.6
                if "GLOW" in param:
                	me.igr = float(val)
                if "RFAM" in param:
                	me.rh = float(val)
                if "SCHNEE" in param:
                	me.hs = float(val)
                if "TL" in param:
                	me.ta = float(val)
                if "TP" in param:
                	me.td = float(val)
            if not me.empty():
                station.data.append(me)
            i += 1

