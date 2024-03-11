'''opens instrument file and parses them into a tidy list of setups and measurements'''
import pathlib
from leica import gsi
from gps import load_and_average_gps_csv_file

def filename_details(fn: str):
	''' returns stem and ext for a given filepath '''
	stem: str = str(pathlib.Path(fn).stem)
	suffix: str = str(pathlib.Path(fn).suffix)

	return stem, suffix

def instrument_file_as_source(full_fn:str, debug_json_output:bool = False):
	'''with a given fn, check compatibility/support and load the file into memory'''

	stem, suffix = filename_details(full_fn)

	match suffix.lower():
		case ".gsi":  # Leica TPS 1100/1200 Series 8/16-bit Data
			# open file, read first line to determine bit-depth
			with open(full_fn, 'r') as leica_gsi:
				first_line = leica_gsi.readline().strip('\n')

			# * in first position equals 16-bit
			if first_line[0] == '*':
				gsi_bit_depth = 16
				data = gsi(full_fn, gsi_bit_depth, debug_json_output)
				source = {
					'file_name': stem + suffix,
					'format': 'Leica Geosystems 16-bit GSI (Geo Serial Interface)',
					'capture_date_time': data[0]['date_time'],
					'type': 'radials',
					'data': data,
				}

			else:
				gsi_bit_depth = 8
				raise Exception('8-bit Leica .GSI Not Supported')

		case ".r25":  # Carlson RW5
			raise Exception('Carlson RW5 Not Supported')

		case ".raw":  # Trimble 1
			raise Exception('Trimble RAW Not Supported')

		case ".are":  # Trimble 1
			raise Exception('Trimble ARE Not Supported')

		case ".csv": # GPS Survey Data
			data = load_and_average_gps_csv_file(full_fn)
			source = {
				'file_name': stem + suffix,
				'format': 'RTK/GNSS Position Data: CSV Format',
				'capture_date_time': None,
				'type': 'gps',
				'data': data
			}

		case _:
			raise Exception('Unknown File Type')

	# output the opened parsed instrument file
	return source

if __name__ == "__main__":
	source = instrument_file_as_source('data/SPORTRD1.GSI')
	print(source)
