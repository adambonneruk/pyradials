'''reusable mathematical calculations/functions'''

def mm_to_m(length_mm):
    '''Converts length from millimetres (mm) to decimal metres (m).'''
    if length_mm is None:
        return None
    try:
        length_mm = float(length_mm)
        length_m = length_mm / 1000
        return length_m
    except ValueError:
        print("Invalid input. Please enter a valid number representing length in millimetres.")

def dms_to_decimal(input_string):
    # Remove the last character (assuming it's a direction indicator)
    direction_indicator = input_string[-1]
    input_string = input_string[:-1]

    # Extract degrees, minutes, and seconds from the input string
    seconds = float(input_string[-2:])
    minutes = float(input_string[-4:-2]) if len(input_string) > 2 else 0
    degrees = float(input_string[:-4]) if len(input_string) > 4 else 0

    # Calculate decimal degrees
    decimal_degrees = degrees + minutes / 60 + seconds / 3600

    # Adjust the decimal degrees based on the direction indicator
    if direction_indicator in ['S', 'W']:
        decimal_degrees *= -1

    return round(decimal_degrees, 6)