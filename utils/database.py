from common.database import *
from utils.mongodb import *
from utils.influxdb import *

class Database:
    def get_database(db):
        if(db is DatabaseType.File):
            pass
        if(db is DatabaseType.MySql):
            pass
        if(db is DatabaseType.MongoDb):
            return MongoDbClient()
        if(db is DatabaseType.InfluxDb):
            return InfluxDbClient()
