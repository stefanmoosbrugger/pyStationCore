import time
import sys
import influxdb_client

class InfluxDbClient:
    def open(self,url,tok,org,bucket,batchsize=500,maxretries=3):
        self.url = url
        self.tok = tok
        self.org = org
        self.bucket = bucket
        self.client = influxdb_client.InfluxDBClient(url=self.url, token=self.tok, org=self.org)
        self.write_api = self.client.write_api(write_options=influxdb_client.client.write_api.SYNCHRONOUS)
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
            for key,val in m.items(): 
                if key=="timestamp":
                    # skip timestamp dict value as it is not a measurement
                    continue
                # write each measurement into the database.
                data.append({
                    "measurement": key,
                    "tags": tags,
                    "fields": { "value": val },
                    "time": m["timestamp"]
                })
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

    def get_station_data(self,station):
        raise NotImplementedError
