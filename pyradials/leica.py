import logging, json
from collections import namedtuple
from textwrap import wrap
from calc import mm_to_m, dms_to_decimal

'''
General
	11	Point number (includes block number)
	12	Instrument serial number
	13	Instrument type
	18	Time format 1:
	19	Time format 2:

Angles
	21	Horizontal circle (Hz)
	22	Vertical angle (V)
	25	Horizontal circle difference(Hz0-Hz)

Distances
	31	Slope distance
	32	Horizontal distance
	33	Height difference

Codeblock.
	41	Code number (includes block number)
	42+	Information 1-8

Distance (additional information)
	51	Constants (ppm,mm)
	52	Number of measurements
	53	Standard Deviation
	58	Signal strength
	59	Reflector constant (1/10 mm) ppm

Point coding
	71	Point code
	72+	Attrib. 1-8

Coordinates
	81	Easting (target)
	82	Northing (target)
	83	Elevation (target)
	84	Station easting (Eo)
	85	Station northing (No)
	86	Station elevation (Ho)
	87	Reflector height (above ground)
	88	Instrument height (above ground)
'''

def strip_leading_zeros(input_str:str, field_type='int'):
	if input_str == '0' * len(input_str):
		return 0

	# Strip leading zeros
	stripped_str = input_str.lstrip('0')

	# Try converting to integer
	try:
		result = int(stripped_str)
	except ValueError:
		# If conversion fails, return as string
		result = stripped_str

	return result if field_type == 'int' else str(result)

def derive_date_time(w18:str, w19:str) -> str:
	if w18 is not None and w19 is not None:
		w18 = "0" + str(w18)
		w19 = "0" + str(w19)

		year:str = "20" + w18[-8:-6]
		month:str = w19[-8:-6]
		day:str = w19[-6:-4]
		hour:str = w19[-4:-2]
		min:str = w19[-2:]
		sec:str = w18[-6:-4]

		return (str(year) + "-" + str(month) + "-" + str(day) + " " + str(hour) + ":" + str(min) + ":" + str(sec))

def gsi_to_blocks_list(fn:str, bit_depth:int = 16, debug_json_output = False) -> list:
	'''takes a gsi filename and returns a list of tuples with the setups, codes, and measurements'''
	# Set word_size based on bit_depth
	match bit_depth:
		case 8:
			word_size:int = 12
			trim_16bit_prefix = False
			logging.debug('word size:%d, trim * prefix: %r' % (word_size, trim_16bit_prefix))

		case 16:
			word_size:int = 24
			trim_16bit_prefix = True
			logging.debug('word size:%d, trim * prefix: %r' % (word_size, trim_16bit_prefix))

		case _:
			raise Exception('Unknown File Type: Leica .GSI Incorrect Bit-depth')

	# Open and read the file
	with open(fn, 'r') as gsi_file:
		gsi_file_reader = [text.rstrip() for text in gsi_file.readlines()]

	list_of_blocks = []
	# Named Tuples
	Setup = namedtuple("Setup","type station w84 w85 w86 w88 w79 raw")
	Code = namedtuple("Code","type code w42 w43 w44 w45 w46 w47 w48 w49 raw")
	Measurement = namedtuple("Measurement","type point_id w21 w22 w31 w87 w81 w82 w83 date_time raw")

	for row in gsi_file_reader:
		words = wrap(row, word_size)

		if trim_16bit_prefix:
			words[0] = words[0][1:]

		intermediate_dict = {}

		for word in words:
			intermediate_dict[word[:2]] = strip_leading_zeros(word[7:])

		if intermediate_dict.get('84') is not None:
			logging.debug("this block is a setup")
			setup = Setup("setup",
				intermediate_dict.get('11'),
				intermediate_dict.get('84'),
				intermediate_dict.get('85'),
				intermediate_dict.get('86'),
				intermediate_dict.get('88'),
				intermediate_dict.get('79'),
				words,
			)
			list_of_blocks.append(setup)

		elif intermediate_dict.get('41') is not None:
			logging.debug("this block is a code")
			code = Code("code",
				intermediate_dict.get('41'),
				intermediate_dict.get('42'),
				intermediate_dict.get('43'),
				intermediate_dict.get('44'),
				intermediate_dict.get('45'),
				intermediate_dict.get('46'),
				intermediate_dict.get('47'),
				intermediate_dict.get('48'),
				intermediate_dict.get('49'),
				words,
			)
			list_of_blocks.append(code)

		else:
			logging.debug("this block is a measurement")
			measurement = Measurement("measurement",
				intermediate_dict.get('11'),
				intermediate_dict.get('21'),
				intermediate_dict.get('22'),
				intermediate_dict.get('31'),
				intermediate_dict.get('87'),
				intermediate_dict.get('81'),
				intermediate_dict.get('82'),
				intermediate_dict.get('83'),
				derive_date_time(intermediate_dict.get('18'),intermediate_dict.get('19')),
				words,
			)
			list_of_blocks.append(measurement)

	if debug_json_output:
		with open('debug/processed_gsi.json', "w") as write_file:
			write_file.write(json.dumps(list_of_blocks) + "\n")

	return list_of_blocks

def check_integrity_of_setup(setup_block,ro_code_block,ro_measurement) -> None:

	logging.debug(setup_block)

	if setup_block.type != "setup":
		raise Exception('gsi does not start with a setup' + str(setup_block))
	if ro_code_block.type != "code":
		raise Exception('gsi does not follow setup with a RO' + str(setup_block))
	if ro_code_block.code != "RO":
		raise Exception('code is not RO following setup' + str(setup_block))
	if ro_measurement.type != "measurement":
		raise Exception('ro is missing the measurement' + str(setup_block))

def combine_strings(*args):
	filtered_args = [str(arg) for arg in args if arg not in (None, '', '0', 0, '.', '>')]
	return ', '.join(filtered_args)

def reduce_and_code_measurements(gsi_blocks:list , debug_json_output:bool = False) -> dict:

	check_integrity_of_setup(gsi_blocks[0],gsi_blocks[1],gsi_blocks[2])
	setups_with_coded_measurements = []
	Coded_Measurement = namedtuple("Coded_Measurement", "point_id code attrib hz vt sd ea no el th")

	recent_code:str = None
	recent_attrib:str = None

	for i, block in enumerate(gsi_blocks, start=0):
		match block.type:
			case "setup":
				check_integrity_of_setup(gsi_blocks[i],gsi_blocks[i+1],gsi_blocks[i+2])
				setups_with_coded_measurements.append(dict())
				setups_with_coded_measurements[-1]['station'] = block.station
				setups_with_coded_measurements[-1]['easting'] = mm_to_m(block.w84)
				setups_with_coded_measurements[-1]['northing'] = mm_to_m(block.w85)
				setups_with_coded_measurements[-1]['elevation'] = mm_to_m(block.w86)
				setups_with_coded_measurements[-1]['height'] = mm_to_m(block.w88)
				setups_with_coded_measurements[-1]['backsight'] = block.w79
				setups_with_coded_measurements[-1]['date_time'] = None
				setups_with_coded_measurements[-1]['coded_measurements'] = []

			case "code":
				recent_code = block.code
				recent_attrib = combine_strings(block.w42,block.w43,block.w44,block.w45,block.w46,block.w47,block.w48,block.w49)

			case "measurement":
				coded_measurement = Coded_Measurement(
					block.point_id,
					recent_code,
					recent_attrib,
					dms_to_decimal(str(block.w21)),
					dms_to_decimal(str(block.w22)),
					mm_to_m(block.w31),
					mm_to_m(block.w81),
					mm_to_m(block.w82),
					mm_to_m(block.w83),
					mm_to_m(block.w87)
				)

				if block.date_time is not None:
					setups_with_coded_measurements[-1]['date_time'] = block.date_time

				setups_with_coded_measurements[-1]['coded_measurements'].append(coded_measurement)

			case _: raise Exception('block isn\'t a code, measurement or setup')

	if debug_json_output:
		with open('debug/reduce_measurements.json', "w") as write_file:
			write_file.write(json.dumps(setups_with_coded_measurements) + "\n")

	return setups_with_coded_measurements

def gsi(fn:str, bit_depth:int, debug_json_output:bool = False) -> list:
	gsi_blocks = gsi_to_blocks_list(fn,bit_depth,debug_json_output)
	data = reduce_and_code_measurements(gsi_blocks,True)

	return data

if __name__ == "__main__":
	#data = main('data/OFFICE.GSI',16,True)
	data = gsi('data/SOUTHPOR.GSI',16,True)
	#print(data)

