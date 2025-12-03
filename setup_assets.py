import shutil
import os

src_dir = r"C:\Users\USER\.gemini\antigravity\brain\158c81f4-36ad-4c91-a5bf-594bdfb3f620"
dst_dir = r"C:\Users\USER\.gemini\antigravity\scratch\nyancat_pet\assets"

files = {
    "nyan_cat_sprite_1764755981108.png": "nyan_cat.png",
    "pixel_star_1764756019554.png": "star.png"
}

if not os.path.exists(dst_dir):
    os.makedirs(dst_dir)

for src_name, dst_name in files.items():
    src_path = os.path.join(src_dir, src_name)
    dst_path = os.path.join(dst_dir, dst_name)
    if os.path.exists(src_path):
        shutil.copy2(src_path, dst_path)
        print(f"Copied {src_name} to {dst_name}")
    else:
        print(f"Source file not found: {src_path}")
