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

class ProcessorFR:

    def __init__(self,conn):
        self.conn = conn
        self.baseUri = "http://iav-portal.com/index.php?"

    def get_stations(self):
        response = self.conn.get_request(str(self.baseUri)+"nav=data_meteo_stations&lang=en")
        soup = BeautifulSoup(response, 'html.parser')
        alldata = soup.findAll('tr')
        station_codes = []
        for i in alldata[1:]:
            tds = i.findChildren('td')
            code = ""
            if len(tds)==0 or len(tds[0])==0: 
                continue
            if len(tds)>=2 and not "France" in tds[2]: 
                continue
            if len(tds)>=7 and not "green" in str(tds[7]): 
                continue
            station_codes.append(tds[0].get_text())
        stations = []
        for c in station_codes:
            resp = self.conn.get_request(str(self.baseUri)+"nav=data_meteo_station&lang=en&code="+str(c))
            stationd = BeautifulSoup(resp, 'html.parser')
            data = stationd.findAll('td',{'valign':'top','align':'left','colspan':'2'})[0]
            trs = data.findChildren('tr')
            sid = "fr-"+str(c)
            name = ""
            lat = ""
            lng = ""
            alt = 0
            for x in trs:
                tds = x.findChildren('td')
                if len(tds)>=2:
                    if "Site" in tds[0].get_text():
                        name = tds[2].get_text()
                    if "Latitude" in tds[0].get_text():
                        lat = tds[2].get_text()
                    if "Longitude" in tds[0].get_text():
                        lng = tds[2].get_text()
                    if "Altitude" in tds[0].get_text():
                        alt = tds[2].get_text()[0:-4]
            stations.append(Station(sid,name,lng,lat,alt,Region.Frankreich))
        return stations

    def get_data_for(self,station):
        if not station.region is Region.Frankreich:
            warnings.warn("Cannot use given processor (Frankreich) for station in region "+str(station.region))
            return
        # get station specific uri
        sid = station.id[3:]
        uri = "http://www.iav-portal.com/isaw/idod/idod.php?s="+str(sid)+"&f=json&d=1"
        response = self.conn.get_request(uri)
        decoded_response = json.loads(response)
        if decoded_response is None or decoded_response.get("lastdata") is None:
            return 
        if decoded_response.get("measures") is None:
            return 
        me = Measurement()
        tsval = decoded_response.get("lastdata")
        tsval.replace(" ","T")
        tsval = tsval+"+01:00"
        # stupid timevalue string modifications. 
        ts = datetime.datetime.fromisoformat(tsval).timestamp()
        vals = decoded_response.get("measures")

        me.timestamp = ts
        get_val = lambda i: vals.get(i)[0] if not vals.get(i) is None and len(vals.get(i)) else None
        # get snow height
        me.hs = get_val("snow_height_seg1_nc")
        # get air temp
        me.ta = get_val("air_temperature_mean_nc")
        # get surface temp
        me.tss = get_val("ground_temperature_mean_nc")
        # get windspeed
        me.vw = get_val("wind_speed_mean_young")
        # get wind gust speed
        me.vwmax = get_val("wind_speed_maxi_young")
        # get wind direction
        me.dw = get_val("wind_direction_mini_young")
        # append the measurement
        station.data.append(me)
