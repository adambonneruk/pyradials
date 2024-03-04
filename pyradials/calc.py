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

def spherical_to_cartesian(radius, inclination, azimuth, origin = (0,0,0)):
    # Convert degrees to radians
    inclination_rad = math.radians(inclination)
    azimuth_rad = math.radians(azimuth)

    # Calculate Cartesian coordinates
    x = origin[0] + radius * math.sin(inclination_rad) * math.cos(azimuth_rad)
    y = origin[1] + radius * math.sin(inclination_rad) * math.sin(azimuth_rad)
    z = origin[2] + radius * math.cos(inclination_rad)

    return x, y, z

def cartesian_to_spherical(coord1, coord2):
    x1, y1, z1 = coord1
    x2, y2, z2 = coord2

    # Calculate differences in coordinates
    dx = x2 - x1
    dy = y2 - y1
    dz = z2 - z1

    # Calculate radius
    radius = math.sqrt(dx**2 + dy**2 + dz**2)

    # Calculate inclination (theta)
    if dx == 0 and dy == 0:
        if dz > 0:
            inclination = 90.0
        elif dz < 0:
            inclination = -90.0
        else:
            inclination = 0.0
    else:
        inclination = math.degrees(math.atan2(math.sqrt(dx**2 + dy**2), dz))

    # Calculate azimuth (phi)
    if dx == 0:
        if dy > 0:
            azimuth = 90.0
        elif dy < 0:
            azimuth = -90.0
        else:
            azimuth = 0.0
    else:
        azimuth = math.degrees(math.atan2(dy, dx))
        if azimuth < 0:
            azimuth += 360.0

    return radius, inclination, azimuth

def horizontal_to_azimuth(horizontal_angle):
    # Ensure the angle is within 0 to 360 degrees range
    horizontal_angle %= 360

    # Azimuth is 90 degrees minus horizontal angle
    azimuth = (90 - horizontal_angle) % 360

    return azimuth


