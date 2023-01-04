from common.region import *
from core.processor_ch import *
from core.processor_fr import *
from core.processor_de_by import *
from core.processor_at_ti import *
from core.processor_at_vb import *
from core.processor_it_st import *

class Processor:
   def get_processor(region,conn):
      if(region is Region.Schweiz):
         return ProcessorCH(conn)
      if(region is Region.Tirol):
         return ProcessorTI(conn)
      if(region is Region.Vorarlberg):
         return ProcessorVB(conn)
      if(region is Region.Bayern):
         return ProcessorBY(conn)
      if(region is Region.Suedtirol):
         return ProcessorSTI(conn)
      if(region is Region.Frankreich):
         return ProcessorFR(conn)
