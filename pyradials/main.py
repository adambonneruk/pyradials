# default imports
import logging, sys, os, pathlib
from tabulate import tabulate
from datetime import datetime

# this projects imports
from cli import banner, draw_nice_line, print_gps, print_coordinates, print_stations, print_radials, print_control
from instrument import instrument_file_as_source
from calc import spherical_to_cartesian, dms_to_decimal, cartesian_to_spherical, horizontal_to_azimuth
from dxf import plot_dxf
from colour import Colour
from control import control

DEBUG_MODE = False
if DEBUG_MODE:
	logging.basicConfig(format='%(message)s', level=logging.DEBUG)

''' == PyRadials documentation / Notes ==

-- Instrument Source Format --

	source {
		'file_name': 'example.gsi',
		'format': 'Leica Geosystems 16-bit GSI (Geo Serial Interface)',
		'capture_date_time': '2024-03-03 01:50:45',
		'data': [
			{
				'station': 'STN1',
				'easting': 1000.0,
				'northing': 2000.0,
				'elevation': 50.0,
				'height': 1.555,
				'backsight': 'STN2',
				'date_time': '2024-03-09 16:53:32',
				'coded_measurements': [
					Coded_Measurement(
						point_id='STN2',
						code='RO',
						attrib='STN2',
						hz=187.161944,
						vt=94.013611,
						sd=16.285,
						th=0.1
					), Coded_Measurement(
						point_id=1,
						code='LS',
						attrib=None,
						hz=164.898333,
						vt=108.121111,
						sd=4.701,
						th=0.0
					)
				]
			}
		]
	}

-- PyRadials Project Format --

	project {
		'name': 'example survey'
		'datetime': '2024-03-03 01:50:45'
		'traversal'
		'measurements'
		'elevations'
		'drawings'
	}
'''

def main():

	colour = Colour() # initialise the colour object, this will allow us to print in colour
	banner()

	for argument in sys.argv[1:]:
		source = instrument_file_as_source(argument,True)

		print("\nfilename: %s" % source.get('file_name'))
		print("type: %s" % source.get('type'))
		print("format: %s" % source.get('format'))
		print("capture_date: %s" % source.get('capture_date_time'))
		draw_nice_line()

		if source['type'] == 'gps':
			print_gps(source)

		if source['type'] == 'total_station':
			print_coordinates(source)
			print_stations(source)
			print_control(control)
			radials = print_radials(source,control)

			plot_dxf(radials,100,pathlib.Path(argument).with_suffix('.dxf'))
			os.system("start %s " % pathlib.Path(argument).with_suffix('.dxf'))

	# End of Program
	print("\n")
