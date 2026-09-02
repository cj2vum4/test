#!/usr/bin/env python3
"""Build a glowing potsticker PWA icon from a REAL photograph.

Source: assets/hero-poster.jpg — an actual food-photography shot already
used on the site's hero section — cropped to the chopstick-held,
crispy-bottomed potsticker close-up. The crop is bloomed/warmed for a
"glowing" look and set as a feathered circular badge over a dark ember
radial-glow background. This keeps the icon a genuine photographic image
rather than an illustration.

Run `python3 generate-icon.py` (needs Pillow) to produce icon-master.png
in this folder, then `python3 export-sizes.py` to derive every icon size
manifest.json / index.html reference.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(REPO_ROOT, "assets", "hero-poster.jpg")
OUT_PATH = os.path.join(HERE, "icon-master.png")

MASTER = 1024
W = H = MASTER

# ---- palette (wood / ember brand tones), matching the site's theme ----
BG_DEEP = (15, 9, 7)
BG_EDGE = (44, 25, 17)
GLOW_CORE = (255, 181, 79)
GLOW_MID = (233, 132, 37)
GLOW_OUTER = (150, 64, 21)


def radial_gradient(size, inner, outer, center, radius):
    w, h = size
    small = 256
    simg = Image.new("RGB", (small, small))
    spx = simg.load()
    scx, scy = small * center[0] / w, small * center[1] / h
    sradius = small * radius / w
    for y in range(small):
        for x in range(small):
            d = min(1.0, math.hypot(x - scx, y - scy) / sradius)
            spx[x, y] = tuple(int(inner[i] + (outer[i] - inner[i]) * d) for i in range(3))
    return simg.resize(size, Image.BICUBIC)


# --------------------------------------------------------- background ---
cx, cy = W * 0.5, H * 0.5
canvas = radial_gradient((W, H), BG_EDGE, BG_DEEP, (cx, cy), W * 0.75).convert("RGBA")

glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow_layer)
for rad, col, alpha in [
    (0.50, GLOW_OUTER, 130),
    (0.40, GLOW_MID, 175),
    (0.30, GLOW_CORE, 210),
]:
    r = W * rad
    gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col + (alpha,))
glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(W * 0.05))
canvas = Image.alpha_composite(canvas, glow_layer)

# ------------------------------------------------------------ the photo ---
photo_full = Image.open(SRC).convert("RGB")
# Crop to the chopstick-held potsticker close-up (steam, crispy base, ooze).
# Tuned against hero-poster.jpg's native 976x1235 — re-check this box if
# that source photo is ever replaced.
box = (566, 250, 976, 660)
crop = photo_full.crop(box)  # ~410x410, real photograph

badge_d = int(W * 0.66)  # badge radius (0.33 W) stays inside the 0.4 W
                         # maskable-icon safe zone
crop = crop.resize((badge_d, badge_d), Image.LANCZOS)

# bloom: lift the bright crispy/steam highlights and screen them back in
gray = crop.convert("L")
bright_mask = gray.point(lambda p: max(0, min(255, int((p - 175) * 3))))
highlights = Image.composite(crop, Image.new("RGB", crop.size, (0, 0, 0)), bright_mask)
highlights = highlights.filter(ImageFilter.GaussianBlur(badge_d * 0.025))
bloomed = ImageChops.screen(crop, highlights)

# warm grade + punch, then sharpen to counter the upscale softness
r, g, b = bloomed.split()
r = r.point(lambda p: min(255, int(p * 1.05)))
b = b.point(lambda p: max(0, int(p * 0.96)))
bloomed = Image.merge("RGB", [r, g, b])
bloomed = ImageEnhance.Color(bloomed).enhance(1.18)
bloomed = ImageEnhance.Contrast(bloomed).enhance(1.10)
bloomed = ImageEnhance.Sharpness(bloomed).enhance(1.6)
bloomed = bloomed.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))

# feathered circular mask so the photo melts into the glow behind it
mask = Image.new("L", (badge_d, badge_d), 0)
md = ImageDraw.Draw(mask)
feather = badge_d * 0.05
md.ellipse([feather, feather, badge_d - feather, badge_d - feather], fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(feather * 0.9))

badge_rgba = bloomed.convert("RGBA")
badge_rgba.putalpha(mask)

paste_xy = (int(cx - badge_d / 2), int(cy - badge_d / 2))
canvas.alpha_composite(badge_rgba, paste_xy)

# bright rim ring right at the badge edge to sell the glowing transition
rim_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
rd = ImageDraw.Draw(rim_layer)
rr = badge_d / 2 - feather * 0.5
rd.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=GLOW_CORE + (235,),
           width=max(2, int(W * 0.006)))
rim_layer = rim_layer.filter(ImageFilter.GaussianBlur(W * 0.006))
canvas = Image.alpha_composite(canvas, rim_layer)

# a couple of warm sparkle motes for extra sparkle/life
mote_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
mdw = ImageDraw.Draw(mote_layer)
for mx, my, mr, ma in [
    (cx + badge_d * 0.42, cy - badge_d * 0.46, W * 0.007, 210),
    (cx - badge_d * 0.48, cy - badge_d * 0.30, W * 0.0045, 170),
    (cx + badge_d * 0.50, cy + badge_d * 0.10, W * 0.0035, 140),
]:
    mdw.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(255, 232, 182, ma))
mote_layer = mote_layer.filter(ImageFilter.GaussianBlur(W * 0.0035))
canvas = Image.alpha_composite(canvas, mote_layer)

final = canvas.convert("RGB")
final.save(OUT_PATH, quality=95)
print("done", final.size, "->", OUT_PATH)
