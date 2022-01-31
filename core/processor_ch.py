import json
from utils.connection import *
from common.region import *
from core.station import *
from core.measurement import *

class ProcessorCH:

    def __init__(self,conn):
        self.conn = conn
        self.baseUri = "https://odb.slf.ch/api/v1/"

    def get_stations(self):
        # get stations of CH using the given conn
        response = self.conn.request(str(self.baseUri+"/spatial"))
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
            if not "id" in prop or not "label" in prop or not "type" in prop:
                continue
            # fetch id, label and type
            sid = prop["id"]
            name = prop["label"]
            stype = prop["type"]
            # only use the automatic weather stations
            if "AMS" in stype:
                stations.append(Station(sid,name,coord[0],coord[1],coord[2],Region.Schweiz))
        return stations

    def get_data_for(self, station):
        # get data for a specific station of that region and store the time series
        # as a list of measurements objects in the station object.
        response = self.conn.request(str(self.baseUri+"/measurement?id="+station.id))
        decoded_response = json.loads(response)
        for m in decoded_response:
            spm = m.split(";")
            conv = lambda i : i or None
            me = Measurement()
            me.timestamp = conv(spm[0])
            me.hs = conv(spm[1])
            me.hs24h = conv(spm[2])
            me.ta = conv(spm[3])
            me.tss = conv(spm[4])
            me.vw = conv(spm[5])
            me.vwmax = conv(spm[6])
            me.dw = conv(spm[7])
            station.data.append(me)
