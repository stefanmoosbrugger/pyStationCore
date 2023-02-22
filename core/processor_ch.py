import json
import time
import datetime
from pyproj import Proj,transform
from utils.connection import *
from common.region import *
from core.station import *
from core.measurement import *

class ProcessorCH:

    def __init__(self,conn):
        self.conn = conn
        self.baseUri = "https://public-meas-data.slf.ch/public/station-data/"
        self.params = ["HEIGHT_NEW_SNOW_1D","SNOW_HEIGHT","TEMPERATURE_AIR","TEMPERATURE_SNOW_SURFACE","WIND_MEAN"]

    def get_stations(self):
        # get stations of CH using the given conn
        for p in self.params:
            response = self.conn.get_request(str(self.baseUri+"timepoint/"+p+"/current/geojson"))
            decoded_response = json.loads(response)
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
                if not "code" in prop or not "label" in prop:
                    continue
                # fetch id, label and type
                sid = prop["code"]
                name = prop["label"]
                network = prop["network"]
                # only use the automatic weather stations
                news = Station(sid,name,coord[0],coord[1],coord[2],Region.Schweiz)
                insert = True
                for s in stations:
                    if s.id==sid:
                        insert = False
                if insert:
                    stations.append(news)
        return stations

    def get_data_for(self, station):
        # get data for a specific station of that region and store the time series
        # as a list of measurements objects in the station object.
        network = "IMIS"
        if station.id.startswith("*"):
            network = "SMN"
        response = self.conn.get_request(str(self.baseUri+"timeseries/week/current/"+network+"/"+station.id))
        decoded_response = json.loads(response)
        timestamps = {}
        for m in decoded_response:
            if "windVelocityMean" in m:
                for val in decoded_response["windVelocityMean"]:
                    if "timestamp" in val and "value" in val:
                        ts = val["timestamp"]
                        if ts in timestamps:
                            timestamps[ts].vw = val["value"]
                        else:
                            me = Measurement()
                            me.timestamp = ts
                            me.vw = val["value"]
                            timestamps[ts] = me
            if "temperatureAir" in m:
                for val in decoded_response["temperatureAir"]:
                    if "timestamp" in val and "value" in val:
                        ts = val["timestamp"]
                        if ts in timestamps:
                            timestamps[ts].ta = val["value"]
                        else:
                            me = Measurement()
                            me.timestamp = ts
                            me.ta = val["value"]
                            timestamps[ts] = me
            if "windVelocityMax" in m:
                for val in decoded_response["windVelocityMax"]:
                    if "timestamp" in val and "value" in val:
                        ts = val["timestamp"]
                        if ts in timestamps:
                            timestamps[ts].vwmax = val["value"]
                        else:
                            me = Measurement()
                            me.timestamp = ts
                            me.vwmax = val["value"]
                            timestamps[ts] = me
            if "windDirectionMean" in m:
                for val in decoded_response["windDirectionMean"]:
                    if "timestamp" in val and "value" in val:
                        ts = val["timestamp"]
                        if ts in timestamps:
                            timestamps[ts].dw = val["value"]
                        else:
                            me = Measurement()
                            me.timestamp = ts
                            me.dw = val["value"]
                            timestamps[ts] = me
            if "snowHeight" in m:
                for val in decoded_response["snowHeight"]:
                    if "timestamp" in val and "value" in val:
                        ts = val["timestamp"]
                        if ts in timestamps:
                            timestamps[ts].hs = val["value"]
                        else:
                            me = Measurement()
                            me.timestamp = ts
                            me.hs = val["value"]
                            timestamps[ts] = me
            if "temperatureSnowSurface" in m:
                for val in decoded_response["temperatureSnowSurface"]:
                    if "timestamp" in val and "value" in val:
                        ts = val["timestamp"]
                        if ts in timestamps:
                            timestamps[ts].tss = val["value"]
                        else:
                            me = Measurement()
                            me.timestamp = ts
                            me.tss = val["value"]
                            timestamps[ts] = me
            if "heightNewSnow" in m:
                for val in decoded_response["heightNewSnow"]:
                    if "timestamp" in val and "value" in val:
                        ts = val["timestamp"]
                        if ts in timestamps:
                            timestamps[ts].hs24h = val["value"]
                        else:
                            me = Measurement()
                            me.timestamp = ts
                            me.hs24h = val["value"]
                            timestamps[ts] = me
        for ts in timestamps:
            oldts = timestamps[ts].timestamp
            unixepochts = time.mktime(datetime.datetime.strptime(oldts, "%Y-%m-%dT%H:%M:%S%z").timetuple())
            timestamps[ts].timestamp = unixepochts
            station.data.append(timestamps[ts])
