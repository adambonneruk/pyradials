'''dxf.py stores functions relating to processing, plotting, drawing and finally saving a .dxf file'''
import ezdxf; from ezdxf import zoom
from pyradials.dxf.plot_ref import layers
from plot_ref import code_table, layers

def code_property(instrument_code:str, property:str, attrib:str = None) -> str:
	if instrument_code in code_properties:
		layer, type, label =  code_properties.get(instrument_code)
		match property:
			case "layer": return layer
			case "type": return type
			case "label": return label

	elif instrument_code == "Z": # special case for Z as we want to pass through the comma detail
		#print("found a z with an attrib of %s" % attrib)
		match property:
			case "layer": return 0
			case "type": return "point"
			case "label": return attrib

	elif instrument_code[:2] == "RO":
		match property:
			case "layer": return "control"
			case "type": return "block"
			case "label": return instrument_code[3:] + " "

	else:
		match property:
			case "layer": return 0
			case "type": return "point"
			case "label": return instrument_code

def plot_dxf(c_x_y_z:list,stations:list,scale:int,filename:str) -> None:
	'''pass in coded x, y, and z, coordinates, the drawing scale and the output filename and this function will produce the dxf'''

	# create the dxf document
	doc = ezdxf.new(dxfversion='R2010', setup=True)

	# setup document scale parameters
	point_size:float = 0.1
	point_style:int = 0 # dot
	text_height:float = 0.1
	units:int = 6 # meters

	match scale:
		case 100: # 1:200 Scale for Internals / Floor plans / Measured Building
			text_height = 0.12
			point_size = 0.025
			point_style = 3 # x-cross
		case 200: # 1:200 Scale for Topographical and Utility Surveys
			text_height = 0.24
			point_size = 0.05
			point_style = 2 # +-cross
		case _:
			pass

	# document headers
	doc.header['$PDSIZE'] = point_size
	doc.header['$PDMODE'] = point_style
	doc.header['$INSUNITS'] = units
	doc.header['$LTSCALE'] = text_height * 2

	# setup the document with layers, loop through layers list to populate
	for layer in layers:
		la_name, la_colour, la_linetype = layer
		doc.layers.add(name=la_name, color=la_colour, linetype=la_linetype)

	# create the default modelspace
	msp = doc.modelspace()

	# start plotting
	prev_code = None
	prev_coord = None
	prev_setup = None
	i = 227 # default line colour for radials / work-in-progress

	# Create a block with the name 'FLAG'
	flag = doc.blocks.new(name='FLAG')

	# Add DXF entities to the block 'FLAG'.
	# The default base point (= insertion point) of the block is (0, 0).
	flag.add_lwpolyline([(0, 0), (0, 5), (5, 3), (0, 3)])  # the flag symbol as 2D polyline
	flag.add_circle((0, 0), .04)  # mark the base point with a circle

	for name, x, y, z in stations:
		point = (x, y, z)
		msp.add_point(point, dxfattribs={'layer': 'control'})
		text_pos = (x + 0.1, y + 0.0, z)
		msp.add_text(name, dxfattribs={
				'height': text_height,
				'insert': text_pos,
				"layer": 'control'
			})
		msp.add_blockref('FLAG', point, dxfattribs={
				'xscale': 0.075,
				'yscale': 0.075,
				'rotation': 0,
				"layer": 'control'
			})

	for pid, code, x, y, z, attrib, sx, sy, sz, ih in c_x_y_z:

		#print(c_x_y_z)

		# Add a point at the specified coordinate.
		point = (x, y, z)
		msp.add_point(point, dxfattribs={"layer": code_property(code, "layer")})

		# then add a text label next to the point.
		if code_property(code, "label") != None:
			text_pos = (x + 0.1, y + 0.0, z)
			label = code_property(code, "label", attrib)
			if code_property(code, "type") == "point":
				text_string = "{}{:.2f}".format(label, z)
			else:
				text_string = label
			msp.add_text(text_string, dxfattribs={
				'height': text_height,
				'insert': text_pos,
				"layer": code_property(code, "layer")
			})

		# then add the point number to the point on it's own special layer
		text_pos = (x + -0.075, y + 0.05, z)
		msp.add_text(str(pid), dxfattribs={
			'height': text_height/4,
			'insert': text_pos,
			"layer": 'points'
			})

		# draw the special radials lines
		if prev_setup is not None and prev_setup != (sx,sy,sz,ih):
			i += 1
		prev_setup = (sx,sy,sz,ih)

		msp.add_line((sx, sy, sz+ih), (x, y, z), dxfattribs={
			"layer": 'radials',
			"color": i
		})

		# is this point a line?
		if code_property(code, "type") == "line":
			if prev_code is not None and prev_code == code:
				msp.add_line(prev_coord, (x, y, z), dxfattribs={"layer": code_property(code, "layer")})
			prev_code = code
			prev_coord = (x, y, z)

		# is this point a block?
		if code_property(code, "type") == "block":
			msp.add_blockref('FLAG', point, dxfattribs={
				'xscale': 0.075,
				'yscale': 0.075,
				'rotation': 0,
				"layer": code_property(code, "layer")
			})


	# zoom to see the created diagram
	zoom.extents(msp); print("zoom out")

	# save the document
	doc.saveas(filename); print("save")

if __name__ == "__main__":
	pass
