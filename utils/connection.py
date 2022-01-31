import requests
from common.connection import *

class DefaultConnection:
    def request(self,uri):
       # make request using systems default 
       # connection and return the response text
       r = requests.get(uri)
       return r.text

class Connection:
   def get_connection(conn):
      if(conn is ConnectionType.Default):
         return DefaultConnection()
      if(conn is ConnectionType.Tor):
         pass