import pandas as pd
import numpy as np
import datetime
from pygam import GAM, LinearGAM, s, f, l
import matplotlib.pyplot as plt

class HsGam:
   def __init__(self):
      self.result = {}
      self.gam = None
      self.XX = None
      self.y = None

   def get_df_from_stations(self,stations):
      df = pd.DataFrame()
      today = datetime.datetime.now().date()
      for station in stations:
         if station.data is None or len(station.data)==0:
            # no measurement
            continue
         if station.data[-1].hs is None:
            # no hs value
            continue
         dt_object = datetime.datetime.fromtimestamp(station.data[-1].timestamp)
         if dt_object.date()!=today:
            # no current hs value
            continue
         df2 = pd.DataFrame(data=
            {'alt':[station.altitude],
             'hs':[station.data[-1].hs]})
         df = pd.concat([df,df2],ignore_index=True)
      zeroValDf = pd.DataFrame(data={'alt':[0,300],'hs':[0,0]})
      df = pd.concat([df,zeroValDf],ignore_index=True)
      return df

   def generate_hsgam(self,stations):
      df = self.get_df_from_stations(stations)

      X = df.drop(['hs'],axis=1).values
      y = df['hs']

      self.gam =  GAM(s(0)).gridsearch(X, y, lam=[1,2])
      self.XX = self.gam.generate_X_grid(term=0)
      self.y = self.gam.predict(self.XX)

   def return_hs_dict(self):
      # return a dict that represents predicted snow heights for 
      # the given interval and stepsize.
      res = {}
      res["data"] = []
      for i in range(0,len(self.XX)):
         dataval = {
            "alt":round(float(self.XX[i][0]),0),
            "hs":round(float(max(0,self.y[i])),0) }
         res["data"].append(dataval)
      return res
