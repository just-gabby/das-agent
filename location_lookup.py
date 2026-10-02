import csv
from math import radians, sin, cos, sqrt, atan2

# NaPTAN StopType codes for the kinds of stop we care about
RAIL_CODES = {"RLY", "RSE"}   # railway station / station entrance
BUS_CODES = {"BCT", "BST", "BCS", "BCQ", "BCE"}  # bus stop / bus station

def haversine(lat1, lon1, lat2, lon2):
    """Straight-line distance between two points on Earth, in km."""
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

def find_field(fieldnames, target):
    """Match a column name regardless of whether the file uses lower or UPPER case."""
    lookup = {name.lower(): name for name in fieldnames}
    return lookup.get(target.lower())

def get_postcode_coords(postcode, onspd_rows, onspd_fieldnames):
    pcd_field = find_field(onspd_fieldnames, "pcds")
    lat_field = find_field(onspd_fieldnames, "lat")
    long_field = find_field(onspd_fieldnames, "long")

    postcode_clean = postcode.upper().replace(" ", "")
    for row in onspd_rows:
        if row[pcd_field].upper().replace(" ", "") == postcode_clean:
            return float(row[lat_field]), float(row[long_field])
    return None

def find_nearest_by_type(lat, lon, naptan_rows, naptan_fieldnames, allowed_codes):
    name_field = find_field(naptan_fieldnames, "CommonName")
    lat_field = find_field(naptan_fieldnames, "Latitude")
    long_field = find_field(naptan_fieldnames, "Longitude")
    type_field = find_field(naptan_fieldnames, "StopType")

    nearest_name, nearest_distance = None, float("inf")
    for row in naptan_rows:
        if row.get(type_field) not in allowed_codes:
            continue
        try:
            distance = haversine(lat, lon, float(row[lat_field]), float(row[long_field]))
        except (ValueError, KeyError):
            continue
        if distance < nearest_distance:
            nearest_name, nearest_distance = row[name_field], distance
    return nearest_name, round(nearest_distance, 2)