import logging, sys, os
from tabulate import tabulate
from cli import banner, draw_nice_line
from instrument import instrument_file
from calc import spherical_to_cartesian, dms_to_decimal, cartesian_to_spherical, horizontal_to_azimuth
from colour import Colour
from control import control

DEBUG_MODE = True
if DEBUG_MODE:
	logging.basicConfig(format='%(message)s', level=logging.INFO)

''' == PyRadials documentation / Notes ==

-- Instrument Source Format --

	source {
		'filename': 'example.gsi',
		'process_datetime': '2024-03-03 01:50:45',
		'format': 'Leica Geosystems 16-bit GSI (Geo Serial Interface)',
		'instrument_serial_number': '626246',
		'capture_datetime': '2024-03-03 01:50:45',
		'setup': [
			station,backsight,instrument_height,station_easting,station_northing,station_elevation,shot[
				(shot_number,radius,inclination,azimuth,target_height,code)
				(shot_number,radius,inclination,azimuth,target_height,code)
				(shot_number,radius,inclination,azimuth,target_height,code)
			]
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

	banner()
	colour = Colour() # initialise a colour object, this will allow us to print in colour

	for argument in sys.argv[1:]:
		source = instrument_file(argument)

		print("filename: %s" % source.get('filename'))
		print("format: %s" % source.get('format'))
		print("survey_date: %s" % source.get('capture_datetime'))
		draw_nice_line()

		# Known Stations / Coordinates
		colour.print("\nKNOWN STATIONS:\nStations Traversed/RTK'd into the system, these are known and can be referenced\n", Colour.LIGHT_MAGENTA)
		control.insert(0,['Station','Easting','Northing','Elevation'])
		colour.print(tabulate(control, headers='firstrow', floatfmt='.3f'), Colour.MAGENTA)

		# Setups
		colour.print("\nSETUPS:\nSetups are instances of putting the instrument on a station and recording detail\n", Colour.LIGHT_RED)
		setups = [['Name','Easting','Northing','Elevation','Height','Backsight','Shots']]

		for setup in source['setup']:
			setups.append([
				setup.get('station'),
				setup.get('station_easting'),
				setup.get('station_northing'),
				setup.get('station_elevation'),
				setup.get('instrument_height'),
				setup.get('backsight'),
				len(setup.get('shot'))
			])

		colour.print(tabulate(setups, headers='firstrow', floatfmt='.3f'), Colour.RED) #tablefmt="heavy_grid"

		# Shots
		colour.print("\nSHOTS (Spherical Observations):\nA sample 20 measurements taken from the first setup within this .gsi file\n", Colour.LIGHT_YELLOW)
		shots = [['Code','Number','Tgt Height','Hz Angle','Vt Angle','Sl Dist']]

		for shot in source['setup'][0]['shot'][:20]:
			shots.append([
				shot[1],
				shot[0],
				shot[5],
				shot[4],
				shot[3],
				shot[2],
			])

		colour.print(tabulate(shots, headers='firstrow', floatfmt='.3f'), Colour.YELLOW) #tablefmt="heavy_grid"

		# Calculated Coordinates
		colour.print("\nCOORDS (Derived Cartesian Coordinates):\nA sample 20 measurements with reduced coordinated x, y, and z using the project control\n", Colour.LIGHT_GREEN)
		shots = [['Code','Number','Tgt H','Azimuth','Setup Hgt','x','y','z']]

		amb1 = (control[1][1],control[1][2],control[1][3])
		amb2 = (control[2][1],control[2][2],control[2][3])

		control_phi = cartesian_to_spherical(amb1,amb2)

		for shot in source['setup'][0]['shot'][:20]:
			working_phi = (
				horizontal_to_azimuth(shot[4])
				- horizontal_to_azimuth(dms_to_decimal("4305380"))
				+ control_phi[2] ) % 360

			x,y,z = spherical_to_cartesian(shot[2],shot[3],working_phi,amb1)

			# adjust for station height and target height
			z += source['setup'][0]['instrument_height']
			z -= shot[5]


			shots.append([
				shot[1], #code
				shot[0], #num
				shot[5], #tgt_h
				working_phi, #az
				source['setup'][0]['instrument_height'], #ins_h
				x,
				y,
				z
			])

		colour.print(tabulate(shots, headers='firstrow', floatfmt='.3f'), Colour.GREEN) #tablefmt="heavy_grid"

	# End of Program Newline
	print("\nThe End\n")