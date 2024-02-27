import sys, logging, json
from load_gsi import load_gsi

if __name__ == '__main__':

	DEBUG_MODE = True
	if DEBUG_MODE:
		logging.basicConfig(format='%(message)s', level=logging.INFO)

	# Load in the passed argument as instrument data
	fn = sys.argv[1]
	instrument_data = load_gsi(fn, 16)

	#convert to json
	json_string = json.dumps(instrument_data, indent=4)

	with open("data_file.json", "w") as write_file:
		json.dump(instrument_data, write_file, indent=4)





'''#####################################################################################################'''
'''#####################################################################################################'''
'''#####################################################################################################'''

'''instrument_file = {
		'filename': None,
		'data': dict(instrument_data)
	}

	survey = {
		'control': None,
		'traverse': None,
		'measurement': [],
		'model': None,
	}'''

''' Project Data Structure:

"Survey Project".json
- Control
	- Station
		- Fixed Coordinates
		- Other Coordinates
- Traverse
- Measure
	- Instrument File
- Model
	- Topographical
	- Elevation

	- Leica Instrument Data File 8-Bit (.GSI)
	- [lidf16] Leica Instrument Data File 16-Bit (.GSI)
		- Filename
		- Setup
			- Stn, IH, BS, FS[], TH, E, N, H
			- Observation (e.g. Points, Lines, Circles etc.)
				- [block] Block
					- [word] Word

	'''