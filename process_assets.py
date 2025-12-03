from PIL import Image
import os

def process_image(input_path, output_path):
    img = Image.open(input_path)
    img = img.convert("RGBA")
    
    datas = img.getdata()
    
    new_data = []
    for item in datas:
        # Change all white (also shades of whites) pixels to transparent
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
            
    img.putdata(new_data)
    img.save(output_path, "PNG")
    print(f"Processed {input_path} to {output_path}")

# Paths
src_dir = r"C:\Users\USER\.gemini\antigravity\brain\158c81f4-36ad-4c91-a5bf-594bdfb3f620"
dst_dir = r"C:\Users\USER\.gemini\antigravity\scratch\nyancat_pet\assets"
input_file = os.path.join(src_dir, "nyan_cat_solid_bg_1764756439196.png")
output_file = os.path.join(dst_dir, "nyan_cat.png")

if not os.path.exists(dst_dir):
    os.makedirs(dst_dir)

process_image(input_file, output_file)
