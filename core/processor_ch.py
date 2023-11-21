import time
import json
import datetime
from pyproj import Proj,transform
from utils.connection import *
from common.region import *
from core.station import *
from core.measurement import *

class ProcessorCH:

    def __init__(self,conn):
        self.conn = conn
        self.baseUri = "https://measurement-api.slf.ch/public/api/"
        self.study_plots = []
        self.imis = []
        self.study_plots_data = None
        self.imis_data = None

    def get_measurement_data(self):
        if not self.study_plots_data:
            response = self.conn.get_request(str(self.baseUri)+"study-plot/measurements")
            decoded_response = json.loads(response)
            self.study_plots_data = decoded_response
        if not self.imis_data:
            response = self.conn.get_request(str(self.baseUri)+"imis/measurements")
            decoded_response = json.loads(response)
            self.imis_data = decoded_response        

    def get_stations(self):
        station_type = ["study-plot","imis"]
        stations = []
        for st in station_type:
            response = self.conn.get_request(str(self.baseUri)+st+"/stations")
            decoded_response = json.loads(response)
            required_fields = ["code","label","lon","lat","elevation"]
            for s in decoded_response:
                for p in required_fields:
                    if not p in s:
                        continue
                if station_type[0]==st:
                    self.study_plots.append(s["code"])
                if station_type[1]==st:
                    self.imis.append(s["code"])
                stations.append(Station(s["code"],s["label"],s["lon"],s["lat"],s["elevation"],Region.Schweiz))
        return stations

    def get_data_for(self, station):
        # get data for a specific station of that region and store the time series
        # as a list of measurements objects in the station object.
        self.get_measurement_data()
        if station.id in self.imis:
            for val in self.imis_data:
                if not "station_code" in val:
                    continue
                if not station.id==val["station_code"]:
                    continue
                # station_code is not existant or does not match
                me = Measurement()
                utc_time = datetime.datetime.fromisoformat(val["measure_date"].rstrip('Z'))
                epoch_time = utc_time.timestamp()
                me.timestamp = epoch_time
                # get timestamp
                if "HS" in val and not None is val["HS"]:
                    me.hs = val["HS"]
                if "HN_1D" in val and not None is val["HN_1D"]:
                    me.hs24h = val["HN_1D"]
                if "TA_30MIN_MEAN" in val and not None is val["TA_30MIN_MEAN"]:
                    me.ta = val["TA_30MIN_MEAN"]
                if "RH_30MIN_MEAN" in val and not None is val["RH_30MIN_MEAN"]:
                    me.rh = val["RH_30MIN_MEAN"]
                if "TSS_30MIN_MEAN" in val and not None is val["TSS_30MIN_MEAN"]:
                    me.tss = val["TSS_30MIN_MEAN"]
                if "RSWR_30MIN_MEAN" in val and not None is val["RSWR_30MIN_MEAN"]:
                    me.ogr = val["RSWR_30MIN_MEAN"]
                if "VW_30MIN_MEAN" in val and not None is val["VW_30MIN_MEAN"]:
                    me.vw = val["VW_30MIN_MEAN"]*3.6
                if "VW_30MIN_MAX" in val and not None is val["VW_30MIN_MAX"]:
                    me.vwmax = val["VW_30MIN_MAX"]*3.6
                if "DW_30MIN_MEAN" in val and not None is val["DW_30MIN_MEAN"]:
                    me.dw = val["DW_30MIN_MEAN"]
                # get measurements
                station.data.append(me)
                # append data
        if station.id in self.study_plots:
            for val in self.study_plots_data:
                if not "station_code" in val:
                    continue
                if not station.id==val["station_code"]:
                    continue
                # station_code is not existant or does not match
                me = Measurement()
                utc_time = datetime.datetime.fromisoformat(val["measure_date"].rstrip('Z'))
                epoch_time = utc_time.timestamp()
                me.timestamp = epoch_time
                # get timestamp
                if "HS" in val and not None is val["HS"]:
                    me.hs = val["HS"]
                if "HN_1D" in val and not None is val["HN_1D"]:
                    me.hs24h = val["HN_1D"]
                # get measurements
                station.data.append(me)
                # append data
