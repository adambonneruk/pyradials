import logging, sys, os
from tabulate import tabulate
from cli_functions import banner, draw_nice_line
from open_instrument_file import import_instrument_file
from math_functions import pad_decimal, spherical_to_cartesian, dms_to_decimal

DEBUG_MODE = True
if DEBUG_MODE:
	logging.basicConfig(format='%(message)s', level=logging.DEBUG)

''' == PyRadials documentation / Notes ==

-- Instrument Source Format --

	source {
		'filename': 'example.gsi',
		'process_datetime': '2024-03-03 01:50:45',
		'format': 'Leica Geosystems 16-bit GSI (Geo Serial Interface)',
		'instrument_serial_number': '626246',
		'setup': [
			station,backsight,instrument_height,station_easting,station_northing,station_elevation,shot[
				(shot_number,radius,inclination,azimuth,target_height,code)
				(shot_number,radius,inclination,azimuth,target_height,code)
				(shot_number,radius,inclination,azimuth,target_height,code)
			]
		]
	}
'''

def main():
	banner()

	for argument in sys.argv[1:]:
		observation = import_instrument_file(argument)

		print("filename: %s" % observation['filename'])
		print("format: %s" % observation['format'])

		draw_nice_line()

		print("\nStations:")
		for setup in observation['setup']:
			print(
				setup['station']
				+ '\t' + pad_decimal(setup['instrument_height'])
				+ '\t' + pad_decimal(setup['station_easting'])
				+ '\t' + pad_decimal(setup['station_northing'])
				+ '\t' + pad_decimal(setup['station_elevation'])
			)

		def print_tabulated_array(array, headers=None):
			if headers is None:
				headers = [f"Column {i+1}" for i in range(len(array[0]))]
			print(tabulate(array, headers=headers, tablefmt="grid"))

		'''print("\nCoordinates:")
		print_tabulated_array(
			observation['setup'][0]['shot'][:10],
			['Stn.','Code','Sd','V','Hz','Rh','X','Y','Z']
		)'''

		print("\nSpherical to Cartesian:")
		for shot in observation['setup'][0]['shot'][:10]:
			print(
				str(shot[0])
				+ '\t' + str(shot[1])
				+ '\t' + str(shot[2])
				+ '  ' + pad_decimal(shot[3])
				+ '  ' + pad_decimal(shot[4])
				+ '  ' + pad_decimal(shot[5])
				+ ' %.3f  %.3f  %.3f' % (spherical_to_cartesian(shot[2],shot[3],shot[4],1000,2000,50,1.609,shot[5]))
			)

	print('\n\n\n')

