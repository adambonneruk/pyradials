'''Convert OSGB36 (E,N using OSTN15 corrections) to W3W (with intermedia Lat/Long pair)
	- Latitude: Measured from Equator (53)
	- Longitude: Measured from Prime Meridian (-2)'''
import os
import what3words
from dotenv import load_dotenv
from convertbng.util import convert_lonlat

def unpack_long_lat_data(data):
    foo, = data[0]
    bar, = data[1]
    return foo, bar

# load env vars and configure w3w app key
load_dotenv()
w3w_app_key:str = os.getenv('W3W_APP_KEY')

def osgb360_to_w3w(easting:float,northing:float) -> str:
	# W3W works best if I go a meter north, box seems to fit better
	northing += 1

	# convert easting, northing to long, lat
	long_and_lat_res = convert_lonlat(easting,northing)
	long, lat = unpack_long_lat_data(long_and_lat_res)

	# pass app key to object, and make api call with lat & long
	geocoder = what3words.Geocoder(w3w_app_key)
	w3w_resp = geocoder.convert_to_3wa(what3words.Coordinates(lat,long))

	return "///" + w3w_resp['words'] # w3w branding

# Main block to execute if the script is run directly
if __name__ == "__main__":
	from gps import load_and_average_gps_csv_file
	filename = 'data/SROAD.csv'  # Replace 'data.csv' with your file name
	result = load_and_average_gps_csv_file(filename)

	for station, easting, northing, elevation in result[1:]:
		w3w_dot_string = osgb360_to_w3w(easting, northing)
		print(station, easting, northing, w3w_dot_string)