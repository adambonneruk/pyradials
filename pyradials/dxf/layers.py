'''layers.py used to store instrument code and layer info'''

# Static Colour Definitions
WHITE:int = 0
RED:int = 1
YELLOW:int = 2
GREEN:int = 3
CYAN:int = 4
BLUE:int = 5
MAGENTA:int = 6
DARK_GREY:int = 7
GREY:int = 8
LIGHT_GREY:int = 9
SALMON:int = 11
BRICK:int = 12
BROWN:int = 26
ORANGE:int = 30
PINK:int = 31
WOOD:int = 41
SUNSHINE:int = 51
SPARK:int = 52
TECH:int = 115
TURQUOISE:int = 122
NATURE:int = 124
SKY_BLUE:int = 161
IMPORTANT:int = 240
LASER:int = 247
DULL:int = 252

# Code Table, format is {'code':['desc', 'layer','type','height-code']}
code_table = {
    # control, meta, and important
    'RO':['Reference Object','control','block',None],
    'Z':['Reference Object','control','block',None],

    # internal and external
    'FE':['Fence','fences_gates','line','FE'],
    'SL':['Spot Level','surface_change','point',''],
    'CS':['Surface Change','surface_change','line',''],
    'ST':['Step','steps_stairs','line',''],
    'STEP':['Step','steps_stairs','line',''],

    # internal
    'DC':['Drop Ceiling','oh_beams','line',None],
    'PW':['Party Wall','bg_walls','line',None],
    'SW':['Solid Wall','bg_walls','line',None],
    'CC':['Ceiling Change','oh_beams','line',None],
    'FCL':['Ceiling Level','text','point','CL'],
    'FFL':['Floor Level','text','point','FL'],
    'LINT':['Lintel Height','text','point','L'],
    'SILL':['Sill Height','text','point','S'],
    'WIN':['Window','windows','line',None],
    'DH':['Door Height','text','point','DH'],
    'DW':['Door (Width)','text','line',None],
    'LIG':['Light (Round)','lighting','point','LIGHT'],
    'RAD':['Radiator (2 Point)','radiators','line',None],
    'BE':['Overhead Beam','oh_beams','line',None],
    'USB':['Underside of Beam','oh_beams','point','USB'],
    'US':['Unknown String','text','line',None],
    'SK':['Kitchen Sink','kitchen_furniture','line',None],
    'URI':['Urinal','sanitary','line',None],
    'SINK':['Sink','sanitary','line',None],
    'HATCH':['Hatch','internal_furniture','line',''],

    # external
    'BB':['Bottom of Bank','bank_bottom','line',''],
    'DP':['Drain Pipe','utilities','circle',''],
    'TB':['Top of Bank','bank_top','line',''],
    'BG':['Building','buildings','line',''],
    'BC':['Building Canopy','building_canopy','line',None],
    'GE':['Gate','fences_gates','line',''],
    'LS':['Level String','levels','line',''],
    'WL':['Wall','walls','line',''],
    'TE':['Tree','vegetation','block',None],
    'TEMG':['Multi-Girth Tree','vegetation','block',None],
    'STUMP':['Tree Stump','vegetation','block',None],
    'WAT':['Water Level','water_courses','point','WL'],
    'HE':['Hedge (Center)','vegetation','line',''],
    'HEF':['Hedge (Face)','vegetation','line',''],
    'SAP':['Sapling','vegetation','block',None],
    'K':['Kerb','kerb','line',''],
    'KT':['Kerb Top','kerb_top','point',''],
    'RCL':['Road Center Line','road_marking','line',''],
    'GY3P':['Gully (3 Point)','gully','line',''],
    'GY':['Gully','gully','line',''],
    'GH':['Green House','green_house','line',''],
    'RL':['Ridge Level','level','point','RL'],
    'LP':['Lamp Post','street_furniture','block','LP'],
    'MH':['Manhole (3-Point)','utilities','block','MH'],
}

# Layer Table, format is {'layer':[colour-code,'line-type']}
layer_table = {
    # control, meta, and important
    'control':[IMPORTANT,'Continuous'],
    'grid':[WOOD,'Continuous'],
    'os_grid':[DULL,'Continuous'],
    'points':[TECH,'Continuous'],
    'radials':[LASER,'Continuous'],
    'text':[MAGENTA,'Continuous'],
    'text_surface':[ORANGE,'Continuous'],
    'titleblock':[WHITE,'Continuous'],
    'viewports':[WHITE,'Continuous'],

    # internal and external
    'fences_gates':[RED,'DASHDOT'],
    'steps_stairs':[NATURE,'Continuous'],
    'surface_change':[WHITE,'DASHED'],
    'no_access':[DULL,'Continuous'],

    # internal
    'bg_walls':[CYAN,'Continuous'],
    'bg_walls_partition':[GREEN,'Continuous'],
    'doors':[DULL,'Continuous'],
    'internal_furniture':[TURQUOISE,'Continuous'],
    'kitchen_furniture':[TURQUOISE,'Continuous'],
    'lighting':[YELLOW,'Continuous'],
    'oh_beams':[WOOD,'DASHED'],
    'radiators':[GREEN,'Continuous'],
    'sanitary':[SALMON,'Continuous'],
    'services':[CYAN,'Continuous'],
    'skylights':[SKY_BLUE,'DASHED'],
    'tanks':[SUNSHINE,'Continuous'],
    'windows':[WHITE,'Continuous'],

    # external
    'bank_bottom':[ORANGE,'Continuous'],
    'bank_top':[ORANGE,'Continuous'],
    'boundary':[BROWN,'Continuous'],
    'buildings':[BLUE,'Continuous'],
    'building_canopy':[BLUE,'DASHED'],
    'gully':[WHITE,'Continuous'],
    'green_house':[TECH,'Continuous'],
    'kerb':[WHITE,'Continuous'],
    'kerb_top':[GREY,'Continuous'],
    'level':[BRICK,'Continuous'],
    'road_marking':[GREY,'Continuous'],
    'street_furniture':[GREY,'Continuous'],
    'tadpoles':[PINK,'Continuous'],
    'utilities':[RED,'Continuous'],
    'vegetation':[GREEN,'Continuous'],
    'walls':[RED,'Continuous'],
    'water_courses':[CYAN,'Continuous'],

    # services
    'service_bt':[BLUE,'Dot'],
    'service_electricity':[SPARK,'Dot'],
    'service_gas':[GREY,'Dot'],
    'service_virgin':[RED,'Dot'],
    'service_water':[CYAN,'Dot'],
}

def get_code_info(code):
    code_info = code_table.get(code)
    if code_info:
        desc, layer, type_, height_code = code_info
        layer_info = layer_table.get(layer)
        if layer_info:
            color_code, linetype = layer_info
            return {
                'layer_name': layer,
                'layer_color': color_code,
                'layer_linetype': linetype,
                'description': desc,
                'type': type_,
                'height_code': height_code
            }
        else:
            return {
                'layer_name': layer,
                'description': desc,
                'type': type_,
                'height_code': height_code
            }
    else:
        return None

# Main block to execute if the script is run directly
if __name__ == "__main__":
    code = 'BE'
    code_info = get_code_info(code)
    if code_info:
        print("Code Information:")
        for key, value in code_info.items():
            print(f"{key}: {value}")
    else:
        print("Code not found in the code table.")
