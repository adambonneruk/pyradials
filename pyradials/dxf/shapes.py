import ezdxf, math

def flag(doc):
    flag_block = doc.blocks.new(name='FLAG')

    # Add DXF entities to the block 'FLAG'.
    # The default base point (= insertion point) of the block is (0, 0).
    flag_block.add_lwpolyline([(0, 0), (0, 5), (5, 3), (0, 3)])  # the flag symbol as 2D polyline
    flag_block.add_circle((0, 0), .04)  # mark the base point with a circle

    return flag_block

def tree_canopy(doc):
	canopy_block = doc.blocks.new(name='CANOPY')

    #center-x, center-y, center-z, radius, arc-start, and arc-end
	arcs = [
        [0.003, 0.358, 0, 0.1860, 28, 159],
        [0.213, 0.288, 0, 0.1860, 352, 123],
        [0.341, 0.108, 0, 0.1860, 316, 87],
        [0.3390, -0.1130, 0, 0.1860, 280, 51],
		[0.2080, -0.2910, 0, 0.1860, 244, 15],
		[-0.0030, -0.3580, 0, 0.1860, 208, 339],
		[-0.212, -0.288, 0, 0.1860, 172, 303],
		[-0.341, -0.1080, 0, 0.1860, 136, 267],
		[-0.3390, 0.1130, 0, 0.1860, 100, 231],
		[-0.2080, 0.2910, 0, 0.1860, 64, 195]
	]

	for arc_data in arcs:
		cx, cy, cz, r, sa, ea = arc_data
		canopy_block.add_arc(center=(cx, cy), radius=r, start_angle=sa, end_angle=ea)

	return canopy_block

def create_tree(doc, name, spread, girth):
    # Create a new block definition
    block = doc.blocks.new(name=name)

    # Calculate the center points for circles based on spread and girth
    center = (0, 0)

    # trunk
    block.add_circle(center=center, radius=girth / 3.14 / 2)

    # canopy
    #block.add_circle(center=center, radius=spread / 2)
    block.add_blockref('CANOPY', center, dxfattribs={
        'xscale': spread,
        'yscale': spread,
        'rotation': 0,
        "layer": 'vegetation'
    })

    return block

def create_mg_tree(doc, name, spread):
    # Create a new block definition
    block = doc.blocks.new(name=name)

	# spread
    center = (0, 0)
    block.add_blockref('CANOPY', center, dxfattribs={
        'xscale': spread,
        'yscale': spread,
        'rotation': 0,
        "layer": 'vegetation'
    })

	# multi-girth trunk
    block.add_circle(center=(0, 0.0625), radius=0.075)
    block.add_circle(center=(0.0541, -0.0313), radius=0.075)
    block.add_circle(center=(-0.0541, -0.0313), radius=0.075)

    return block

def create_sapling_tree(doc, name, spread):
	# Create a new block definition
    block = doc.blocks.new(name=name)

	# spread
    center = (0, 0)
    block.add_blockref('CANOPY', center, dxfattribs={
        'xscale': spread,
        'yscale': spread,
        'rotation': 0,
        "layer": 'vegetation'
    })

    return block

def tree_splitter(attribs:str):
			values = attribs.split(',')

			is_multi_girth:bool = False
			tree_girth:float = 0
			tree_spread:float = 0

			if len(values) == 3:
				is_multi_girth = True
				tree_girth = round(float(values[1]),3) # girth is the circumference
				tree_spread = float(values[2])
			elif len(values) == 2:
				tree_girth = round(float(values[0]),3) # girth is the circumference
				tree_spread = float(values[1])
			else:
				print(attribs)
				raise ValueError("tree has unknown amount of attributes")

			return is_multi_girth, tree_girth, tree_spread