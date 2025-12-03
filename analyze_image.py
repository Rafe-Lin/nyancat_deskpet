from PIL import Image

def analyze_image(path):
    img = Image.open(path)
    print(f"Image size: {img.size}")
    print(f"Mode: {img.mode}")
    
    bbox = img.getbbox()
    if bbox:
        print(f"Content bounding box: {bbox}")
        # Crop and show info about the cropped area
        cropped = img.crop(bbox)
        print(f"Cropped size: {cropped.size}")
    else:
        print("Image is completely transparent!")

analyze_image("assets/star.png")
