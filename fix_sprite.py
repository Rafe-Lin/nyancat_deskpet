from PIL import Image

def fix_sprite(path):
    img = Image.open(path)
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        # Resize to reasonable height (e.g. 64px)
        base_height = 64
        w_percent = (base_height / float(img.size[1]))
        w_size = int((float(img.size[0]) * float(w_percent)))
        img = img.resize((w_size, base_height), Image.Resampling.LANCZOS)
        img.save(path)
        print(f"Fixed sprite saved to {path}. New size: {img.size}")
    else:
        print("Image is empty!")

fix_sprite("assets/nyan_cat.png")
