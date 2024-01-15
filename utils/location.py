from core.station import *
from utils.idhash import *

def are_stations_locations_approximately_same(station1, station2, lat_lon_tolerance=0.02, alt_tolerance=50):
    # Interne IDs generieren
    id1 = get_internal_id(station1.name, station1.lat, station1.long)
    id2 = get_internal_id(station2.name, station2.lat, station2.long)

    # Prüfen, ob die IDs gleich sind
    if id1 == id2:
        return True

    # Näherungsweise Gleichheit prüfen
    lat_close = abs(station1.lat - station2.lat) <= lat_lon_tolerance
    lon_close = abs(station1.long - station2.long) <= lat_lon_tolerance
    alt_close = abs(station1.altitude - station2.altitude) <= alt_tolerance

    return lat_close and lon_close and alt_close
