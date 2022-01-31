from common.region import *
from core.processor_ch import *
from core.processor_by import *
from core.processor_ti import *

class Processor:
   def get_processor(region,conn):
      if(region is Region.Schweiz):
         return ProcessorCH(conn)
      if(region is Region.Tirol):
         return ProcessorTI(conn)
      if(region is Region.Vorarlberg):
         pass
      if(region is Region.Bayern):
         return ProcessorBY(conn)
