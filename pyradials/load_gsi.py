'''loads and instrument .GSI file into a well-formatted dictionary'''
import logging, re
from textwrap import wrap

def load_gsi(file_name:str, bit_depth:int):
	logging.debug("loading file: " + file_name + ", with bit depth: " + str(bit_depth))

	match bit_depth:
		case 8: word_size:int = 12 # need to verify
		case 16: word_size:int = 24
		case _: None

	# open the file, and load up an array of dicts called observation
	with open(file_name, 'r') as lidf16:

		# create array of blocks for each line in the lidf16
		lidf16_block = lidf16.readlines()
		logging.debug(str(lidf16_block[0:2][0:80]) + "\n")

		# remove \n given by the readlines() function
		lidf16_block = [text.rstrip() for text in lidf16_block]
		logging.debug(str(lidf16_block[0:2][0:80]) + "\n")

		# count the number of lines/blocks
		lidf16_block_count:int = len(lidf16_block)
		logging.debug("block count: "+ str(lidf16_block_count))

		# create dictionary to store the observations
		observation_details = {
			'type': None, 'code': None, 'block': None, 'shot': None,
			'target_height': None, 'instrument_height': None,
			'backsight': None, 'hz_angle': None, 'vt_angle': None,
			'slope_dist': None, 'serial_number': None, 'date_time': None,
			'easting': None, 'northing': None, 'elevation': None,
			'is_setup_flag': False,	'raw_data': None
		}

		# create array of observation_details, 1 for each block in lidf16
		observation = [dict(observation_details) for _ in lidf16_block]

		# for each block, do:
		for i, lidf16_block in enumerate(lidf16_block, start=0):

			# chunk up the [lidf16_words]s in the [lidf16_block]s by word_size
			lidf16_word = wrap(lidf16_block,word_size) #.split() errors on spaces

			# create temp datetime varibles for string extraction
			year:str = None; month:str = None; day:str = None
			hour:str = None; min:str = None; sec:str = None; ms:str = None

			# for each lidf16_word word, do:
			for word in lidf16_word:

						# remove * prefix character for 16-bit .gsi files
				if word_size == 24 and word[0] == '*':
					word = word[1:]

				# format + copy word into the correct observation value
				match int(word[:2]):

					case 11: # point number (includes block number)
						observation[i]['block'] = re.sub(r'^0+',r'',word[2:6])
						observation[i]['shot'] = re.sub(r'^0+',r'',word[7:])
						observation[i]['type'] = 'point'

					case 12: # instrument serial number
						observation[i]['serial_number'] = re.sub(r'^0+',r'',word[7:])

					case 18: # time format 1: YYSSsss
						year = "20" + word[-8:-6]
						sec = word[-6:-4]
						ms = word[-4:-1]

					case 19: # time format 2: MMDDHHmm
						month = word[-8:-6]
						day = word[-6:-4]
						hour = word[-4:-2]
						min = word[-2:]

					case 21: # horizontal circle (Hz)
						observation[i]['hz_angle'] = int(re.sub(r'^0+',r'',word[7:]))

					case 22: # vertical angle (V)
						observation[i]['vt_angle'] = int(re.sub(r'^0+',r'',word[7:]))

					case 31: # slope distance
						observation[i]['slope_dist'] = int(re.sub(r'^0+',r'',word[7:]))

					case 41: # code number (includes block number)
						observation[i]['block'] = re.sub(r'^0+',r'',word[2:6])
						observation[i]['code'] = re.sub(r'^0+',r'',word[7:])
						observation[i]['type'] = 'code'

					case 45:
						observation[i]['shot'] = re.sub(r'^0+',r'',word[7:])

					case 79: # Attrib 8
						observation[i]['backsight'] = re.sub(r'^0+',r'',word[7:])

					case 81: # Easting (target)
						zero_safe_word = 0
						if re.sub(r'^0+',r'',word[7:]) != '':
							zero_safe_word = int(re.sub(r'^0+',r'',word[7:]))
						observation[i]['easting'] = zero_safe_word

					case 82: # Northing (target)
						zero_safe_word = 0
						if re.sub(r'^0+',r'',word[7:]) != '':
							zero_safe_word = int(re.sub(r'^0+',r'',word[7:]))
						observation[i]['northing'] = zero_safe_word

					case 83: # Elevation (target)
						zero_safe_word = 0
						if re.sub(r'^0+',r'',word[7:]) != '':
							zero_safe_word = int(re.sub(r'^0+',r'',word[7:]))
						observation[i]['elevation'] = zero_safe_word

					case 84: # Station Easting (Eo)
						observation[i]['is_setup_flag'] = True # Make this specific block a setup
						zero_safe_word = 0
						if re.sub(r'^0+',r'',word[7:]) != '':
							zero_safe_word = int(re.sub(r'^0+',r'',word[7:]))
						observation[i]['easting'] = zero_safe_word

					case 85: # Station Northing (No)
						zero_safe_word = 0
						if re.sub(r'^0+',r'',word[7:]) != '':
							zero_safe_word = int(re.sub(r'^0+',r'',word[7:]))
						observation[i]['northing'] = zero_safe_word

					case 86: # Station Elevation (Ho)
						zero_safe_word = 0
						if re.sub(r'^0+',r'',word[7:]) != '':
							zero_safe_word = int(re.sub(r'^0+',r'',word[7:]))
						observation[i]['elevation'] = zero_safe_word

					case 87: # Reflector height (above ground)
						zero_safe_word = 0
						if re.sub(r'^0+',r'',word[7:]) != '':
							zero_safe_word = int(re.sub(r'^0+',r'',word[7:]))
						observation[i]['target_height'] = zero_safe_word

					case 88: # Instrument height (above ground)
						observation[i]['instrument_height'] = int(re.sub(r'^0+',r'',word[7:]))

			# check for setup flag and set type to station
			if observation[i]['is_setup_flag']:
				observation[i]['type']='setup'

			observation[i]['date_time'] = (
				str(year) + "-" + str(month) + "-" + str(day)
				+ " " + str(hour) + ":" + str(min) + ":" + str(sec) + "." + str(ms)
			)

			# grab the entire block as a text string (for debugging)
			observation[i]['raw_data'] = lidf16_word

	for o in observation:
		logging.debug("\n" + str(o))

	# design the data structure for the instrument data/setup/code/point
	instrument_data = []
	setup = {
		'station': None, 'backsight': None,
		'instrument_height': None, 'target_height': None,
		'easting': None, 'northing': None, 'elevation': None,
		'raw_data': None, 'radials': []
	}

	# parse through observation array, creating generic instrument_data
	for parsed_block in observation:

		if parsed_block['type'] == 'setup': # is it a station setup?

			# add a new setup to the instrument_data
			instrument_data.append(dict(setup))

			# populate the data from the parsed block setup
			instrument_data[-1]['station'] = parsed_block['shot']
			instrument_data[-1]['backsight'] = parsed_block['backsight']
			instrument_data[-1]['instrument_height'] = parsed_block['instrument_height']
			instrument_data[-1]['target_height'] = parsed_block['target_height']
			instrument_data[-1]['easting'] = parsed_block['easting']
			instrument_data[-1]['northing'] = parsed_block['northing']
			instrument_data[-1]['elevation'] = parsed_block['elevation']
			instrument_data[-1]['raw_data'] = parsed_block['raw_data']

		elif parsed_block['type'] == 'code': # or is it a code?

			# store the code in memory, so we can use it afterwards in the loop
			most_recent_code = parsed_block['code']
			most_recent_sub_code = parsed_block['shot']

		else: # else it's a point/line/circle etc., copy the parsed block

			# append the measurement, grab the code from earlier loop run
			instrument_data[-1]['radials'].append(parsed_block)
			instrument_data[-1]['radials'][-1]['code'] = most_recent_code

			# some codes need custom sub-codes that allow us to label the drawing or pass params
			if most_recent_code == 'Z':
				instrument_data[-1]['radials'][-1]['code'] = (
					most_recent_code +","
					+ most_recent_sub_code
				)

	return instrument_data