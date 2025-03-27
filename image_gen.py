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

    tree1 = ET.parse(left_svg_path)
    root1 = tree1.getroot()
    ensure_unique_classes(root1, 'a_')

    tree2 = ET.parse(right_svg_path)
    root2 = tree2.getroot()
    ensure_unique_classes(root2, 'b_')

    target_size = 200
    overlap = target_size // 2
    final_width = target_size + overlap

    new_svg = ET.Element('svg', width=str(final_width), height=str(target_size), viewBox=f"0 0 {final_width} {target_size}")

    scale1 = target_size / float(root1.get('viewBox').split()[2])
    scale2 = target_size / float(root2.get('viewBox').split()[2])

    g1 = ET.SubElement(new_svg, 'g', transform=f"translate(0,0) scale({scale1})")
    g1.extend(root1)

    g2 = ET.SubElement(new_svg, 'g', transform=f"translate({overlap},0) scale({scale2})")
    g2.extend(root2)

    tree = ET.ElementTree(new_svg)
    tree.write(output_svg_path)

def combine_all_logos(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    logos = [f for f in os.listdir(input_dir) if f.endswith('.svg')]
    for logo1 in logos:
        for logo2 in logos:
            if logo1 != logo2:
                output_filename = f"{logo1[:-4]}_and_{logo2}"
                output_path = os.path.join(output_dir, output_filename)
                combine_svgs(os.path.join(input_dir, logo1), os.path.join(input_dir, logo2), output_path)

# Example directories
input_dir = "./nba_logos"
output_dir = "./test_logos"

# Combine all logos
combine_all_logos(input_dir, output_dir)
