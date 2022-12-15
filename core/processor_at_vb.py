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

class ProcessorVB:

    def __init__(self,conn):
        self.conn = conn
        self.baseUri = "https://lawis.at/lawis_api/v2_2/station/"
   
    def get_stations(self):
        response = self.conn.request(str(self.baseUri)+"?_=0")
        decoded_response = json.loads(response)
        stations = []
        for f in decoded_response: 
            # for each station entry fetch the relevant data
            if not "country_id" in f or not "region_id" in f:
                continue
            # skip non vorarlberg stations
            country_id = f["country_id"]
            region_id = f["region_id"]
            if country_id != 1 or region_id != 2:
                continue
            # get station data
            name = f["ort"]
            sid = "vb-"+str(f["station_id"])
            alt = f["elevation"]
            lat = f["latitude"]
            lon = f["longitude"]
            stations.append(Station(sid,name,lon,lat,alt,Region.Vorarlberg))
        return stations

    def get_data_for(self,station):
        if not station.region is Region.Vorarlberg:
            warnings.warn("Cannot use given processor (Vorarlberg) for station in region "+str(station.region))
            return
        # get station specific uri
        sid = station.id[3:]
        uri = str(self.baseUri)+str(sid)+"?_=0"
        response = self.conn.request(uri)
        decoded_response = json.loads(response)
        alldata = []
        if "charts" in decoded_response:
            chart = decoded_response["charts"]
            if "1day" in chart:
                singleday = chart["1day"]
                if "link" in singleday:
                    # fetch data from chart viewer
                    link = singleday["link"]
                    response = self.conn.request(link)
                    soup = BeautifulSoup(response, 'html.parser')
                    alldata = soup.findAll('circle',attrs={'class': 'tip'})
        measurements = {}
        for m in alldata:
            # build the measurement structure
            dt = m.get("dt")
            if dt:
                dt = dt+"00" # provided timestamp has strange format
                param = m.get("dp")
                if not dt in measurements.keys():
                    measurements[dt] = {} 
                if "relative Feuchte" in param:
                    # fetch rh value
                    measurements[dt]["rh"] = m.get("dv")
                if "Schneehöhe" in param:
                    # fetch hs value
                    measurements[dt]["hs"] = m.get("dv")
                if "Windrichtung" in param:
                    # fetch dw value
                    measurements[dt]["dw"] = m.get("dv")
                if "Windböen" in param:
                    # fetch hs value
                    measurements[dt]["vwmax"] = m.get("dv")
                if "Windgeschw." in param:
                    # fetch hs value
                    measurements[dt]["vw"] = m.get("dv")
                if "Lufttemperatur" in param:
                    # fetch hs value
                    measurements[dt]["ta"] = m.get("dv")
        get_val = lambda l,k: l[k] if k in l.keys() else None
        for k,m in measurements.items():
            # each measurement in the structure is
            # appended to the station as a Measurement 
            # object
            me = Measurement()
            me.timestamp = k
            me.hs = get_val(m,"hs")
            me.ta = get_val(m,"ta")
            me.vw = get_val(m,"vw")
            me.vwmax = get_val(m,"vwmax")
            me.dw = get_val(m,"dw")
            me.rh = get_val(m,"rh")
            station.data.append(me)
           