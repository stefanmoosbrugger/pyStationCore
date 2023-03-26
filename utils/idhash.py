import hashlib

def get_internal_id(name,lat,lng):
   encstr = name+str(lat)+str(lng)
   hash_object = hashlib.md5(encstr.encode())
   return hash_object.hexdigest()
