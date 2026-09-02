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
BG_EDGE = (44, 25, 17)  # matches make_icon.py's outer gradient color, for seamless padding

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

# maskable icon: pad content to ~84% so it survives Android's safe-zone crop
def make_maskable(size):
    canvas = Image.new("RGB", (size, size), BG_EDGE)
    inner = int(size * 0.84)
    resized = master.resize((inner, inner), Image.LANCZOS)
    off = (size - inner) // 2
    canvas.paste(resized, (off, off))
    return canvas

for size in (512, 192):
    im = make_maskable(size)
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
