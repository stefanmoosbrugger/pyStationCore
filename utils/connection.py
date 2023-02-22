import requests
from common.connection import *

class DefaultConnection:
    def raw_get_request(self,uri):
        # make get request using systems default 
        # connection and return the raw result
        return requests.get(uri)

    def get_request(self,uri):
        # make get request using systems default 
        # connection and return the response text
        r = requests.get(uri)
        return r.text

    def post_request(self,uri,cookies,headers,data):
        # make post request using systems default 
        # connection and return the response text
        r = requests.post(uri,cookies=cookies,headers=headers,data=data)
        return r.text

class Connection:
    def get_connection(conn):
        if(conn is ConnectionType.Default):
            return DefaultConnection()
        if(conn is ConnectionType.Tor):
            pass