import ezdxf
from ezdxf import zoom
from dxf.layers import layer_table, get_code_info
import dxf.shapes

def draw_dxf(radials,stations,scale:int,filename:str) -> None:

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
			raise ValueError("unsupported scale factor")

	# document headers
	doc.header['$PDSIZE'] = point_size
	doc.header['$PDMODE'] = point_style
	doc.header['$INSUNITS'] = units
	doc.header['$LTSCALE'] = text_height * 2

	# setup the document with layers, loop through layers list to populate
	layers = [[key, value[0], value[1]] for key, value in layer_table.items()]
	for layer, colour, line_type in layers:
		doc.layers.add(name=layer, color=colour, linetype=line_type)

	# create the default modelspace
	msp = doc.modelspace()

	# start plotting
	prev_code:float = None
	prev_coord:float = None
	prev_setup:float = None
	radial_colour:int = 226

	# create drawing blocks
	dxf.shapes.flag(doc)

	# insert control points
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

	for pid, code, x, y, z, attrib, sx, sy, sz, ih in radials:
		try:
			layer_name, type, height_code = map(get_code_info(code).get, ('layer_name', 'type', 'height_code'))
		except:
			layer_name = '0'
			type = 'line'
			height_code = code
			raise ValueError("ADAM YOU ARE MISSING %s" % code)

		# point
		point = (x, y, z)
		msp.add_point(point, dxfattribs={"layer": layer_name})

		# point number
		text_pos = (x + -0.075, y + 0.05, z)
		msp.add_text(str(pid), dxfattribs={
			'height': text_height/4,
			'insert': text_pos,
			"layer": 'points'
			})

		# radial
		if prev_setup is not None and prev_setup != (sx,sy,sz,ih):
			radial_colour += 1
		prev_setup = (sx,sy,sz,ih)

		msp.add_line((sx, sy, sz+ih), (x, y, z), dxfattribs={
			"layer": 'radials',
			"color": radial_colour
		})

		# height label (with optional prefix)
		if height_code is not None:
			text_pos = (x + 0.1, y + 0.0, z)
			text_string = "{}{:.2f}".format(height_code, z)
			msp.add_text(text_string, dxfattribs={
				'height': text_height,
				'insert': text_pos,
				"layer": layer_name
			})

		# is it a line, draw back to previous point
		if type == 'line':
			if prev_code is not None and prev_code == code:
				msp.add_line(prev_coord, (x, y, z), dxfattribs={"layer": layer_name})
			prev_code = code
			prev_coord = (x, y, z)

	# zoom to see the created diagram
	zoom.extents(msp)

	# save the document
	doc.saveas(filename); print("done")

# Main block to execute if the script is run directly
if __name__ == "__main__":
	draw_dxf(100,'test.dxf')