#!/usr/bin/env python3
"""Procedural treasure map for make.fun bounty
'u-ravendell-charm-the-cartographers-a-one-day-00854547'.

Renders a charming parchment-style treasure map of a fictional island
with 7 labeled places, a dashed route to a big red X, a compass rose,
a sea monster and a tiny ship. Python 3 stdlib + PIL only, fixed seed,
no network, no downloaded assets. Output: entry.png, 1024x1024, <=1 MiB.
"""
import math
import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SEED = 42
W = H = 1024
# entry.png lives at the work-directory root, next to main.ts
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "entry.png")

rng = random.Random(SEED)

# ---------- palette (one consistent parchment palette) ----------
PARCHMENT = (233, 214, 168)
PARCH_DARK = (214, 188, 138)
SEA = (168, 205, 196)
SEA_DEEP = (140, 185, 178)
SAND = (238, 220, 170)
LAND = (196, 205, 138)
LAND_DARK = (168, 182, 110)
INK = (74, 52, 28)          # dark brown ink for outlines + labels
INK_SOFT = (110, 82, 46)
RIVER = (96, 150, 168)
ROUTE = (178, 74, 52)       # dashed route red-brown
RED_X = (196, 42, 28)
GOLD = (198, 148, 52)

FONT_LABEL = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_TEXT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_ITALIC = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

# ---------- canvas: parchment with soft mottling ----------
img = Image.new("RGB", (W, H), PARCHMENT)
d = ImageDraw.Draw(img, "RGBA")

# soft blotches
for _ in range(260):
    x, y = rng.uniform(0, W), rng.uniform(0, H)
    r = rng.uniform(20, 120)
    a = rng.randint(6, 18)
    col = (190, 160, 105, a) if rng.random() < 0.5 else (250, 236, 196, a)
    d.ellipse([x - r, y - r, x + r, y + r], fill=col)

# faint speckles
for _ in range(1400):
    x, y = rng.uniform(0, W), rng.uniform(0, H)
    d.point((x, y), fill=(150, 120, 70, rng.randint(10, 40)))

# ---------- sea ----------
sea = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(sea)
# gentle sea wash: big soft blobs of sea colour
for _ in range(60):
    x, y = rng.uniform(0, W), rng.uniform(0, H)
    r = rng.uniform(60, 200)
    sd.ellipse([x - r, y - r, x + r, y + r], fill=SEA + (26,))
img = Image.alpha_composite(img.convert("RGBA"), sea)
d = ImageDraw.Draw(img, "RGBA")

# wave doodles in the sea (small arcs, away from the island)
def wave(x, y, s, col=INK_SOFT):
    d.arc([x, y, x + s, y + s * 0.6], 200, 340, fill=col + (150,), width=3)
    d.arc([x + s * 0.5, y - s * 0.2, x + s * 1.5, y + s * 0.4], 200, 340,
          fill=col + (150,), width=3)

for (x, y, s) in [(120, 120, 46), (250, 90, 38), (880, 120, 44),
                  (120, 900, 44), (880, 900, 40), (920, 480, 36),
                  (90, 470, 36), (700, 120, 34), (300, 930, 40)]:
    wave(x, y, s)

# ---------- island coastline (seeded blob, smoothed) ----------
CX, CY = 512, 545
N = 72
radii = []
base_rx, base_ry = 330, 285
for i in range(N):
    ang = 2 * math.pi * i / N
    wob = 1 + 0.10 * math.sin(3 * ang + 0.7) + 0.07 * math.sin(7 * ang + 2.1) \
        + 0.05 * math.sin(11 * ang + 4.0) + rng.uniform(-0.03, 0.03)
    radii.append(wob)
# smooth radii
for _ in range(3):
    radii = [(radii[i - 1] + 2 * radii[i] + radii[(i + 1) % N]) / 4
             for i in range(N)]

def blob_points(scale_x, scale_y, ox=0, oy=0):
    pts = []
    for i in range(N):
        ang = 2 * math.pi * i / N
        r = radii[i]
        pts.append((CX + ox + base_rx * r * scale_x * math.cos(ang),
                    CY + oy + base_ry * r * scale_y * math.sin(ang)))
    return pts

outer = blob_points(1.0, 1.0)
inner = blob_points(0.93, 0.92)
d.polygon(outer, fill=SAND + (255,))
d.polygon(inner, fill=LAND + (255,))
# coastline ink: two strokes for a hand-drawn feel
d.line(outer + [outer[0]], fill=INK + (255,), width=5, joint="curve")
d.line(inner + [inner[0]], fill=INK_SOFT + (180,), width=2, joint="curve")

# land texture: soft green patches + dots
for _ in range(90):
    ang = rng.uniform(0, 2 * math.pi)
    rr = rng.uniform(0, 0.85)
    x = CX + base_rx * rr * 0.93 * math.cos(ang)
    y = CY + base_ry * rr * 0.92 * math.sin(ang)
    r = rng.uniform(8, 34)
    d.ellipse([x - r, y - r, x + r, y + r],
              fill=LAND_DARK + (rng.randint(14, 30),))
for _ in range(500):
    ang = rng.uniform(0, 2 * math.pi)
    rr = rng.uniform(0, 0.9)
    x = CX + base_rx * rr * 0.93 * math.cos(ang)
    y = CY + base_ry * rr * 0.92 * math.sin(ang)
    d.point((x, y), fill=(120, 130, 70, rng.randint(20, 60)))

# ---------- hills (small bumps) ----------
def hill(x, y, s):
    d.arc([x - s, y - s, x + s, y + s * 0.7], 180, 360,
          fill=INK_SOFT + (220,), width=3)
    d.arc([x - s * 0.45, y - s * 0.55, x + s * 0.45, y + s * 0.5], 180, 360,
          fill=INK_SOFT + (160,), width=2)

for (x, y, s) in [(430, 470, 26), (480, 500, 20), (660, 500, 24),
                  (380, 590, 22), (610, 690, 20)]:
    hill(x, y, s)

# ---------- volcano: The Grumpy Volcano ----------
VX, VY = 565, 415
d.polygon([(VX - 52, VY + 30), (VX, VY - 42), (VX + 52, VY + 30)],
          outline=INK + (255,), fill=(176, 138, 96, 255), width=4)
d.polygon([(VX - 16, VY - 18), (VX, VY - 42), (VX + 16, VY - 18)],
          outline=INK + (255,), fill=(226, 214, 188, 255), width=3)
# grumpy smoke puffs
for (sx, sy, sr) in [(VX - 8, VY - 62, 12), (VX + 8, VY - 80, 15),
                     (VX + 22, VY - 100, 11)]:
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
              outline=INK_SOFT + (200,), width=3)
# grumpy face on the volcano
d.ellipse([VX - 14, VY - 6, VX - 6, VY + 2], fill=INK + (255,))   # eye L
d.ellipse([VX + 6, VY - 6, VX + 14, VY + 2], fill=INK + (255,))   # eye R
d.line([(VX - 16, VY - 14), (VX - 4, VY - 10)], fill=INK + (255,), width=3)
d.line([(VX + 16, VY - 14), (VX + 4, VY - 10)], fill=INK + (255,), width=3)
d.arc([VX - 12, VY + 8, VX + 12, VY + 24], 20, 160, fill=INK + (255,), width=3)

# ---------- forest: Ticklewood Forest ----------
def tree(x, y, s):
    d.polygon([(x, y - s), (x - s * 0.55, y + s * 0.5),
               (x + s * 0.55, y + s * 0.5)], outline=INK + (230,),
              fill=(96, 128, 74, 255), width=2)
    d.line([(x, y + s * 0.5), (x, y + s * 0.85)], fill=INK + (230,), width=3)

forest = [(640, 585, 20), (680, 610, 24), (715, 580, 18), (655, 640, 22),
          (700, 650, 20), (620, 630, 16), (735, 625, 18), (675, 560, 16)]
for (x, y, s) in forest:
    tree(x, y, s)

# ---------- river: Giggle Brook (volcano -> east coast) ----------
river_pts = [(585, 455), (640, 490), (680, 540), (720, 590), (770, 640),
             (800, 690)]
# smooth polyline via midpoint interpolation
def smooth_path(pts, steps=14):
    out = []
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        for t in range(steps):
            f = t / steps
            out.append((x0 + (x1 - x0) * f, y0 + (y1 - y0) * f))
    out.append(pts[-1])
    return out

rp = smooth_path(river_pts)
d.line(rp, fill=RIVER + (255,), width=9, joint="curve")
d.line(rp, fill=(150, 200, 214, 255), width=4, joint="curve")

# ---------- landing beach + dashed route to the X ----------
BEACH = (318, 782)
ROUTE_PTS = [(318, 782), (380, 730), (450, 700), (520, 660), (580, 600),
             (640, 540), (690, 490), (724, 452)]
rp2 = smooth_path(ROUTE_PTS, steps=20)
# dashed: draw short segments along the path
for i in range(0, len(rp2) - 2, 6):
    x0, y0 = rp2[i]
    x1, y1 = rp2[i + 2]
    d.line([(x0, y0), (x1, y1)], fill=ROUTE + (255,), width=5)
# little anchor doodle at the beach
d.ellipse([BEACH[0] - 4, BEACH[1] - 4, BEACH[0] + 4, BEACH[1] + 4],
          fill=ROUTE + (255,))

# ---------- the big red X ----------
XX, XY = 730, 440
d.line([(XX - 26, XY - 26), (XX + 26, XY + 26)], fill=RED_X + (255,), width=10)
d.line([(XX - 26, XY + 26), (XX + 26, XY - 26)], fill=RED_X + (255,), width=10)
d.ellipse([XX - 34, XY - 34, XX + 34, XY + 34], outline=RED_X + (200,), width=3)

# ---------- crabs at Crab Court (tiny doodles) ----------
def crab(x, y, s):
    d.ellipse([x - s, y - s * 0.6, x + s, y + s * 0.6],
              outline=ROUTE + (255,), fill=(224, 130, 90, 255), width=3)
    d.line([(x - s, y), (x - s * 1.7, y - s * 0.5)], fill=INK + (255,), width=2)
    d.line([(x + s, y), (x + s * 1.7, y - s * 0.5)], fill=INK + (255,), width=2)
    d.ellipse([x - s * 0.4, y - s * 0.9, x - s * 0.1, y - s * 0.6],
              fill=INK + (255,))
    d.ellipse([x + s * 0.1, y - s * 0.9, x + s * 0.4, y - s * 0.6],
              fill=INK + (255,))

crab(380, 355, 12)
crab(420, 340, 9)

# ---------- mermaid tail doodle at Mermaid's Rest ----------
d.arc([760, 640, 800, 690], 0, 180, fill=RIVER + (255,), width=6)
d.polygon([(762, 668), (748, 690), (772, 682)], fill=RIVER + (255,))
d.polygon([(798, 668), (812, 690), (788, 682)], fill=RIVER + (255,))

# ---------- compass rose (bottom-right, in the sea) ----------
CCX, CCY = 862, 838
d.ellipse([CCX - 62, CCY - 62, CCX + 62, CCY + 62],
          outline=INK + (255,), fill=(240, 226, 184, 255), width=4)
d.ellipse([CCX - 50, CCY - 50, CCX + 50, CCY + 50],
          outline=INK_SOFT + (180,), width=2)
for ang_deg, ln, wd in [(0, 46, 5), (90, 46, 5), (180, 46, 5), (270, 46, 5),
                        (45, 30, 3), (135, 30, 3), (225, 30, 3), (315, 30, 3)]:
    a = math.radians(ang_deg - 90)
    d.line([(CCX, CCY),
            (CCX + ln * math.cos(a), CCY + ln * math.sin(a))],
           fill=INK + (255,), width=wd)
# north star tip
d.polygon([(CCX, CCY - 46), (CCX - 7, CCY - 8), (CCX + 7, CCY - 8)],
          fill=RED_X + (255,))
d.ellipse([CCX - 6, CCY - 6, CCX + 6, CCY + 6], fill=INK + (255,))
f_n = font(FONT_LABEL, 24)
d.text((CCX, CCY - 84), "N", font=f_n, fill=INK + (255,), anchor="mm",
       stroke_width=2, stroke_fill=PARCHMENT + (255,))

# ---------- sea monster (top-left sea) ----------
MX, MY = 185, 235
# humps: filled humps so the serpent reads clearly
for (hx, hy, hr) in [(MX - 40, MY + 10, 17), (MX, MY - 6, 21),
                     (MX + 42, MY + 8, 16)]:
    d.pieslice([hx - hr, hy - hr, hx + hr, hy + hr], 180, 360,
               fill=SEA_DEEP + (255,), outline=INK + (255,), width=3)
# head + neck
d.arc([MX + 58, MY - 40, MX + 112, MY + 14], 200, 20,
      fill=INK_SOFT + (230,), width=4)
d.ellipse([MX + 74, MY - 52, MX + 104, MY - 20], outline=INK + (255,),
          fill=SEA_DEEP + (255,), width=3)
d.ellipse([MX + 86, MY - 44, MX + 92, MY - 38], fill=INK + (255,))  # eye
d.line([(MX + 98, MY - 28), (MX + 108, MY - 32)], fill=INK + (255,), width=2)
# little tail curl at the back
d.arc([MX - 78, MY - 6, MX - 48, MY + 24], 90, 270,
      fill=INK_SOFT + (230,), width=4)

# ---------- tiny ship (top-right sea) ----------
SX, SY = 800, 165
d.polygon([(SX - 34, SY + 14), (SX + 34, SY + 14), (SX + 22, SY + 30),
           (SX - 22, SY + 30)], outline=INK + (255,),
          fill=(150, 100, 60, 255), width=3)
d.line([(SX, SY + 14), (SX, SY - 34)], fill=INK + (255,), width=3)
d.polygon([(SX + 2, SY - 32), (SX + 2, SY + 10), (SX + 30, SY + 10)],
          outline=INK + (255,), fill=(240, 226, 184, 255), width=2)
d.polygon([(SX - 2, SY - 26), (SX - 2, SY + 10), (SX - 24, SY + 10)],
          outline=INK + (255,), fill=(240, 226, 184, 255), width=2)
d.arc([SX - 44, SY + 34, SX + 44, SY + 52], 0, 180,
      fill=INK_SOFT + (200,), width=3)

# ---------- labels (large, high contrast, haloed, no overlaps) ----------
f_big = font(FONT_LABEL, 32)
f_mid = font(FONT_LABEL, 30)
f_small = font(FONT_LABEL, 24)
f_joke = font(FONT_ITALIC, 21)

def label(text, x, y, fnt=f_big, anchor="mm"):
    d.text((x, y), text, font=fnt, fill=INK + (255,), anchor=anchor,
           stroke_width=4, stroke_fill=(250, 238, 200, 255))

# 1. Whispering Dunes — south-west, near the landing beach
label("Whispering Dunes", 335, 735, f_big)
# 2. Fort Snooze — west coast
label("Fort Snooze", 268, 565, f_big)
# 3. Crab Court — north coast
label("Crab Court", 375, 305, f_big)
# 4. The Grumpy Volcano — centre-north, above the volcano cone
label("The Grumpy Volcano", 630, 330, f_mid)
# 5. Ticklewood Forest — centre-east forest
label("Ticklewood Forest", 668, 700, f_mid)
# 6. Mermaid's Rest — east coast lagoon (kept clear of the compass "N")
label("Mermaid's Rest", 700, 748, f_mid)
# 7. Captain's Last Laugh — the X, the destination
label("Captain's Last Laugh", 700, 380, f_mid)
# small joke labels
label("Giggle Brook", 700, 545, f_small)
label("Here be grumpy dragons", 150, 420, f_joke)
label("Do NOT feed the kraken", 800, 215, f_joke)
label("No refunds beyond this point", 210, 862, f_joke)

# title cartouche (top centre, in the sea, clear of the island)
d.rounded_rectangle([182, 18, 842, 92], radius=18,
                    outline=INK + (255,), fill=(240, 226, 184, 255), width=4)
f_title = font(FONT_LABEL, 40)
d.text((512, 44), "ISLE OF MISCHIEF", font=f_title, fill=INK + (255,),
       anchor="mm")
f_sub = font(FONT_ITALIC, 20)
d.text((512, 74), "drawn by a cartographer who got lost twice",
       font=f_sub, fill=INK_SOFT + (255,), anchor="mm")

# ---------- vignette / aged edges ----------
vig = Image.new("L", (W, H), 0)
vd = ImageDraw.Draw(vig)
vd.rectangle([0, 0, W, H], fill=0)
vd.rectangle([26, 26, W - 26, H - 26], fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(28))
dark = Image.new("RGBA", (W, H), (120, 84, 40, 90))
img = Image.composite(img, Image.alpha_composite(img, dark), vig)

img = img.convert("RGB")
img.save(OUT, "PNG", optimize=True)
print("saved", OUT, img.size)
