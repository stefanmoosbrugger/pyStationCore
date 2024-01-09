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

    def get_name_for_region(self):
      if self.subreg == Region.Vorarlberg:
         return "Vorarlberg"
      return "None"

    def get_stations(self):
        response = self.conn.get_request(str(self.baseUri)+"/filter?state="+self.get_name_for_region())
        decoded_response = json.loads(response)
        stations = []
        if "matching_stations" in decoded_response:
            ms = decoded_response["matching_stations"]
            for f in ms:
                # get station data
                name = f["name"].title()
                sid = "zamg-"+str(f["id"])
                alt = f["altitude"]
                lat = f["lat"]
                lon = f["lon"]
                stations.append(Station(sid,name,lon,lat,alt,self.subreg))
        return stations

    def get_data_for(self,station):
        if self.get_name_for_region() == "None" or not station.region is self.subreg:
            warnings.warn("Cannot use given processor ("+self.get_name_for_region()+") for station in region "+str(station.region))
            return
        sid = station.id[5:]
        currdate = datetime.datetime.now().strftime("%Y-%m-%d")
        prevdate = (datetime.datetime.now()-datetime.timedelta(days=2)).strftime("%Y-%m-%d")        
        uri = str(self.baseUri+"?parameters=DD&parameters=FFAM&parameters=FFX"+
            "&parameters=GLOW&parameters=RFAM"+
            "&parameters=SCHNEE&parameters=TL&parameters=TP"+
            "&station_ids="+str(sid)+
            "&output_format=geojson")
        response = self.conn.get_request(uri)
        decoded_response = json.loads(response)
        if not "features" in decoded_response:
            return

        i = 0
        for ts in decoded_response["timestamps"]:
            datetime_obj = datetime.datetime.fromisoformat(ts)
            epoch_timestamp = datetime_obj.replace(tzinfo=datetime.timezone.utc).timestamp()
            me = Measurement()
            me.timestamp = epoch_timestamp
            feat = decoded_response["features"][0]
            for param in feat["properties"]["parameters"]:
                val = feat["properties"]["parameters"][param]["data"][i]
                if val == None:
                    continue
                if "DD" in param:
                    me.ta = float(val)
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

