import ezdxf, math

def flag(doc):
    flag_block = doc.blocks.new(name='FLAG')

    # Add DXF entities to the block 'FLAG'.
    # The default base point (= insertion point) of the block is (0, 0).
    flag_block.add_lwpolyline([(0, 0), (0, 5), (5, 3), (0, 3)])  # the flag symbol as 2D polyline
    flag_block.add_circle((0, 0), .04)  # mark the base point with a circle

    return flag_block