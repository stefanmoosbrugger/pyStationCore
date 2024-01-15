import json
import time
import datetime
import warnings
from bs4 import BeautifulSoup
from utils.connection import *
from common.region import *
from core.station import *
from core.measurement import *

class ProcessorAOS:

    def __init__(self,conn):
        self.conn = conn
        self.baseUri = "https://presidi2.regione.vda.it/"
        self.response = None

        self.cookies = { }
        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': str(self.baseUri),
            'Referer': str(self.baseUri)+"str_dataview",
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 OPR/94.0.0.0',
            'X-CSRF-Token': '0',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Chromium";v="108", "Opera";v="94", "Not)A;Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
        }
        self.data = {'params': '[]',}

    def fetch_cookie_and_csrf(self):
        # get protection cookie in order to be able to retrieve the data
        # and extract the csrf token.
        response = self.conn.raw_get_request(self.baseUri+'str_dataview')
        self.cookies = response.cookies.get_dict()
        csrf_start = response.text.find("X-CSRF-Token")+13
        csrf_tok_start = response.text.find("'",csrf_start)+1
        csrf_tok_end = response.text.find("'",csrf_tok_start)
        csrf_tok = response.text[csrf_tok_start:csrf_tok_end]
        if len(csrf_tok)==40:
            self.headers["X-CSRF-Token"] = csrf_tok

    def get_stations(self):
        # get stations of Aosta using the given conn
        if len(self.cookies)==0:
            self.fetch_cookie_and_csrf()
        response = self.conn.post_request(
            self.baseUri+'str_dataview_get_map_stations',
            cookies=self.cookies,
            headers=self.headers,
            data=self.data)
        decoded_response = json.loads(response)
        if not "stations" in decoded_response:
            return
        stations = []
        for station in decoded_response["stations"]:
            internalid = "it-aosta-"+str(station["marker_id"])
            name = station["marker_name"]
            lati = station["marker_lat"]
            longi = station["marker_lon"]
            alti = 0
            altiresp = self.conn.get_request(str(self.baseUri)+str("str_dataview_station/")+str(station["marker_id"]))
            soup = BeautifulSoup(altiresp, 'html.parser')
            alldata = soup.findAll('tr')
            quotaFound = False
            for x in alldata:
                if not quotaFound and "Quota" in str(x):
                    quotaFound = True
                    mpos = str(x).find("m s.l.m")
                    tdpos = str(x).rfind(">",0,mpos)
                    alti = str(x)[tdpos+1:mpos].strip()
                    if not alti.isdigit():
                        # no altitude info found. set to 0.
                        alti = 0
            stations.append(Station(internalid,name,longi,lati,alti,Region.Aosta))
        return stations    

    def get_data_for(self, station):
        # get data for a specific station of that region and store the time series
        # as a list of measurements objects in the station object.
        # get stations of Aosta using the given conn
        if not station.region is Region.Aosta:
            warnings.warn("Cannot use given processor (Aosta) for station in region "+str(station.region))
            return
        if len(self.cookies)==0:
            self.fetch_cookie_and_csrf()
        postdata = self.data
        now = datetime.datetime.now()
        nowstr = now.strftime("%Y-%m-%d %H:00:00")
        twodaysago = now - datetime.timedelta(days=2)
        twodaysagostr = twodaysago.strftime("%Y-%m-%d %H:00:00")
        iid = str(station.id)[station.id.rfind("-")+1:].strip()
        postdata = {
            'id': iid,
            'aggr': 'hh',
            'from': twodaysagostr,
            'to': nowstr,
        }
        response = self.conn.post_request(
            self.baseUri+'str_dataview_get_allparams_data',
            cookies=self.cookies,
            headers=self.headers,
            data=postdata)
        decoded_response = json.loads(response)
        if not "data" in decoded_response:
            return
        measurements = {}
        for dataElem in decoded_response["data"]:
            paramName = dataElem["parameter_name"]
            for tsValPair in dataElem["station_param_values"]:
                ts = tsValPair[0]
                val = tsValPair[1]
                if val is None:
                    continue
                if not ts in measurements:
                    measurements[ts] = Measurement()
                    measurements[ts].timestamp = str(ts)
                me = measurements[ts]
                if "Temperatura" in paramName:
                    me.ta = val
                if "Umidità relativa" in paramName:
                    me.rh = val
                if "Radiazione totale" in paramName:
                    me.igr = val
                if "Radiazione riflessa" in paramName:
                    me.ogr = val
                if "Direzione Vento Vett." in paramName:
                    me.dw = val
                if "Velocità Vento Vett." in paramName:
                    me.vw = float(val)*3.6 # wind speed in km/h
                if "Altezza neve al suolo" in paramName:
                    me.hs = val
                measurements[ts] = me
        for ts in measurements:
            # adapt the timestamp as it has a non-standard format
            # and attach the measurement to the station 
            me = measurements[ts]
            me.timestamp = str(me.timestamp)[:-5] 
            if not me.empty():
                station.data.append(me)
