#!/usr/bin/env python3
"""Regenerate every icon size/variant from icon-master.png.

Run `python3 generate-icon.py` first to (re)create icon-master.png, then
run this script from anywhere — paths are resolved relative to this file.
"""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "icon-master.png")
OUT = HERE
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
os.makedirs(OUT, exist_ok=True)

master = Image.open(SRC).convert("RGB")  # 1024x1024, opaque bg

sizes = {
    "icon-512.png": 512,
    "icon-192.png": 192,
    "icon-180.png": 180,   # apple-touch-icon
    "icon-32.png": 32,     # favicon
    "icon-16.png": 16,     # favicon
}
for name, size in sizes.items():
    im = master.resize((size, size), Image.LANCZOS)
    im.save(os.path.join(OUT, name))
    print("saved", name, im.size)

# maskable icon: generate-icon.py already keeps the photo badge within a
# 0.33 W radius (inside Android's 0.4 W safe zone) with the background
# filling edge-to-edge, so the same composition is reused as-is — no extra
# padding needed.
for size in (512, 192):
    im = master.resize((size, size), Image.LANCZOS)
    im.save(os.path.join(OUT, f"icon-maskable-{size}.png"))
    print("saved maskable", size)

# multi-resolution favicon.ico
favicon_sizes = [16, 32, 48]
favicon_imgs = [master.resize((s, s), Image.LANCZOS) for s in favicon_sizes]
favicon_imgs[0].save(
    os.path.join(REPO_ROOT, "favicon.ico"),
    format="ICO",
    sizes=[(s, s) for s in favicon_sizes],
)
print("saved favicon.ico")
