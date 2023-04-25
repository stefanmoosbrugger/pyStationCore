import hashlib

def get_internal_id(name,lat,lng):
   encstr = name+str(round(float(lat),3))+str(round(float(lng),3))
   hash_object = hashlib.md5(encstr.encode())
   return "am-"+hash_object.hexdigest()
