import os
from tabulate import tabulate
from colour import Colour; colour = Colour()
from calc import spherical_to_cartesian, dms_to_decimal, cartesian_to_spherical, horizontal_to_azimuth


def banner(version:str = '0.0.0'):
	os.system("cls")
	print('\n  ____        ____           _ _       _        ')
	print(' |  _ \ _   _|  _ \ __ _  __| (_) __ _| |___    ')
	print(' | |_) | | | | |_) / _` |/ _` | |/ _` | / __|   ')
	print(' |  __/| |_| |  _ < (_| | (_| | | (_| | \__ \  v%s' % version)
	print(' |_|    \__, |_| \_\__,_|\__,_|_|\__,_|_|___/  by Adam Bonner')
	print('        |___/                                  MIT Licence, 2024\n')

def draw_nice_line():
	terminal_width = os.get_terminal_size().columns
	print("─" * terminal_width)

def print_gps(source):
	colour.print("\n== GPS STATIONS ==\nStations observed with RTK/GNSS\n", Colour.LIGHT_BLUE)
	view_stations = [['Name','Easting','Northing','Elev']]

	for station in source['data']:
		view_stations.append(station)

	colour.print(tabulate(view_stations, headers='firstrow', floatfmt='.3f'), Colour.BLUE)
	print('')

def print_coordinates(source):
	colour.print("== COORDINATES ==",Colour.LIGHT_GREEN)

	for setup in source['data']:
		colour.print("-- " + str(setup['station']) + " --",Colour.LIGHT_GREEN)

		coords = []
		coords.append(['Code','Easting','Northing','Elev','Attribs'])
		for radial in setup['coded_measurements']:
			coords.append([radial.code,radial.ea,radial.no,radial.el,radial.attrib])

		colour.print(tabulate(coords, headers='firstrow', floatfmt='.3f'), Colour.GREEN)
		print('')

def print_stations(source):
	colour.print("== STATIONS ==",Colour.LIGHT_MAGENTA)

	stations = []
	stations.append(['Station','Easting','Northing','Elev'])

	for setup in source['data']:
		stations.append([setup['station'],setup['easting'],setup['northing'],setup['elevation']])

	colour.print(tabulate(stations, headers='firstrow', floatfmt='.3f'), Colour.MAGENTA)
	print('')

def print_control(control):
	colour.print("== CONTROL ==",Colour.LIGHT_RED)

	stations = []
	stations.append(['Station','Easting','Northing','Elev'])

	stations = stations + [[key, *value] for key, value in control.items()]

	colour.print(tabulate(stations, headers='firstrow', floatfmt='.3f'), Colour.RED)
	print('')

def increment_string(s):
	# Convert the string to a list to make it mutable
	s = list(s)

	# Start from the end of the string
	i = len(s) - 1
	carry = 1  # Initialize carry to 1 to increment the last character

	# Iterate through the string characters from the end to the beginning
	while i >= 0 and carry:
		if s[i].isdigit():  # If the character is a digit
			# Increment the digit and check for carry-over
			carry, digit = divmod(int(s[i]) + carry, 10)
			s[i] = str(digit)
		else:
			# If the character is not a digit, break the loop
			break
		i -= 1

	# If carry is still remaining, prepend '1'
	if carry:
		s.insert(0, '1')
	return ''.join(s)

def print_radials(source,control) -> list:
	colour.print("== RADIALS ==",Colour.LIGHT_YELLOW)
	drawing = []

	for setup in source['data']:
		radials = []
		radials.append(['Point ID','Code','Sd','Vt','Hz','Easting','Northing','Elev','Attrib'])
		colour.print("-- " + str(setup['station']) + ", instrument height: " + str(setup['height']) + "m --",Colour.LIGHT_YELLOW)

		station = setup['station']
		backsight = setup['backsight']

		# if it's the first setup, we won't have a backsight, so let's go find it (typically STN2)
		if backsight == None:
			backsight = increment_string(station)

		stn_xyz = control[station]
		try:
			bs_xyz = control[backsight]
		except:
			raise ValueError("cant find backsight in control" + str(setup))
		ro_radius, ro_inclination, ro_azimuth = cartesian_to_spherical(stn_xyz,bs_xyz)

		for shot in setup['coded_measurements']:

			# fix for a RO done backwards
			if setup['coded_measurements'][0].vt > 180:
				shot_angle = shot.hz + 180 % 360
			else:
				shot_angle = shot.hz

			# subtract the instruments angle (j) to get a 0, then add the real RO angle (k) and the shot angle (i)
			i = horizontal_to_azimuth(shot_angle) # angle of shot from 0
			j = horizontal_to_azimuth(setup['coded_measurements'][0].hz) # angle of ro from 0
			k = ro_azimuth # angle of ro from actual 0

			shot_azimuth = i-j+k
			x,y,z = spherical_to_cartesian(shot.sd,shot.vt,shot_azimuth,stn_xyz)

			# adjust height based on instrument and target offsets
			z += setup['height']
			z -= shot.th

			radials.append([
				shot.point_id,
				shot.code,
				shot.sd,
				shot.vt,
				shot.hz,
				x,
				y,
				z,
				shot.attrib
			])

			if shot.code != 'RO':
				sx,sy,sz = stn_xyz
				drawing.append([
					shot.point_id,
					shot.code,
					x, y, z,
					shot.attrib,
					sx,sy,sz,
					setup['height']
				])

		colour.print(tabulate(radials, headers='firstrow', floatfmt='.3f'), Colour.YELLOW)
		print('')

	return drawing