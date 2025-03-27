import xml.etree.ElementTree as ET
import os

def ensure_unique_classes(root, prefix):
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    styles = root.findall('.//svg:style', namespaces=ns)
    for style in styles:
        css = style.text
        classes = set(part.split('{')[0].strip() for part in css.split('.') if '{' in part)
        updated_css = css
        for cl in classes:
            new_class_name = f"{prefix}{cl}"
            updated_css = updated_css.replace(f".{cl}", f".{new_class_name}")
            for elem in root.findall(f'.//*[@class="{cl}"]', namespaces=ns):
                elem.set('class', new_class_name)
        style.text = updated_css

def combine_svgs(left_svg_path, right_svg_path, output_svg_path):
    ET.register_namespace('', "http://www.w3.org/2000/svg")
    ET.register_namespace('xlink', "http://www.w3.org/1999/xlink")

    # Parse the SVG files
    tree1 = ET.parse(left_svg_path)
    root1 = tree1.getroot()
    ensure_unique_classes(root1, 'a_')  # Prefix classes in the first SVG with 'a_'
    tree2 = ET.parse(right_svg_path)
    root2 = tree2.getroot()
    ensure_unique_classes(root2, 'b_')  # Prefix classes in the second SVG with 'b_'

    # Assuming viewBox is well defined in SVGs
    viewBox1 = root1.get('viewBox').split()
    viewBox2 = root2.get('viewBox').split()
    width1, height1 = float(viewBox1[2]), float(viewBox1[3])
    width2, height2 = float(viewBox2[2]), float(viewBox2[3])
    new_width = width1 + width2 / 2
    new_height = max(height1, height2)

    # Create a new SVG element to hold both logos
    new_svg = ET.Element('svg', width=str(new_width), height=str(new_height), viewBox=f"0 0 {new_width} {new_height}")

    # Apply transformations and append the elements
    g1 = ET.SubElement(new_svg, 'g', transform=f"translate(0, {(new_height - height1) / 2})")
    g1.extend(root1)
    g2 = ET.SubElement(new_svg, 'g', transform=f"translate({width1 - width2 / 2}, {(new_height - height2) / 2})")
    g2.extend(root2)

    # Write the new SVG to a file
    tree = ET.ElementTree(new_svg)
    tree.write(output_svg_path)

def combine_all_logos(input_dir, output_dir):
    logos = [f for f in os.listdir(input_dir) if f.endswith('.svg')]
    for logo1 in logos:
        for logo2 in logos:
            if logo1 != logo2:
                output_filename = f"{logo1[:-4]}_and_{logo2}"
                output_path = os.path.join(output_dir, output_filename)
                combine_svgs(os.path.join(input_dir, logo1), os.path.join(input_dir, logo2), output_path)
                # For the reverse combination
                reverse_output_filename = f"{logo2[:-4]}_and_{logo1}"
                reverse_output_path = os.path.join(output_dir, reverse_output_filename)
                combine_svgs(os.path.join(input_dir, logo2), os.path.join(input_dir, logo1), reverse_output_path)

# Directories
input_dir = "./nba_logos"
output_dir = "./test_logos"

# Directories
input_dir = "./nba_logos"
output_dir = "./test_logos"

# Combine all logos
combine_all_logos(input_dir, output_dir)

# # File paths
# hawks_logo = "./nba_logos/hawks.svg"
# wizards_logo = "./nba_logos/wizards.svg"
# output_logo = "./test_logos/combined_logo.svg"

# # Combine the SVG files
# combine_svgs(hawks_logo, wizards_logo, output_logo)
