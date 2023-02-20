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

def flatten(t):
    return [item for sublist in t for item in sublist]

class ProcessorBY:

    def __init__(self,conn):
        self.conn = conn
        self.baseUri = "https://www.lawinenwarndienst-bayern.de/res/daten_meldungen/messdaten/"
   
    def get_stations(self):
        response = self.conn.request(str(self.baseUri))
        pointsfinder = re.findall(r'var points = [^;]*',response,flags=re.DOTALL)
        contentsfinder = re.findall(r'var contents = \[.*\];',response,flags=re.DOTALL)
        points = pointsfinder[0].split("var points = ")[1]
        contents = contentsfinder[0].split("var contents = ")[1]
        pstr = "".join(points.split())[:-3][2:]
        pstr = pstr.replace("'",'"')
        points = json.loads(str("[["+pstr+"]]"))
        stations = []
        for station in points:
           name = station[0]
           # dirty way to extract altitude data from javascript array
           # named "contents". seems to be static content as it did not 
           # change since january 2022. 
           pos = contents.find(name)
           alti = 0
           if pos > -1:
              pos = pos+len(name)+9 # name</span>, 
              if contents[pos:pos+4].isdigit():
                alti = contents[pos:pos+4]
           lat = station[1]
           longi = station[2]
           sid = station[4]
           # the station sensors are sometimes located in different places
           # (e.g., wind and snow data). unfortunately this is not reflected
           # in the location data provided in points. therefore we use the
           # first altitude data that is given (e.g., Herzogstand 1575/1625m is
           # assumed to be located ar 1575m).
           stations.append(Station(sid,name,longi,lat,alti,Region.Bayern))
        return stations; 

    def get_data_for(self,station):
        if not station.region is Region.Bayern:
            warnings.warn("Cannot use given processor (Bayern) for station in region "+str(station.region))
            return
        response = self.conn.request(str(self.baseUri+"messstation.php?rid="+station.id))
        # find the timesteps used in the diagrams and convert to unix epoch time
        timearr = re.findall(r'zeitarr\[.+?(?=;)',response,flags=re.DOTALL)
        timesteps = []
        for t in timearr:
            if "zeitarr[this.point.myIndex]" in str(t):
                continue
            timeval = t.split("'")[1].replace("<b>","").replace(" Uhr</b>","")
            unixepochts = time.mktime(datetime.datetime.strptime(timeval, "%d.%m.%y %H:%M").timetuple())
            now = time.mktime(datetime.datetime.now().timetuple())
            if (now-unixepochts)>0:
                # do not append future timesteps (diagram is always for 2 days)
                timesteps.append(unixepochts)
         # find series of different values (e.g., temp, windspeed, etc.)
        hs = []
        hs24h = []
        ta = []
        tss = []
        vw = []
        vwmax = []
        dw = []
        # dw has to be treated differently
        dwarr = re.findall(r'windrichtung\[.+?(?=;)',response,flags=re.DOTALL)
        for dwval in dwarr:
            if "windrichtung[this.point.myIndex]" in str(dwval):
                continue
            if len(dw)<(len(timesteps)-1):
                if "null" in str(dwval):
                    dw.append(None) # wind measurement error. append a None entry
                else:
                    dwval = dwval.split(" ")[4]
                    dw.append(dwval)
        # get remaining values from series data
        finder = re.findall(r'series: .+?(?=}\);)',response,flags=re.DOTALL)
        for f in finder:
            newstr = str("{"+f+"}").replace("prepare(","").replace("])}","]}")
            parsed_json = demjson.decode(newstr)
            for ts in parsed_json["series"]:
                n = ts["name"]
                if "Windgeschwindigkeit" in n:
                    # fetch all vw values
                    for val in flatten(ts["data"]):
                        if len(vw)<(len(timesteps)-1):
                            vw.append(val)
                if "Böengeschwindigkeit" in n:
                    # fetch all vwmax values
                    for val in ts["data"]:
                        if len(vwmax)<(len(timesteps)-1):
                            vwmax.append(val)
                if "Oberflächentemperatur" in n:
                    # fetch all tss values
                    for val in flatten(ts["data"]):
                        if len(tss)<(len(timesteps)-1):
                            tss.append(val)
                if "Lufttemperatur" in n:
                    # fetch all ta values
                    for val in flatten(ts["data"]):
                        if len(ta)<(len(timesteps)-1):
                            ta.append(val)
                if "Schneehöhe" in n:
                    # fetch all ta values
                    for val in flatten(ts["data"]):
                        if len(hs)<(len(timesteps)-1):
                            hs.append(val)
        i = 0
        for ts in timesteps:
            get_val = lambda l,i: l[i] if i<len(l) else None
            me = Measurement()
            me.timestamp = ts
            me.hs = get_val(hs,i)
            me.hs24h = get_val(hs24h,i)
            me.ta = get_val(ta,i)
            me.tss = get_val(tss,i)
            me.vw = get_val(vw,i)
            me.vwmax = get_val(vwmax,i)
            me.dw = get_val(dw,i)
            station.data.append(me)
            i += 1
           