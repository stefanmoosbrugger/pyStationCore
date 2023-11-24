import json
import re
import time
import datetime
import pytz
import warnings
from utils.connection import *
from common.region import *
from core.station import *
from core.measurement import *


def parse_height(s):
    numbers = re.findall(r'\d+', s)
    if numbers:
        return numbers[0]
    else:
        return None

class ProcessorBY:

    def __init__(self,conn):
        self.conn = conn
        self.baseUri = "https://api-la-dok.bayern.de/public"
   
    def get_stations(self):
        stations = []
        response = self.conn.get_request(str(self.baseUri)+"/weatherstations/all/")
        if response is None:
            return stations
        decoded_response = json.loads(response)
        for station in decoded_response:
            #print(station)
            sid = station["stationId"]
            name = station["name"]
            lat = station["position"]["lat"]
            lng = station["position"]["lng"]
            alt = parse_height(station["altitude"])
            # the station sensors are sometimes located in different places
            # (e.g., wind and snow data). unfortunately this is not reflected
            # in the location data provided in points. therefore we use the
            # first altitude data that is given (e.g., Herzogstand 1575/1625m is
            # assumed to be located ar 1575m).
            stations.append(Station(sid,name,lng,lat,alt,Region.Bayern))
        return stations; 

    def get_data_for(self,station):
        if not station.region is Region.Bayern:
            warnings.warn("Cannot use given processor (Bayern) for station in region "+str(station.region))
            return
        response = self.conn.get_request(str(self.baseUri+"/weatherWeb/"+station.id))
        decoded_response = json.loads(response)
        for val in decoded_response:
            if not "ID" in val:
                continue
            if not station.id==val["ID"]:
                continue
            # station_code is not existant or does not match
            me = Measurement()
            datestr = datetime.datetime.strptime(val["TS"], '%Y-%m-%d %H:%M:%S')
            datestrde = pytz.timezone('Europe/Berlin').localize(datestr)
            datestrutc = datestrde.astimezone(pytz.utc)
            utcts = datestrutc.timestamp()
            me.timestamp = utcts
            # get timestamp
            if "ff" in val and not None is val["ff"]:
                me.vw = float(val["ff"])*3.6 # values are given in m/s
            if "ffBoe" in val and not None is val["ffBoe"]:
                me.vwmax = float(val["ffBoe"])*3.6 # values are given in m/s
            if "dd" in val and not None is val["dd"]:
                me.dw = val["dd"]
            if "TL" in val and not None is val["TL"]:
                me.ta = val["TL"]
            if "TO" in val and not None is val["TO"]:
                me.tss = val["TO"]
            if "HS" in val and not None is val["HS"]:
                me.hs = val["HS"]
            # get measurements
            station.data.append(me)
            # append data


