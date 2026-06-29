import os
from PIL import Image

print("\n" + "=" * 60)
print("📦 INPUT: Histopathology Image Tiles")

TILE_DIR = "/home/thrymr/Downloads/Project_MS/tiles_A2/BLOCKS_NORM_MACENKO"

sample_folder = None
tile_files = []

for root, dirs, files in os.walk(TILE_DIR):
    jpgs = [f for f in files if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    if jpgs:
        sample_folder = root
        tile_files = jpgs
        break

if sample_folder is None:
    print("❌ No image tiles found!")
else:
    img_path = os.path.join(sample_folder, tile_files[0])
    img = Image.open(img_path)

    print(f"Patient ID           : {os.path.basename(sample_folder)}")
    print(f"Number of tiles      : {len(tile_files)}")
    print(f"Tile size            : {img.width} × {img.height} pixels")
    print(f"Tile format          : {img.format}")
    print(f"Color mode           : {img.mode}")
    print(f"Normalization        : Macenko stain normalization")
    print(f"Example tile         : {tile_files[0]}")