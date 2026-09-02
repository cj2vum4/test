#!/usr/bin/env python3
"""Generate a glowing potsticker (鍋貼) PWA icon set as real PNG raster images.

Design: a golden-brown pan-fried potsticker (gyoza/guotie) with a
pleated crimped top and its signature crispy lace "ice-flower" skirt
peeking out beneath, set in a warm ember glow against a deep wood-brown
radial background. Drawn procedurally with Pillow at high supersampling
for clean anti-aliased edges; blurred layers compose the glow.
"""
import math
import os
import random
from PIL import Image, ImageDraw, ImageFilter, ImageChops

OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon-master.png")

SS = 4
MASTER = 1024
W = H = MASTER * SS

# ---- palette (wood / ember brand tones) ----
BG_DEEP = (15, 9, 7)
BG_EDGE = (44, 25, 17)
GLOW_CORE = (255, 181, 79)
GLOW_MID = (233, 132, 37)
GLOW_OUTER = (150, 64, 21)
DOUGH_LIGHT = (250, 227, 181)
DOUGH_MID = (226, 174, 103)
SEAR_DARK = (128, 67, 29)
SEAR_DARKER = (82, 41, 17)
SPOT = (56, 24, 9)
RIM_LIGHT = (255, 232, 182)
CREASE = (150, 90, 42)


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


canvas = radial_gradient((W, H), BG_EDGE, BG_DEEP, (W * 0.5, H * 0.46), W * 0.75).convert("RGBA")

cx, cy = W * 0.5, H * 0.56

# --------------------------------------------------------- ambient glow ---
glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow_layer)
for rad, col, alpha in [
    (0.48, GLOW_OUTER, 120),
    (0.37, GLOW_MID, 165),
    (0.27, GLOW_CORE, 205),
]:
    r = W * rad
    gd.ellipse([cx - r, cy - r * 0.68, cx + r, cy + r * 0.68], fill=col + (alpha,))
glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(W * 0.045))
canvas = Image.alpha_composite(canvas, glow_layer)

# body geometry (defined early so skirt/shadow can reference it)
body_w = W * 0.29
body_h = H * 0.235
body_cy = cy - H * 0.045
sear_bottom_y = body_cy + body_h * 0.40  # approx lowest point of the belly

# ---------------------------------------------------- ground contact shadow
shadow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
shd = ImageDraw.Draw(shadow_layer)
shd.ellipse([cx - W * 0.26, sear_bottom_y + H * 0.05,
             cx + W * 0.26, sear_bottom_y + H * 0.14], fill=(8, 4, 3, 150))
shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(W * 0.02))
canvas = Image.alpha_composite(canvas, shadow_layer)

# ------------------------------------------------- crispy lace ice-skirt ---
# Peeks out from beneath the dumpling on both sides & the front, doubling
# as its glowing halo.
skirt_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(skirt_layer)
skirt_rx = body_w * 1.34
skirt_ry = H * 0.055
skirt_cy = sear_bottom_y - H * 0.01
sd.ellipse([cx - skirt_rx, skirt_cy - skirt_ry, cx + skirt_rx, skirt_cy + skirt_ry],
           fill=GLOW_CORE + (235,))
random.seed(11)
for _ in range(40):
    ang = random.uniform(0, math.pi * 2)
    fr = random.uniform(0.15, 0.95)
    px = cx + math.cos(ang) * skirt_rx * fr
    py = skirt_cy + math.sin(ang) * skirt_ry * fr
    length = random.uniform(0.025, 0.07) * W
    ang2 = ang + random.uniform(-0.9, 0.9)
    ex, ey = px + math.cos(ang2) * length, py + math.sin(ang2) * length * 0.5
    sd.line([px, py, ex, ey], fill=(255, 246, 218, 140), width=max(1, int(W * 0.0015)))
mask = Image.new("L", (W, H), 0)
md = ImageDraw.Draw(mask)
md.ellipse([cx - skirt_rx, skirt_cy - skirt_ry, cx + skirt_rx, skirt_cy + skirt_ry], fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(W * 0.006))
skirt_layer = skirt_layer.filter(ImageFilter.GaussianBlur(W * 0.004))
skirt_layer.putalpha(ImageChops.multiply(skirt_layer.split()[3], mask))
canvas = Image.alpha_composite(canvas, skirt_layer)

# ------------------------------------------------------------- dumpling ---
# A smooth crescent body with a small fan of crimped pleats bunched along
# the crest of the top ridge (matching how a real gyoza/guotie folds),
# rather than scallops running the whole silhouette.
num_pleats = 5
pleat_r = body_w * 0.115
pleat_t0, pleat_t1 = 0.30 * math.pi, 0.70 * math.pi


def seam_edge(t):
    """t in [0, pi]; the smooth dome the pleats are anchored to."""
    x = cx - body_w * math.cos(t)
    y = body_cy - body_h * (math.sin(t) ** 0.88)
    return x, y


def top_edge(t):
    return seam_edge(t)


def bottom_edge(u):
    """u in [0, 1] from right to left; seared belly curve."""
    x = cx + body_w - 2 * body_w * u
    y = body_cy + body_h * 0.40 * (math.sin(u * math.pi) ** 0.7) + body_h * 0.10
    return x, y


n, n2 = 240, 140
pts = [seam_edge(i / n * math.pi) for i in range(n + 1)]
pts += [bottom_edge(i / n2) for i in range(n2 + 1)]

body_mask_layer = Image.new("L", (W, H), 0)
bmd = ImageDraw.Draw(body_mask_layer)
bmd.polygon(pts, fill=255)
# fuse a small fan of rounded pleat bumps onto the crest of the dome —
# overlapping circles read as soft, plump gyoza pleats.
pleat_centers = []
for i in range(num_pleats):
    t = pleat_t0 + (i + 0.5) / num_pleats * (pleat_t1 - pleat_t0)
    px, py = seam_edge(t)
    py -= pleat_r * 0.30
    pleat_centers.append((px, py, t))
    bmd.ellipse([px - pleat_r, py - pleat_r * 0.85, px + pleat_r, py + pleat_r * 0.85], fill=255)
body_mask_layer = body_mask_layer.filter(ImageFilter.GaussianBlur(W * 0.0018))

top_y = body_cy - body_h - pleat_r
bot_y = body_cy + body_h * 0.55
shade = Image.new("L", (W, H), 0)
shdraw = ImageDraw.Draw(shade)
for yy in range(int(top_y), int(bot_y) + 1):
    t = max(0.0, min(1.0, (yy - top_y) / max(1, (bot_y - top_y))))
    shdraw.line([(0, yy), (W, yy)], fill=int(255 * t))
tinted_light = Image.new("RGB", (W, H), DOUGH_LIGHT)
tinted_dark = Image.new("RGB", (W, H), SEAR_DARK)
blended = Image.composite(tinted_dark, tinted_light, shade)
body_rgba = Image.new("RGBA", (W, H), (0, 0, 0, 0))
body_rgba.paste(blended, (0, 0))
body_rgba.putalpha(body_mask_layer)
canvas = Image.alpha_composite(canvas, body_rgba)

# crispy sear crescent along the very bottom edge (darker, mottled)
sear_top_y = body_cy + body_h * 0.16
sear_mask_layer = Image.new("L", (W, H), 0)
smd = ImageDraw.Draw(sear_mask_layer)
sear_pts = [bottom_edge(i / n2) for i in range(n2 + 1)]
sear_pts += [(cx - body_w + 2 * body_w * (i / n2), sear_top_y) for i in range(n2 + 1)]
smd.polygon(sear_pts, fill=255)
sear_rgb = Image.new("RGB", (W, H), SEAR_DARK)
sdw = ImageDraw.Draw(sear_rgb)
random.seed(3)
for _ in range(240):
    x = random.uniform(cx - body_w, cx + body_w)
    y = random.uniform(sear_top_y, sear_bottom_y + body_h * 0.05)
    r = random.uniform(W * 0.0018, W * 0.0075)
    c = SEAR_DARKER if random.random() < 0.6 else SPOT
    sdw.ellipse([x - r, y - r, x + r, y + r], fill=c)
sear_final = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sear_final.paste(sear_rgb, (0, 0))
sear_final.putalpha(sear_mask_layer)
canvas = Image.alpha_composite(canvas, sear_final)

# crease lines at each pleat valley (where adjacent bumps meet) — short
# subtle fold marks, not reaching deep into the body.
crease_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
cd = ImageDraw.Draw(crease_layer)
for i in range(1, num_pleats):
    t = pleat_t0 + i / num_pleats * (pleat_t1 - pleat_t0)
    x, y = seam_edge(t)
    y -= pleat_r * 0.25
    x2 = x
    y2 = y + pleat_r * 0.85
    cd.line([x, y, x2, y2], fill=CREASE + (130,), width=max(1, int(W * 0.002)))
crease_layer = crease_layer.filter(ImageFilter.GaussianBlur(W * 0.0018))
canvas = Image.alpha_composite(canvas, crease_layer)

# rim light: a soft bright arc over the top of each pleat bump and along
# the plain shoulders of the dome, catching the glow.
rim_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
rd = ImageDraw.Draw(rim_layer)
rim_w = max(2, int(W * 0.005))
rim_pts = [seam_edge(i / n * math.pi) for i in range(n + 1)]
rd.line(rim_pts, fill=RIM_LIGHT + (140,), width=rim_w, joint="curve")
for (px, py, t) in pleat_centers:
    bbox = [px - pleat_r, py - pleat_r * 0.85, px + pleat_r, py + pleat_r * 0.85]
    rd.arc(bbox, 178, 362, fill=RIM_LIGHT + (215,), width=rim_w)
rim_layer = rim_layer.filter(ImageFilter.GaussianBlur(W * 0.002))
canvas = Image.alpha_composite(canvas, rim_layer)

# soft glossy highlight, upper-left of the dough
sheen = Image.new("RGBA", (W, H), (0, 0, 0, 0))
shn = ImageDraw.Draw(sheen)
shn.ellipse([cx - body_w * 0.5, body_cy - body_h * 0.85,
             cx - body_w * 0.02, body_cy - body_h * 0.28],
            fill=(255, 255, 255, 55))
sheen = sheen.filter(ImageFilter.GaussianBlur(W * 0.018))
canvas = Image.alpha_composite(canvas, sheen)

# floating spark/steam motes
mote_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
mdw = ImageDraw.Draw(mote_layer)
for mx, my, mr, ma in [
    (cx + body_w * 1.15, body_cy - body_h * 1.05, W * 0.007, 210),
    (cx - body_w * 1.25, body_cy - body_h * 0.55, W * 0.0045, 170),
    (cx + body_w * 1.35, body_cy - body_h * 0.15, W * 0.0035, 140),
]:
    mdw.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=RIM_LIGHT + (ma,))
mote_layer = mote_layer.filter(ImageFilter.GaussianBlur(W * 0.0035))
canvas = Image.alpha_composite(canvas, mote_layer)

# ------------------------------------------------------------- finalize ---
final = canvas.convert("RGB").resize((MASTER, MASTER), Image.LANCZOS)
final.save(OUT_PATH)
print("done", final.size, "->", OUT_PATH)
