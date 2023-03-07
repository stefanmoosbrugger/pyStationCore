import pandas as pd
import datetime
import time
import json
import sys
import influxdb_client
from core.station import *
from core.measurement import *
from common.region import *


class InfluxDbClient:
    def open(self,url,tok,org,bucket,batchsize=500,maxretries=3):
        self.url = url
        self.tok = tok
        self.org = org
        self.bucket = bucket
        self.client = influxdb_client.InfluxDBClient(url=self.url, token=self.tok, org=self.org)
        self.write_api = self.client.write_api(write_options=influxdb_client.client.write_api.SYNCHRONOUS)
        self.query_api = self.client.query_api()
        self.batch = batchsize # defaults to 500. use smaller/larger values if required
        self.tries = maxretries # defaults to 3 (e.g., aws has write limits like 1MB/min)

    def write_station_data(self,station):
        stationMeta = station.meta_as_dict()
        mlist = station.measurements_as_list()
        if(len(mlist)==0):
            return
        data = []
        tags = stationMeta
        for m in mlist:
            entry = {
                "measurement": "meteo",
                "tags": tags,
                "fields": m,
                "time": m["timestamp"]
            }
            del entry["fields"]["timestamp"]
            data.append(entry)
        for sp in [data[i * self.batch:(i + 1) * self.batch] for i in range((len(data) + self.batch - 1) // self.batch )]:
            for i in range(self.tries):
                try:
                    self.write_api.write(bucket=self.bucket, org=self.org, record=sp, write_precision='s')
                except:
                    time.sleep(300)
                    if i < self.tries - 1: 
                        continue
                    else:
                        raise
                break

    def get_station_data(self,station,fromTs,toTs,aggregateWindow="30m",aggregateFunction="mean"):
        query = 'from(bucket: "stationdb")\
            |> range(start: '+str(fromTs)+', stop: '+str(toTs)+')\
            |> filter(fn: (r) => r.internalid == "'+station.id+'")\
            |> map(fn: (r) => ({\
                 _time: r._time,\
                 _measurement: r._field,\
                 _value: r._value\
             }))\
            |> aggregateWindow(every: '+aggregateWindow+', \
                fn: '+aggregateFunction+')\
            |> yield()'
        result = self.query_api.query(org=self.org, query=query)
        jsonres = json.loads(result.to_json())
        for result in jsonres:
            ts = time.mktime(pd.to_datetime(result["_time"]).timetuple())
            me = 0
            i = 0
            append = False
            while not me and i<len(station.data):
                if station.data[i].timestamp==ts:
                    me = station.data[i]
                else:
                    i = i+1
            if not me:
                me = Measurement()
                append = True
            me.timestamp = ts
            paramName = result["_measurement"]
            val = result["_value"]
            if val is None:
                continue
            if "hs" == paramName:
                me.hs = val
            if "ta" == paramName:
                me.ta = val
            if "td" == paramName:
                me.td = val
            if "tss" == paramName:
                me.tss = val
            if "rh" == paramName:
                me.rh = val
            if "vw" == paramName:
                me.vw = val
            if "vwmax" == paramName:
                me.vwmax = val
            if "dw" == paramName:
                me.dw = val
            if "ogr" == paramName:
                me.ogr = val
            if "igr" == paramName:
                me.igr = val
            if append:
                station.data.append(me)
            else:
                station.data[i] = me

    def get_all_stations(self,fromTs,toTs):
        query = 'from(bucket: "stationdb")\
            |> range(start: '+fromTs+', stop: '+toTs+')\
            |> keep(columns: ["_time", "internalid", "name", "region", "altitude", "longitude", "latitude"])\
            |> group(columns: ["internalid"])\
            |> last(column: "_time")\
            |> map(fn: (r) => ({\
                  _name: r.name,\
                  _latitude: float(v: r.latitude),\
                  _longitude: float(v: r.longitude),\
                  _altitude: float(v: r.altitude),\
                  _region: r.region,\
                  _internalid: r.internalid,\
              }))\
            |> unique(column: "_internalid")\
            |> yield()'
        result = self.query_api.query(org=self.org, query=query)
        stations = []
        jsonres = json.loads(result.to_json())
        for station in jsonres:
            stations.append(Station(
                station["_internalid"],
                station["_name"],
                station["_longitude"],
                station["_latitude"],
                station["_altitude"],
                Region[station["_region"][7:]]))
        return stations

    def write_event(self,station,event):
        data = []
        tags = { "stationid": station.id }
        entry = {
            "measurement": "event",
            "tags": tags,
            "fields": {
                str(event.name): event.level
            },
            "time": event.timestamp
        }
        self.write_api.write(bucket=self.bucket, org=self.org, record=entry, write_precision='s')
