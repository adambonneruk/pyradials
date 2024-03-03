import logging, sys, pathlib, re, json
from textwrap import wrap
from datetime import datetime
from calc import mm_to_m, dms_to_decimal

DEBUG_MODE = True
if DEBUG_MODE:
	logging.basicConfig(format='%(message)s', level=logging.INFO)

def filename_details(fn: str):
	''' returns lowercase stem and ext for a given filepath '''
	stem: str = str(pathlib.Path(fn).stem)
	suffix: str = str(pathlib.Path(fn).suffix)

	return stem.lower(), suffix.lower()

def import_leica_gsi_file(full_fn: str, export_json: bool = False, gsi_bit_depth: int = 16):
	'''open a .gsi file and load into dictionary, optionally dump json of raw data'''
	source = {}  # Create Dictionary for this .GSI Source
	source['filename'] = '%s%s' % (filename_details(full_fn))
	source['process_datetime'] = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
	source['format'] = 'Leica Geosystems %d-bit GSI (Geo Serial Interface)' % gsi_bit_depth

	with open(full_fn, 'r') as leica_gsi:
		leica_gsi_block = [text.rstrip() for text in leica_gsi.readlines()]

	logging.debug(str(leica_gsi_block[0:2][0:80]) + "\n") # 80 chars of top 2 lines
	parsed_leica_gsi_block = [dict() for _ in leica_gsi_block]

	word_size: int = 0
	trim_16bit_prefix: bool = False

	match gsi_bit_depth:
		case 8:
			word_size: int = 12
		case 16:
			word_size: int = 24
			trim_16bit_prefix = True
			logging.debug('word size:%d, trim * prefix: %r' % (word_size, trim_16bit_prefix))
		case _:
			raise Exception('Unknown File Type: Leica .GSI Incorrect Bit-depth')

	for i, leica_gsi_block in enumerate(leica_gsi_block, start=0):
		leica_gsi_word = wrap(leica_gsi_block, word_size)

		# trim the '*' from first word
		leica_gsi_word[0] = leica_gsi_word[0][1:]

		for word in leica_gsi_word:
			match int(word[:2]):
				case 11: # point number (includes block number)
					parsed_leica_gsi_block[i]['block'] = re.sub(
						r'^0+', r'', word[2:6])
					parsed_leica_gsi_block[i]['shot'] = re.sub(
						r'^0+', r'', word[7:])
					parsed_leica_gsi_block[i]['type'] = 'point'
				case 12: # instrument serial number
					parsed_leica_gsi_block[i]['serial_number'] = re.sub(
						r'^0+', r'', word[7:])
					source['instrument_serial_number'] = parsed_leica_gsi_block[i]['serial_number']
				case 18: # time format 1: YYSSsss
					year = "20" + word[-8:-6]
					sec = word[-6:-4]
					# ms = word[-4:-1] # ms seems to always be .000
				case 19: # time format 2: MMDDHHmm
					month = word[-8:-6]
					day = word[-6:-4]
					hour = word[-4:-2]
					min = word[-2:]
				case 21: # horizontal circle (Hz)
					parsed_leica_gsi_block[i]['Hz'] = int(
						re.sub(r'^0+', r'', word[7:]))
				case 22: # vertical angle (V)
					parsed_leica_gsi_block[i]['V'] = int(
						re.sub(r'^0+', r'', word[7:]))
				case 31: # slope distance (SD)
					parsed_leica_gsi_block[i]['Sd'] = int(
						re.sub(r'^0+', r'', word[7:]))
				case 41: # code number (includes block number)
					parsed_leica_gsi_block[i]['block'] = re.sub(
						r'^0+', r'', word[2:6])
					parsed_leica_gsi_block[i]['code'] = re.sub(
						r'^0+', r'', word[7:])
					parsed_leica_gsi_block[i]['type'] = 'code'
				case 43:
					parsed_leica_gsi_block[i]['shot'] = re.sub(
						r'^0+', r'', word[7:])
				case 45:
					parsed_leica_gsi_block[i]['shot'] = re.sub(
						r'^0+', r'', word[7:])
				case 79: # Attrib 8
					parsed_leica_gsi_block[i]['backsight'] = re.sub(
						r'^0+', r'', word[7:])
				case 81: # Easting (target)
					zero_safe_word = 0
					if re.sub(r'^0+', r'', word[7:]) != '':
						zero_safe_word = int(re.sub(r'^0+', r'', word[7:]))
					parsed_leica_gsi_block[i]['Et'] = zero_safe_word
				case 82: # Northing (target)
					zero_safe_word = 0
					if re.sub(r'^0+', r'', word[7:]) != '':
						zero_safe_word = int(re.sub(r'^0+', r'', word[7:]))
					parsed_leica_gsi_block[i]['Nt'] = zero_safe_word
				case 83: # Elevation (target)
					zero_safe_word = 0
					if re.sub(r'^0+', r'', word[7:]) != '':
						zero_safe_word = int(re.sub(r'^0+', r'', word[7:]))
					parsed_leica_gsi_block[i]['Et'] = zero_safe_word
				case 84: # Station Easting (Eo)
					parsed_leica_gsi_block[i]['type'] = 'setup' # Make this specific block a setup
					zero_safe_word = 0
					if re.sub(r'^0+', r'', word[7:]) != '':
						zero_safe_word = int(re.sub(r'^0+', r'', word[7:]))
					parsed_leica_gsi_block[i]['Eo'] = zero_safe_word
				case 85: # Station Northing (No)
					zero_safe_word = 0
					if re.sub(r'^0+', r'', word[7:]) != '':
						zero_safe_word = int(re.sub(r'^0+', r'', word[7:]))
					parsed_leica_gsi_block[i]['No'] = zero_safe_word
				case 86: # Station Elevation (Ho)
					zero_safe_word = 0
					if re.sub(r'^0+', r'', word[7:]) != '':
						zero_safe_word = int(re.sub(r'^0+', r'', word[7:]))
					parsed_leica_gsi_block[i]['Ho'] = zero_safe_word
				case 87: # Reflector height (above ground)
					zero_safe_word = 0
					if re.sub(r'^0+', r'', word[7:]) != '':
						zero_safe_word = int(re.sub(r'^0+', r'', word[7:]))
					parsed_leica_gsi_block[i]['Rh'] = zero_safe_word
				case 88: # Instrument height (above ground)
					parsed_leica_gsi_block[i]['Ih'] = int(
						re.sub(r'^0+', r'', word[7:]))
		try:
			parsed_leica_gsi_block[i]['date_time'] = (
				str(year) + "-" + str(month) + "-" + str(day)
				+ " " + str(hour) + ":" + str(min) + ":" + str(sec)
			)
			source['capture_datetime'] = parsed_leica_gsi_block[i]['date_time']
		except:
			logging.debug("this particular block doesn't have datetime info")

		# store the block-word array as raw
		parsed_leica_gsi_block[i]['raw'] = leica_gsi_word

		# json export
		if export_json:
			with open(pathlib.Path(full_fn).with_suffix('.json'), "w") as write_file:
				write_file.write(json.dumps(parsed_leica_gsi_block) + "\n")

	# the leica_gsi is now parsed_leica_gsi, lets grab the relevant data for source{}
	source['setup'] = []
	for parsed_block_value in parsed_leica_gsi_block:
		match parsed_block_value['type']:
			case 'setup':
				# put a dictionary in the observation array for a setup, then populate with setup details
				source['setup'].append(dict())
				source['setup'][-1]['station'] = parsed_block_value.get('shot')
				source['setup'][-1]['backsight'] = parsed_block_value.get('backsight')
				source['setup'][-1]['instrument_height'] = mm_to_m(parsed_block_value.get('Ih'))
				source['setup'][-1]['target_height'] = mm_to_m(parsed_block_value.get('Rh'))
				source['setup'][-1]['station_easting'] = mm_to_m(parsed_block_value.get('Eo'))
				source['setup'][-1]['station_northing'] = mm_to_m(parsed_block_value.get('No'))
				source['setup'][-1]['station_elevation'] = mm_to_m(parsed_block_value.get('Ho'))
				source['setup'][-1]['shot'] = []

			case 'code':
				most_recent_code: str = parsed_block_value.get('code')
				if parsed_block_value.get('shot') != '':
					most_recent_comma_code: str = parsed_block_value.get(
						'shot')
				else:
					most_recent_comma_code = None

			case 'point':
				# derive the full comma-code
				if most_recent_comma_code:
					current_code = str(most_recent_code + "," + most_recent_comma_code)
				else:
					current_code = most_recent_code

				# built the tuple
				source['setup'][-1]['shot'].append(tuple((
					parsed_block_value.get('shot'),						# Shot = Point Number
					current_code,										# Code = Codelist Code, Comma Code
					mm_to_m(parsed_block_value.get('Sd')),				# Radius = Slope Distance
					dms_to_decimal(str(parsed_block_value.get('V'))),	# Inclination = Vertical Angle
					dms_to_decimal(str(parsed_block_value.get('Hz'))),	# Azimuth = Horizontal Angle
					mm_to_m(parsed_block_value.get('Rh'))				# Target Height = Reflector Height
				)))

			case _:
				raise Exception('Not a Setup, Code or Point')

	return source

def import_instrument_file(full_fn: str, export_json: bool = False):
	'''with a given fn, check compatibility/support and load the file into memory'''

	stem, suffix = filename_details(full_fn)

	match suffix:
		case ".gsi":  # Leica TPS 1100/1200 Series 8/16-bit Data
			# open file, read first line to determine bit-depth
			with open(full_fn, 'r') as leica_gsi_file:
				first_line = leica_gsi_file.readline().strip('\n')

			# * in first position equals 16-bit
			if first_line[0] == '*':
				gsi_bit_depth = 16
				something = import_leica_gsi_file(
					full_fn, export_json, gsi_bit_depth)
			else:
				gsi_bit_depth = 8
				raise Exception('8-bit Leica .GSI Not Supported')

		case "r25":  # Carlson RW5
			raise Exception('Carlson RW5 Not Supported')

		case "raw":  # Trimble 1
			raise Exception('Trimble RAW Not Supported')

		case "are":  # Trimble 1
			raise Exception('Trimble ARE Not Supported')

		case _:
			raise Exception('Unknown File Type')

	# output the opened parsed instrument file
	return something

full_fn = sys.argv[1]
source = import_instrument_file(full_fn)
