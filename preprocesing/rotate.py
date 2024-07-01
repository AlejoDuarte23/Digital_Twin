import os
import cairosvg

# Path to the original SVG file
original_svg_path = '/Users/alejandroduarte/Documents/digital_twin_engine/static/models/truck.svg'

# Path to save the rotated SVG files
output_dir = '/Users/alejandroduarte/Documents/digital_twin_engine/static/models/'

# Function to rotate and save SVG
def rotate_and_save_svg(input_path, output_path, angle):
    with open(input_path, 'r') as file:
        svg_data = file.read()

    # Create a new SVG with the rotation applied
    rotated_svg_data = f"""
    <svg xmlns="http://www.w3.org/2000/svg">
      <g transform="rotate({angle}, 12.5, 12.5)">
        {svg_data}
      </g>
    </svg>
    """

    with open(output_path, 'w') as file:
        file.write(rotated_svg_data)

# Generate rotated images
rotate_and_save_svg(original_svg_path, os.path.join(output_dir, 'truckright.svg'), 90)
rotate_and_save_svg(original_svg_path, os.path.join(output_dir, 'truckdown.svg'), 180)
rotate_and_save_svg(original_svg_path, os.path.join(output_dir, 'truckleft.svg'), 270)

print("Rotated SVG images have been generated and saved.")