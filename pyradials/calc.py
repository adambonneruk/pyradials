'''reusable mathematical calculations/functions'''
import math

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

def pad_decimal(decimal):
    # Convert the decimal to a string with 3 decimal places
    padded_decimal = format(decimal, '08.3f')
    return padded_decimal

def spherical_to_cartesian(radius, inclination, azimuth, observer_x=0, observer_y=0, observer_z=0, instrument_height=0, target_height=0):
    # Convert degrees to radians
    inclination = math.radians(inclination)
    azimuth = math.radians(azimuth)

    # Calculate Cartesian coordinates
    y = observer_y + (radius * math.sin(inclination) * math.cos(azimuth))
    x = observer_x + (radius * math.sin(inclination) * math.sin(azimuth))
    z = observer_z + (radius * math.cos(inclination))

    # Adjust for instrument height and target height
    z += instrument_height
    z -= target_height

    # Round off each coordinate result to 3 decimal places
    x = round(x, 3)
    y = round(y, 3)
    z = round(z, 3)

    return x, y, z