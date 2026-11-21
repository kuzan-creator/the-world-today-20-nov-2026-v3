#!/usr/bin/env python3
"""The World Today — Friday 20 November 2026: 38 stories, 7 regions.
v3 redrawn FRESH: 2x supersampling + gradients + shading + texture.
Pillow only, deterministic (no random, no clock, no network).
Renders at 2048x2048, downscales to 1024x1024 with LANCZOS.
"""
import math
from PIL import Image, ImageDraw, ImageFont

SCALE = 2
W, H = 1024, 1024
SW, SH = W * SCALE, H * SCALE

LIB = "/usr/share/fonts/truetype/liberation/"

# ---------------------------------------------------------------- helpers
def S(v):
    return int(round(v * SCALE))

def B(x0, y0, x1, y1):
    return [S(x0), S(y0), S(x1), S(y1)]

def lerp(c1, c2, t):
    return tuple(int(round(a + (b - a) * t)) for a, b in zip(c1, c2))

def vgrad(dr, x0, y0, x1, y1, c1, c2):
    """Vertical gradient, line by line (1x coords)."""
    h = S(y1) - S(y0)
    if h <= 0:
        return
    for i in range(h):
        t = i / max(1, h - 1)
        dr.line([(S(x0), S(y0) + i), (S(x1), S(y0) + i)], fill=lerp(c1, c2, t))

def vgrad3(dr, x0, y0, x1, y1, c1, c2, c3):
    mid = (y0 + y1) / 2.0
    vgrad(dr, x0, y0, x1, mid, c1, c2)
    vgrad(dr, x0, mid, x1, y1, c2, c3)

def hgrad(dr, x0, y0, x1, y1, c1, c2):
    w = S(x1) - S(x0)
    if w <= 0:
        return
    for i in range(w):
        t = i / max(1, w - 1)
        dr.line([(S(x0) + i, S(y0)), (S(x0) + i, S(y1))], fill=lerp(c1, c2, t))

def rr(dr, x0, y0, x1, y1, r, **kw):
    dr.rounded_rectangle(B(x0, y0, x1, y1), radius=S(r), **kw)

def ell(dr, x0, y0, x1, y1, **kw):
    dr.ellipse(B(x0, y0, x1, y1), **kw)

def oell(x0, y0, x1, y1, fill):
    """Ellipse on the true-alpha overlay layer (blends on composite)."""
    od.ellipse(B(x0, y0, x1, y1), fill=fill)

def orect(x0, y0, x1, y1, fill):
    """Rectangle on the true-alpha overlay layer (blends on composite)."""
    od.rectangle(B(x0, y0, x1, y1), fill=fill)

def line(dr, pts, fill, w=1):
    dr.line([(S(x), S(y)) for x, y in pts], fill=fill, width=max(1, S(w)),
            joint="curve")

def poly(dr, pts, **kw):
    dr.polygon([(S(x), S(y)) for x, y in pts], **kw)

def arc(dr, x0, y0, x1, y1, a0, a1, fill, w=1):
    dr.arc(B(x0, y0, x1, y1), a0, a1, fill=fill, width=max(1, S(w)))

def txt(dr, x, y, s, f, fill, anchor="la"):
    dr.text((S(x), S(y)), s, font=f, fill=fill, anchor=anchor)

def tw(dr, s, f):
    return dr.textlength(s, font=f) / SCALE

_fonts = {}
def F(name, size):
    key = (name, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(LIB + name, S(size))
    return _fonts[key]

def serif_b(sz): return F("LiberationSerif-Bold.ttf", sz)
def serif(sz): return F("LiberationSerif-Regular.ttf", sz)
def serif_i(sz): return F("LiberationSerif-Italic.ttf", sz)
def sans_b(sz): return F("LiberationSans-Bold.ttf", sz)
def sans(sz): return F("LiberationSans-Regular.ttf", sz)
def sans_i(sz): return F("LiberationSans-Italic.ttf", sz)

def grain(dr, x0, y0, x1, y1, phase=0.0, alpha=8, step=7, base=(255, 255, 255),
          base2=None):
    """Deterministic sine-hash speckle. 1x coords; dots are 1px at 1x.
    NOTE: ImageDraw on RGBA replaces pixels, so `alpha` is ignored in the
    final RGB output — density (threshold), step and the two base colours
    are what actually add variety."""
    for gx in range(int(x0), int(x1), step):
        for gy in range(int(y0), int(y1), step):
            v = math.sin(gx * 12.9898 + gy * 78.233 + phase) * 43758.5453
            if v - math.floor(v) < 0.60:
                b = base
                if base2 is not None:
                    v2 = math.sin(gx * 26.651 + gy * 11.135 + phase * 2.0) * 24634.6345
                    if v2 - math.floor(v2) < 0.5:
                        b = base2
                dr.rectangle([S(gx), S(gy), S(gx) + SCALE - 1, S(gy) + SCALE - 1],
                             fill=b + (alpha,))

# ---------------------------------------------------------------- palette
PAPER_TOP = (248, 241, 222)
PAPER_BOT = (240, 229, 198)
INK = (26, 26, 26)
BODY = (64, 60, 52)
GREY = (96, 90, 78)
RED = (163, 18, 18)
RED_D = (122, 10, 10)
NAVY = (16, 41, 74)
NAVY_D = (10, 28, 52)
GOLD = (200, 144, 26)
GOLD_B = (212, 160, 23)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- canvas
img = Image.new("RGBA", (SW, SH), PAPER_TOP + (255,))
d = ImageDraw.Draw(img)
# separate layer for TRUE alpha shading (ImageDraw on RGBA replaces pixels
# instead of blending, so translucent shapes go here and are composited
# at the end, like the BEAMS searchlights)
ov = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
od = ImageDraw.Draw(ov)
vgrad3(d, 0, 0, W, H, PAPER_TOP, (244, 235, 210), PAPER_BOT)
grain(d, 0, 0, W, H, phase=1.7, alpha=6, step=5, base2=(216, 206, 182))

M = 28            # side margin
CW = W - 2 * M    # 968 content width

# ---------------------------------------------------------------- top strip
txt(d, W / 2, 12, "38 STORIES  ·  7 REGIONS  ·  EVERY ONE DATED FRIDAY 20 NOVEMBER 2026",
    sans_b(12), RED, anchor="ma")
line(d, [(M, 28), (M + 120, 28)], (170, 150, 120), 1)
line(d, [(W - M - 120, 28), (W - M, 28)], (170, 150, 120), 1)

# kicker
txt(d, W / 2, 32, "T H E   W O R L D   T O D A Y", sans_b(15), RED, anchor="ma")

# masthead (shrink until it fits)
_msize = 88
while tw(d, "Friday 20 November 2026", serif_b(_msize)) > 960 and _msize > 70:
    _msize -= 2
txt(d, W / 2, 50, "Friday 20 November 2026", serif_b(_msize), INK, anchor="ma")
line(d, [(M, 132), (W - M, 132)], (60, 50, 40), 2)

# subhead
txt(d, W / 2, 137, "Russian missiles hit Kyiv's bridges  ·  Cyclone Akvan strikes India  ·  "
                   "An AI sell-off sinks Asia's markets",
    serif_i(16), (58, 52, 44), anchor="ma")

# ---------------------------------------------------------------- number strip
NS_Y0, NS_Y1 = 158, 196
vgrad3(d, M, NS_Y0, W - M, NS_Y1, (255, 253, 246), (248, 244, 231), (240, 233, 214))
rr(d, M, NS_Y0, W - M, NS_Y1, 2, outline=(198, 186, 164), width=1)
stats = [
    ("3", "bridges hit in Kyiv"),
    ("300,000+", "evacuated before Akvan"),
    ("\u22126.2%", "Taiwan Taiex this week"),
    ("100,000", "youth visas a year, UK\u2013EU"),
    ("$2.36bn", "GTA VI first sales"),
    ("8 yrs", "BepiColombo to Mercury"),
]
cell_w = CW / 6.0
for i, (num, lab) in enumerate(stats):
    cx = M + cell_w * (i + 0.5)
    if i:
        line(d, [(M + cell_w * i, NS_Y0 + 6), (M + cell_w * i, NS_Y1 - 6)],
             (205, 194, 172), 1)
    txt(d, cx, 163, num, serif_b(21), RED, anchor="ma")
    txt(d, cx, 186, lab, sans(9), GREY, anchor="ma")

# ---------------------------------------------------------------- region bar
RB_Y0, RB_Y1 = 200, 220
regions = [
    ("EUROPE 8", 203.8, 10, (47, 93, 138), (30, 66, 104)),
    ("ASIA 8", 203.8, 10, (163, 51, 39), (120, 34, 26)),
    ("MIDDLE EAST 6", 152.8, 10, (185, 138, 29), (150, 108, 20)),
    ("AFRICA 4", 101.9, 10, (46, 125, 91), (30, 96, 68)),
    ("AMERICAS 9", 210.7, 10, (107, 63, 160), (80, 44, 128)),
    ("OCEANIA 2", 51.0, 9, (63, 125, 140), (44, 96, 112)),
    ("GLOBAL 1", 44.0, 8, (88, 84, 78), (64, 60, 56)),
]
_x = M
for j, (lab, wdt, fsz, c1, c2) in enumerate(regions):
    if j == len(regions) - 1:
        wdt = (W - M) - _x
    vgrad(d, _x, RB_Y0, _x + wdt, RB_Y1, c1, c2)
    txt(d, _x + wdt / 2, 206, lab, sans_b(fsz), WHITE, anchor="ma")
    _x += wdt

# ---------------------------------------------------------------- heroes
BEAMS = []  # (points, alpha) searchlight polygons, composited at the end
HERO_Y0, HERO_ART_H = 226, 114
HERO_W = (CW - 20) / 3.0
HERO_X = [M, M + HERO_W + 10, M + 2 * (HERO_W + 10)]

def halo_txt(dr, x, y, s, f, fill, halo=WHITE, anchor="la"):
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        txt(dr, x + dx, y + dy, s, f, halo, anchor=anchor)
    txt(dr, x, y, s, f, fill, anchor=anchor)

def hero_frame(ax, ay, aw, ah, banner, stat):
    bw = tw(d, banner, sans_b(11)) + 18
    rr(d, ax + 6, ay + 6, ax + 6 + bw, ay + 25, 2, fill=RED + (255,))
    txt(d, ax + 15, ay + 10, banner, sans_b(11), WHITE, anchor="la")
    d.rectangle(B(ax, ay + ah - 18, ax + aw, ay + ah), fill=(8, 12, 22, 218))
    txt(d, ax + aw / 2, ay + ah - 14.5, stat, sans_b(9.5), WHITE, anchor="ma")

def bez(p0, p1, p2, n=14):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
        pts.append((x, y))
    return pts

def hero_kyiv(ax, ay, aw, ah):
    vgrad3(d, ax, ay, ax + aw, ay + ah, (226, 110, 55), (120, 70, 90), (24, 38, 80))
    grain(d, ax, ay, ax + aw, ay + ah, phase=3.1, alpha=12, step=5,
          base2=(52, 42, 74))
    # searchlight beams (collected; drawn at the end via true alpha compositing,
    # because ImageDraw on RGBA replaces pixels instead of blending)
    BEAMS.append(([(ax + 52, ay + ah), (ax + 92, ay + 6), (ax + 112, ay + 6),
                   (ax + 84, ay + ah)], 16))
    BEAMS.append(([(ax + 268, ay + ah), (ax + 228, ay + 6), (ax + 246, ay + 6),
                   (ax + 292, ay + ah)], 13))
    # missile trails: 5 dotted arcs
    for k in range(5):
        p0 = (ax + 296 - k * 16, ay + 96 - k * 2)
        p1 = (ax + 235 - k * 8, ay + 18 + k * 6)
        p2 = (ax + 150 + k * 22, ay + 10 + k * 9)
        for (px, py) in bez(p0, p1, p2, 13):
            ell(d, px - 1.6, py - 1.6, px + 1.6, py + 1.6,
                fill=(255, 200, 80, 235))
    # skyline with lit windows
    buildings = [(0, 26, 30), (32, 34, 24), (58, 22, 38), (98, 30, 26),
                 (126, 38, 30), (158, 24, 34), (194, 32, 26), (222, 26, 32),
                 (256, 36, 28), (286, 24, 30)]
    for bx, bh, bw2 in buildings:
        shade = (14 + (bx % 7), 22 + (bx % 5), 46 + (bx % 9))
        d.rectangle(B(ax + bx, ay + ah - 18 - bh, ax + bx + bw2, ay + ah - 18),
                    fill=shade)
        for wy in range(0, bh - 6, 9):
            for wx in range(4, bw2 - 4, 8):
                v = math.sin((bx + wx) * 12.9898 + (wy) * 78.233) * 43758.5453
                if v - math.floor(v) < 0.5:
                    d.rectangle(B(ax + bx + wx, ay + ah - 18 - bh + 4 + wy,
                                  ax + bx + wx + 2.4, ay + ah - 18 - bh + 6.4 + wy),
                                fill=(255, 214, 120, 235))
    # river with gold reflections
    vgrad(d, ax, ay + ah - 18, ax + aw, ay + ah, (18, 34, 68), (10, 22, 48))
    for rx in range(14, int(aw) - 10, 26):
        v = math.sin(rx * 3.7) * 43758.5453
        ln = 8 + (v - math.floor(v)) * 14
        line(d, [(ax + rx, ay + ah - 9), (ax + rx + ln, ay + ah - 9)],
             (255, 190, 90, 130), 1)
    # three bridges with cables + headlights
    for bx0, bx1, arc_h in [(8, 108, 14), (112, 208, 17), (212, 308, 13)]:
        arc(d, ax + bx0, ay + ah - 18 - arc_h, ax + bx1, ay + ah - 4,
            180, 360, fill=(228, 226, 214, 255), w=2)
        for cx in range(bx0 + 12, bx1 - 8, 14):
            line(d, [(ax + cx, ay + ah - 18 - arc_h + 6), (ax + cx, ay + ah - 18)],
                 (200, 198, 188, 200), 1)
        line(d, [(ax + bx0, ay + ah - 18), (ax + bx1, ay + ah - 18)],
             (235, 232, 222, 255), 2)
        for hx in (bx0 + 22, bx0 + 62):
            ell(d, ax + hx - 1.6, ay + ah - 21, ax + hx + 1.6, ay + ah - 18,
                fill=(255, 244, 190, 255))
    # fires + billowing smoke + embers
    for fx, fy in [(52, 82), (168, 78), (262, 84)]:
        ell(d, ax + fx - 11, ay + fy - 7, ax + fx + 11, ay + fy + 7,
            fill=(255, 120, 30, 90))
        ell(d, ax + fx - 6, ay + fy - 4, ax + fx + 6, ay + fy + 4,
            fill=(255, 165, 60, 140))
        ell(d, ax + fx - 3, ay + fy - 2, ax + fx + 3, ay + fy + 2,
            fill=(255, 220, 120, 255))
        puffs = [(-3, -9, 6, 4, (214, 128, 78)), (-7, -14, 9, 6, (96, 94, 92)),
                 (4, -20, 8, 6, (126, 124, 122)), (-2, -27, 7, 5, (156, 154, 152)),
                 (8, -28, 6, 5, (150, 138, 126)), (6, -33, 5, 4, (178, 176, 174))]
        for dx, dy, prx, pry, col in puffs:
            ell(d, ax + fx + dx - prx, ay + fy + dy - pry,
                ax + fx + dx + prx, ay + fy + dy + pry, fill=col + (215,))
        arc(d, ax + fx + 2, ay + fy - 42, ax + fx + 16, ay + fy - 26,
            200, 330, fill=(170, 168, 166, 160), w=1)
        for ex, ey in [(-4, -18), (3, -26), (-1, -34)]:
            ell(d, ax + fx + ex - 1.2, ay + fy + ey - 1.2,
                ax + fx + ex + 1.2, ay + fy + ey + 1.2, fill=(255, 150, 50, 240))
    # horizon glow above the skyline (true alpha, on the overlay)
    orect(ax, ay + 34, ax + aw, ay + 50, (255, 130, 50, 26))
    orect(ax, ay + 50, ax + aw, ay + 58, (255, 170, 90, 18))
    hero_frame(ax, ay, aw, ah, "KYIV", "9 killed \u00b7 3 bridges hit \u00b7 power cut")

def hero_akvan(ax, ay, aw, ah):
    vgrad3(d, ax, ay, ax + aw, ay + 72, (192, 221, 236), (168, 206, 222), (142, 191, 206))
    vgrad3(d, ax, ay + 72, ax + aw, ay + ah, (22, 112, 122), (16, 96, 110), (10, 80, 95))
    grain(d, ax, ay, ax + aw, ay + 72, phase=5.2, alpha=12, step=5,
          base2=(120, 150, 170))
    grain(d, ax, ay + 72, ax + aw, ay + ah, phase=6.8, alpha=12, step=5,
          base=(255, 255, 255), base2=(8, 60, 75))
    # clouds, shaded white -> light grey underneath
    for cx, cy, s in [(40, 16, 1.0), (150, 10, 0.8), (255, 18, 0.9)]:
        ell(d, ax + cx - 18 * s, ay + cy - 6 * s, ax + cx + 18 * s, ay + cy + 6 * s,
            fill=(255, 255, 255, 225))
        ell(d, ax + cx - 8 * s, ay + cy - 10 * s, ax + cx + 10 * s, ay + cy + 4 * s,
            fill=(255, 255, 255, 235))
        ell(d, ax + cx - 15 * s, ay + cy + 1 * s, ax + cx + 15 * s, ay + cy + 7 * s,
            fill=(224, 229, 234, 230))
    # rain, two rows
    for rx in range(12, int(aw) - 8, 14):
        line(d, [(ax + rx, ay + 30), (ax + rx - 4, ay + 46)],
             (110, 145, 168, 150), 1)
        line(d, [(ax + rx + 6, ay + 52), (ax + rx + 2, ay + 66)],
             (110, 145, 168, 120), 1)
    # sand coast
    vgrad(d, ax, ay + 62, ax + aw, ay + 78, (234, 216, 172), (214, 190, 140))
    # palms
    for px, lean in [(28, -6), (66, 5), (252, -5), (288, 6)]:
        line(d, [(ax + px, ay + 74), (ax + px + lean, ay + 44)], (110, 82, 50), 2)
        for fi, ang in enumerate((-70, -35, 0, 35, 70)):
            fcol = (46, 110, 70, 255) if fi % 2 == 0 else (28, 86, 52, 255)
            a = math.radians(ang - 90)
            ex = ax + px + lean + 13 * math.cos(a)
            ey = ay + 44 + 13 * math.sin(a) * 0.55
            arc(d, ex - 7, ey - 4, ex + 7, ey + 4, 180 + ang, 180 + ang + 60,
                fill=fcol, w=2)
    # bus + small red-roof house
    rr(d, ax + 118, ay + 64, ax + 152, ay + 77, 2, fill=(240, 190, 40, 255))
    rr(d, ax + 118, ay + 64, ax + 152, ay + 70, 2, fill=(250, 210, 80, 255))
    for wx in range(122, 150, 8):
        d.rectangle(B(ax + wx, ay + 66, ax + wx + 5, ay + 70), fill=(30, 50, 80))
    ell(d, ax + 124, ay + 75, ax + 130, ay + 81, fill=(30, 30, 30, 255))
    ell(d, ax + 140, ay + 75, ax + 146, ay + 81, fill=(30, 30, 30, 255))
    d.rectangle(B(ax + 162, ay + 66, ax + 182, ay + 78), fill=(250, 240, 214, 255))
    poly(d, [(ax + 159, ay + 66), (ax + 185, ay + 66), (ax + 172, ay + 57)],
         fill=(178, 52, 40, 255))
    d.rectangle(B(ax + 169, ay + 71, ax + 175, ay + 77), fill=(255, 214, 110, 255))
    # sea waves, two highlight layers
    for wy in (84, 94, 104):
        for wx in range(8, int(aw) - 8, 30):
            arc(d, ax + wx, ay + wy - 3, ax + wx + 18, ay + wy + 3, 180, 360,
                fill=(255, 255, 255, 190), w=1)
    for wy in (89, 99):
        for wx in range(20, int(aw) - 8, 30):
            arc(d, ax + wx, ay + wy - 2, ax + wx + 14, ay + wy + 2, 180, 360,
                fill=(200, 235, 240, 170), w=1)
    # closed spiral
    cx, cy = ax + 205, ay + 46
    for r, wd in [(34, 3), (26, 3), (18, 3), (10, 3)]:
        ell(d, cx - r, cy - r, cx + r, cy + r, outline=(255, 255, 255, 235),
            width=S(wd))
    arc(d, cx - 40, cy - 40, cx + 40, cy + 40, 250, 120,
        fill=(255, 255, 255, 200), w=2)
    ell(d, cx - 4, cy - 4, cx + 4, cy + 4, fill=(200, 40, 32, 255))
    ell(d, cx - 6.5, cy - 6.5, cx + 6.5, cy + 6.5, outline=(255, 255, 255, 255),
        width=S(1))
    # landfall dot + label
    ell(d, ax + 148, ay + 62, ax + 156, ay + 70, fill=(200, 40, 32, 255))
    ell(d, ax + 146, ay + 60, ax + 158, ay + 72, outline=(255, 255, 255, 255),
        width=S(1))
    halo_txt(d, ax + 160, ay + 58, "Gopalpur", sans_b(8), (30, 40, 50), anchor="la")
    hero_frame(ax, ay, aw, ah, "CYCLONE AKVAN",
               "300,000+ evacuated \u00b7 209mm rain")

def hero_ai(ax, ay, aw, ah):
    vgrad3(d, ax, ay, ax + aw, ay + ah, (20, 30, 58), (16, 24, 46), (10, 16, 32))
    grain(d, ax, ay, ax + aw, ay + ah, phase=7.4, alpha=12, step=5,
          base2=(150, 60, 60))
    # soft radial glow behind the trend (true alpha, on the overlay)
    oell(ax + 130, ay + 6, ax + 300, ay + 82, (255, 70, 50, 20))
    for gy in range(16, int(ah) - 20, 16):
        line(d, [(ax + 6, ay + gy), (ax + aw - 6, ay + gy)], (255, 255, 255, 22), 1)
    for gx in range(40, int(aw) - 10, 40):
        line(d, [(ax + gx, ay + 6), (ax + gx, ay + ah - 22)], (255, 255, 255, 16), 1)
    tops = [26, 32, 38, 44, 50, 56, 62, 68]
    hs = [14, 12, 16, 10, 14, 9, 12, 8]
    pts = []
    for i, (tp, hh) in enumerate(zip(tops, hs)):
        cx = ax + 24 + i * 34
        vgrad(d, cx - 6, ay + tp, cx + 6, ay + tp + hh, (205, 42, 42), (150, 20, 20))
        line(d, [(cx, ay + tp - 5), (cx, ay + tp)], (225, 85, 85, 255), 1)
        line(d, [(cx, ay + tp + hh), (cx, ay + tp + hh + 4)], (225, 85, 85, 255), 1)
        pts.append((cx, ay + tp - 6))
        if i < 7:
            vgrad(d, cx - 5, ay + tp + hh + 3, cx + 5, ay + tp + hh + 8,
                  (190, 60, 60), (140, 30, 30))
    line(d, pts, (255, 92, 92, 255), 2)
    for (px, py) in pts:
        ell(d, px - 2.6, py - 2.6, px + 2.6, py + 2.6, fill=(255, 255, 255, 255))
        ell(d, px - 4.2, py - 4.2, px + 4.2, py + 4.2,
            outline=(255, 92, 92, 255), width=S(1))
    # down arrow near last dot
    lx, ly = pts[-1]
    poly(d, [(lx + 8, ly + 2), (lx + 16, ly + 2), (lx + 12, ly + 10)],
         fill=(255, 92, 92, 255))
    line(d, [(lx + 12, ly - 6), (lx + 12, ly + 2)], (255, 92, 92, 255), 2)
    # ticker labels (clear of line/dots/candles)
    txt(d, ax + aw - 8, ay + 6, "NIKKEI \u22124.9%", sans_b(9.5), (255, 140, 130),
        anchor="ra")
    txt(d, ax + aw - 8, ay + 20, "HANG SENG \u22122%", sans_b(9.5),
        (255, 140, 130), anchor="ra")
    txt(d, ax + 8, ay + 83, "TAIEX \u22126.2%", sans_b(9.5), (255, 140, 130),
        anchor="la")
    txt(d, ax + 118, ay + 83, "KOSPI \u22125.2%", sans_b(9.5), (255, 140, 130),
        anchor="la")
    txt(d, ax + 235, ay + 83, "NVDA \u221214%", sans_b(9.5), (255, 140, 130),
        anchor="la")
    hero_frame(ax, ay, aw, ah, "AI SELL-OFF",
               "Taiex \u22126.2% \u00b7 Kospi \u22125.2% \u00b7 Nvidia \u221214%")

def hero_text(x, loc, head_lines, body_lines, source):
    txt(d, x, 346, loc, sans_b(9.5), RED_D, anchor="la")
    y = 360
    for ln in head_lines:
        txt(d, x, y, ln, sans_b(15), INK, anchor="la")
        y += 16
    y = 394
    for ln in body_lines:
        txt(d, x, y, ln, sans(10), BODY, anchor="la")
        y += 11
    txt(d, x, 418, source, sans_i(8.5), GREY, anchor="la")

hero_kyiv(HERO_X[0], HERO_Y0, HERO_W, HERO_ART_H)
hero_akvan(HERO_X[1], HERO_Y0, HERO_W, HERO_ART_H)
hero_ai(HERO_X[2], HERO_Y0, HERO_W, HERO_ART_H)

hero_text(HERO_X[0], "KYIV, UKRAINE \u00b7 WAR",
          ["Russian missiles hit three Kyiv", "bridges overnight"],
          ["~110 missiles and 400 drones; 9 killed", "across Ukraine, 3 in Kyiv; power and water cut."],
          "Kyiv Independent, BBC")
hero_text(HERO_X[1], "ODISHA, INDIA \u00b7 CYCLONE",
          ["Cyclone Akvan slams Odisha", "coast at dawn"],
          ["Landfall near Gopalpur ~8am; 300,000+ evacuated;",
           "209mm rain in Ganjam; gusts 90 km/h; no deaths."],
          "IMD, Deccan Herald")
hero_text(HERO_X[2], "ASIAN MARKETS \u00b7 STOCKS",
          ["AI sell-off sinks Asia's markets"],
          ["Taiwan \u22126.2%, worst week since 1991; Seoul \u22125.2%,",
           "Tokyo \u22125.1%; Hong Kong \u22121.9%; Nvidia \u221214%."],
          "Al Jazeera, Anadolu")

# ---------------------------------------------------------------- small cards
CARD_H = 124
BAND_H = 56

def card(x, y0, w, num, loc, code, head_lines, tag, scene):
    vgrad3(d, x, y0, x + w, y0 + CARD_H, (255, 253, 246), (250, 246, 234),
           (244, 238, 222))
    rr(d, x, y0, x + w, y0 + CARD_H, 3, outline=(205, 192, 168), width=1)
    scene(x + 1, y0 + 1, w - 2, BAND_H)
    ell(d, x + 3, y0 + 3, x + 25, y0 + 25, fill=WHITE + (255,),
        outline=(40, 40, 40, 255), width=S(1))
    txt(d, x + 14, y0 + 8.5, str(num), sans_b(11), INK, anchor="ma")
    cw2 = tw(d, code, sans_b(8)) + 10
    rr(d, x + w - 5 - cw2, y0 + 4, x + w - 5, y0 + 18, 2, fill=(30, 30, 30, 230))
    txt(d, x + w - 5 - cw2 / 2, y0 + 7, code, sans_b(8), WHITE, anchor="ma")
    txt(d, x + 6, y0 + 61, loc, sans_b(9.5), RED_D, anchor="la")
    yy = y0 + 73
    for ln in head_lines:
        txt(d, x + 6, yy, ln, sans_b(12.5), INK, anchor="la")
        yy += 14
    txt(d, x + 6, y0 + 106, tag, sans(9), GREY, anchor="la")

def sc_brussels(bx, by, bw, bh):
    vgrad3(d, bx, by, bx + bw, by + bh, (36, 68, 150), (28, 56, 128), (22, 44, 104))
    grain(d, bx, by, bx + bw, by + bh, phase=9.1, alpha=12, step=5,
          base2=(10, 26, 70))
    # EU flag (left), with a darker fold stripe at its right edge
    d.rectangle(B(bx + 8, by + 12, bx + 38, by + 32), fill=(0, 51, 153, 255))
    d.rectangle(B(bx + 34, by + 12, bx + 38, by + 32), fill=(0, 40, 120, 255))
    for k in range(8):
        a = math.radians(k * 45)
        ell(d, bx + 23 + 8 * math.cos(a) - 1, by + 22 + 6 * math.sin(a) - 1,
            bx + 23 + 8 * math.cos(a) + 1, by + 22 + 6 * math.sin(a) + 1,
            fill=(255, 204, 0, 255))
    # UK flag (right), with a diagonal fold line
    d.rectangle(B(bx + bw - 38, by + 12, bx + bw - 8, by + 32),
                fill=(1, 33, 105, 255))
    d.rectangle(B(bx + bw - 27, by + 12, bx + bw - 19, by + 32),
                fill=(255, 255, 255, 255))
    d.rectangle(B(bx + bw - 38, by + 20, bx + bw - 8, by + 24),
                fill=(255, 255, 255, 255))
    d.rectangle(B(bx + bw - 24, by + 12, bx + bw - 22, by + 32),
                fill=(200, 16, 46, 255))
    d.rectangle(B(bx + bw - 38, by + 21, bx + bw - 8, by + 23),
                fill=(200, 16, 46, 255))
    line(d, [(bx + bw - 38, by + 32), (bx + bw - 8, by + 12)],
         (150, 10, 35, 255), 1)
    # gold starburst behind the clasp (bigger, 7 stars)
    cx, cy = bx + bw / 2, by + 30
    for k in range(7):
        a = math.radians(195 + k * 30)
        sx, sy = cx + 34 * math.cos(a), cy + 22 * math.sin(a)
        ell(d, sx - 3.2, sy - 3.2, sx + 3.2, sy + 3.2, fill=(212, 160, 23, 255))
    # forearms + clasped hands, ~1.5x bigger than before
    poly(d, [(bx + 44, by + 52), (cx - 18, by + 26), (cx - 12, by + 40),
             (bx + 50, by + 56)], fill=(0, 51, 153, 255))
    poly(d, [(bx + bw - 44, by + 52), (cx + 18, by + 26), (cx + 12, by + 40),
             (bx + bw - 50, by + 56)], fill=(200, 16, 46, 255))
    # sleeve cuffs: gold edge on the EU sleeve, white edge on the UK sleeve
    line(d, [(cx - 18, by + 26), (cx - 12, by + 40)], (212, 160, 23, 255), 2)
    line(d, [(cx + 18, by + 26), (cx + 12, by + 40)], (255, 255, 255, 255), 2)
    ell(d, cx - 16, by + 20, cx + 16, by + 40, fill=(232, 190, 150, 255))
    ell(d, cx - 16, by + 20, cx + 2, by + 30, fill=(245, 210, 175, 255))
    for fx in (-8, -3, 3, 8):
        line(d, [(cx + fx, by + 26), (cx + fx, by + 38)], (160, 110, 80, 255), 1)
    # parliament silhouette at bottom (shifted down so the hands clear it)
    d.rectangle(B(bx + 62, by + 48, bx + bw - 62, by + bh), fill=(10, 22, 46, 255))
    ell(d, cx - 7, by + 40, cx + 7, by + 50, fill=(10, 22, 46, 255))
    arc(d, cx - 7, by + 40, cx + 7, by + 50, 180, 360,
        fill=(212, 160, 23, 255), w=1)
    for wx in range(66, int(bw) - 64, 10):
        d.rectangle(B(bx + wx, by + 52, bx + wx + 3, by + 55),
                    fill=(255, 214, 110, 255))

def sc_poland(bx, by, bw, bh):
    vgrad3(d, bx, by, bx + bw, by + bh, (205, 228, 238), (186, 218, 213), (168, 208, 188))
    vgrad3(d, bx, by + 34, bx + bw, by + bh, (96, 158, 92), (84, 144, 82), (70, 128, 70))
    for tx in range(6, int(bw) - 6, 16):
        poly(d, [(bx + tx, by + 30), (bx + tx + 6, by + 18), (bx + tx + 12, by + 30)],
             fill=(34, 96, 58, 255))
    for fx in range(10, int(bw) - 6, 22):
        line(d, [(bx + fx, by + 32), (bx + fx, by + 40)], (120, 96, 60, 255), 1)
    # missile lying diagonally
    mx, my = bx + bw / 2 - 34, by + 22
    ell(d, mx - 6, my + 8, mx + 74, my + 22, fill=(0, 0, 0, 60))
    poly(d, [(mx, my + 6), (mx + 56, my), (mx + 68, my + 4), (mx + 56, my + 9),
             (mx, my + 12)], fill=(238, 238, 234, 255))
    poly(d, [(mx, my + 6), (mx + 56, my), (mx + 56, my + 9), (mx, my + 12)],
         fill=(210, 210, 204, 255))
    poly(d, [(mx + 56, my), (mx + 68, my + 4), (mx + 56, my + 9)],
         fill=(178, 40, 36, 255))
    poly(d, [(mx + 8, my + 12), (mx + 16, my + 19), (mx + 20, my + 12)],
         fill=(120, 40, 36, 255))
    for gx in (20, 60, 110, 150):
        line(d, [(bx + gx, by + 48), (bx + gx + 2, by + 42)], (52, 110, 58, 255), 1)
        line(d, [(bx + gx + 4, by + 48), (bx + gx + 2, by + 42)], (52, 110, 58, 255), 1)

def sc_cop31(bx, by, bw, bh):
    vgrad3(d, bx, by, bx + bw, by + bh, (150, 200, 225), (122, 176, 208), (92, 152, 192))
    ell(d, bx + bw - 22, by + 6, bx + bw - 8, by + 20, fill=(255, 214, 110, 255))
    for k in range(8):
        a = math.radians(k * 45)
        line(d, [(bx + bw - 15 + 9 * math.cos(a), by + 13 + 9 * math.sin(a)),
                 (bx + bw - 15 + 13 * math.cos(a), by + 13 + 13 * math.sin(a))],
             (255, 200, 80, 220), 1)
    # globe
    ell(d, bx + 12, by + 8, bx + 44, by + 40, fill=(38, 110, 190, 255))
    poly(d, [(bx + 18, by + 16), (bx + 28, by + 12), (bx + 34, by + 20),
             (bx + 26, by + 26), (bx + 18, by + 24)], fill=(80, 160, 90, 255))
    poly(d, [(bx + 28, by + 30), (bx + 38, by + 30), (bx + 36, by + 38),
             (bx + 28, by + 36)], fill=(80, 160, 90, 255))
    arc(d, bx + 14, by + 10, bx + 34, by + 30, 200, 320,
        fill=(255, 255, 255, 160), w=1)
    # thermometer
    d.rectangle(B(bx + bw - 52, by + 12, bx + bw - 44, by + 36),
                fill=(240, 240, 236, 255))
    ell(d, bx + bw - 54, by + 34, bx + bw - 42, by + 46, fill=(200, 40, 36, 255))
    d.rectangle(B(bx + bw - 50, by + 22, bx + bw - 46, by + 36),
                fill=(200, 40, 36, 255))
    # flags + waves
    for i, col in enumerate([(0, 120, 90), (200, 40, 36), (220, 170, 30)]):
        fx = bx + 58 + i * 16
        line(d, [(fx, by + 14), (fx, by + 30)], (60, 60, 60, 255), 1)
        poly(d, [(fx, by + 14), (fx + 11, by + 17), (fx, by + 20)], fill=col + (255,))
    for wy in (46, 51):
        for wx in range(8, int(bw) - 8, 26):
            arc(d, bx + wx, by + wy - 3, bx + wx + 16, by + wy + 3, 180, 360,
                fill=(255, 255, 255, 180), w=1)

def sc_space(bx, by, bw, bh):
    vgrad3(d, bx, by, bx + bw, by + bh, (10, 16, 34), (20, 28, 58), (30, 42, 82))
    grain(d, bx, by, bx + bw, by + bh, phase=15.1, alpha=12, step=5,
          base2=(60, 80, 130))
    for sx in range(8, int(bw) - 4, 13):
        for sy in range(6, int(bh) - 6, 11):
            v = math.sin(sx * 12.9898 + sy * 78.233 + 4.4) * 43758.5453
            if v - math.floor(v) < 0.4:
                ell(d, bx + sx - 1, by + sy - 1, bx + sx + 1, by + sy + 1,
                    fill=(255, 255, 255, 220))
    # moon with craters + shading
    ell(d, bx + 12, by + 10, bx + 44, by + 42, fill=(168, 168, 160, 255))
    ell(d, bx + 14, by + 12, bx + 32, by + 26, fill=(190, 190, 182, 255))
    for cx, cy, cr, ccol in [(26, 32, 4, (140, 140, 132)), (34, 18, 3, (116, 116, 110)),
                             (20, 24, 2.5, (140, 140, 132)), (30, 26, 2, (116, 116, 110))]:
        ell(d, bx + cx - cr, by + cy - cr, bx + cx + cr, by + cy + cr,
            fill=ccol + (255,))
    # spacecraft with gold panels
    d.rectangle(B(bx + 62, by + 18, bx + 76, by + 26), fill=(220, 220, 214, 255))
    d.rectangle(B(bx + 78, by + 20, bx + 84, by + 24), fill=(200, 160, 40, 255))
    poly(d, [(bx + 56, by + 16), (bx + 62, by + 18), (bx + 62, by + 26),
             (bx + 56, by + 28)], fill=(212, 160, 23, 255))
    poly(d, [(bx + 84, by + 16), (bx + 90, by + 18), (bx + 90, by + 26),
             (bx + 84, by + 28)], fill=(212, 160, 23, 255))
    # ringed planet far right
    ell(d, bx + bw - 30, by + 30, bx + bw - 16, by + 44, fill=(200, 140, 90, 255))
    arc(d, bx + bw - 36, by + 30, bx + bw - 10, by + 44, 160, 340,
        fill=(230, 200, 150, 255), w=1)

def sc_italy(bx, by, bw, bh):
    vgrad3(d, bx, by, bx + bw, by + bh, (240, 230, 210), (224, 214, 194), (206, 196, 176))
    for bx2, bh2 in [(6, 22), (34, 28), (66, 20)]:
        if bx2 + 24 < bw:
            d.rectangle(B(bx + bx2, by + bh - 18 - bh2, bx + bx2 + 24, by + bh - 18),
                        fill=(150, 144, 132, 255))
            for wy in range(4, bh2 - 4, 8):
                d.rectangle(B(bx + bx2 + 4, by + bh - 18 - bh2 + wy,
                              bx + bx2 + 8, by + bh - 18 - bh2 + wy + 4),
                            fill=(255, 220, 130, 220))
    rr(d, bx + bw / 2 - 32, by + 4, bx + bw / 2 + 32, by + 17, 2,
       fill=(178, 32, 32, 255))
    txt(d, bx + bw / 2, by + 6.5, "SCIOPERO", sans_b(8), WHITE, anchor="ma")
    # protesters
    for i, px in enumerate([18, 52, 86, 120]):
        if px + 16 > bw:
            continue
        ell(d, bx + px - 4, by + 26, bx + px + 4, by + 34, fill=(30, 28, 26, 255))
        poly(d, [(bx + px - 6, by + 52), (bx + px - 4, by + 34),
                 (bx + px + 4, by + 34), (bx + px + 6, by + 52)],
             fill=(30, 28, 26, 255))
        line(d, [(bx + px + 3, by + 38), (bx + px + 10, by + 30)],
             (30, 28, 26, 255), 1)
        if i in (1, 3):
            d.rectangle(B(bx + px + 8, by + 20, bx + px + 26, by + 32),
                        fill=(250, 248, 240, 255))
            line(d, [(bx + px + 8, by + 20), (bx + px + 26, by + 20)],
                 (178, 32, 32, 255), 1)

def sc_kenya(bx, by, bw, bh):
    vgrad3(d, bx, by, bx + bw, by + bh, (250, 222, 142), (242, 198, 112), (232, 172, 82))
    grain(d, bx, by, bx + bw, by + bh, phase=16.2, alpha=12, step=5,
          base=(255, 240, 200), base2=(200, 140, 60))
    ell(d, bx + bw - 26, by + 6, bx + bw - 10, by + 22, fill=(255, 150, 40, 255))
    ell(d, bx + bw - 22, by + 10, bx + bw - 14, by + 18, fill=(255, 200, 90, 255))
    for k in range(8):
        a = math.radians(k * 45)
        line(d, [(bx + bw - 18 + 10 * math.cos(a), by + 14 + 10 * math.sin(a)),
                 (bx + bw - 18 + 14 * math.cos(a), by + 14 + 14 * math.sin(a))],
             (255, 170, 60, 220), 1)
    for bx2 in (20, 110):
        arc(d, bx + bx2 - 4, by + 8, bx + bx2 + 4, by + 14, 180, 360,
            fill=(60, 60, 60, 255), w=1)
    # hills + acacia
    poly(d, [(bx, by + 44), (bx + 40, by + 36), (bx + 90, by + 44),
             (bx + bw, by + 38), (bx + bw, by + bh), (bx, by + bh)],
         fill=(190, 140, 70, 255))
    line(d, [(bx + bw - 44, by + 40), (bx + bw - 40, by + 26)], (90, 66, 40, 255), 2)
    ell(d, bx + bw - 58, by + 20, bx + bw - 22, by + 28, fill=(70, 120, 60, 255))
    # oil derrick
    dx = bx + 22
    poly(d, [(dx, by + 52), (dx + 8, by + 14), (dx + 16, by + 52)],
         fill=(40, 32, 26, 255))
    poly(d, [(dx + 3, by + 52), (dx + 8, by + 30), (dx + 13, by + 52)],
         fill=(120, 90, 60, 255))
    line(d, [(dx + 2, by + 44), (dx + 14, by + 44)], (200, 170, 120, 255), 1)
    line(d, [(dx + 4, by + 34), (dx + 12, by + 34)], (200, 170, 120, 255), 1)
    ell(d, dx - 2, by + 50, dx + 18, by + 55, fill=(0, 0, 0, 70))
    for gx in (60, 130):
        line(d, [(bx + gx, by + 50), (bx + gx + 2, by + 44)], (90, 120, 60, 255), 1)
        line(d, [(bx + gx + 4, by + 50), (bx + gx + 2, by + 44)], (90, 120, 60, 255), 1)

def sc_salvador(bx, by, bw, bh):
    vgrad3(d, bx, by, bx + bw, by + bh, (200, 220, 240), (180, 205, 230), (160, 190, 220))
    grain(d, bx, by, bx + bw, by + bh, phase=11.3, alpha=12, step=5,
          base2=(120, 150, 190))
    # falling papers + confetti
    for px, py, col in [(14, 10, (250, 248, 240)), (30, 20, (255, 220, 110)),
                        (bw - 30, 12, (250, 248, 240)), (bw - 16, 26, (255, 150, 140))]:
        poly(d, [(bx + px, by + py), (bx + px + 8, by + py + 2),
                 (bx + px + 6, by + py + 10), (bx + px - 2, by + py + 8)],
             fill=col + (255,))
    for cx2, cy2, col in [(50, 8, (200, 40, 36)), (bw - 50, 40, (40, 120, 200))]:
        ell(d, bx + cx2 - 1.6, by + cy2 - 1.6, bx + cx2 + 1.6, by + cy2 + 1.6,
            fill=col + (255,))
    # ballot box
    cx = bx + bw / 2
    ell(d, cx - 26, by + 46, cx + 26, by + 52, fill=(0, 0, 0, 70))
    vgrad3(d, cx - 22, by + 22, cx + 22, by + 48, (52, 96, 168), (42, 82, 150),
           (30, 66, 128))
    d.rectangle(B(cx - 22, by + 22, cx + 22, by + 28), fill=(70, 120, 190, 255))
    d.rectangle(B(cx - 6, by + 18, cx + 6, by + 23), fill=(20, 46, 96, 255))
    # ballot paper + green tick
    poly(d, [(cx - 12, by + 20), (cx - 2, by + 8), (cx + 6, by + 10),
             (cx - 2, by + 22)], fill=(250, 248, 240, 255))
    line(d, [(cx - 10, by + 14), (cx - 5, by + 19), (cx + 3, by + 9)],
         (40, 160, 70, 255), 2)
    # small flag on box
    line(d, [(cx + 14, by + 8), (cx + 14, by + 20)], (60, 60, 60, 255), 1)
    poly(d, [(cx + 14, by + 8), (cx + 26, by + 11), (cx + 14, by + 14)],
         fill=(0, 80, 160, 255))

def sc_cricket(bx, by, bw, bh):
    vgrad3(d, bx, by, bx + bw, by + bh, (140, 190, 110), (116, 172, 96), (92, 152, 82))
    for cx2 in range(10, int(bw) - 6, 12):
        for cy2 in (8, 14):
            v = math.sin(cx2 * 3.1 + cy2 * 7.7) * 43758.5453
            col = (200, 60, 60) if (v - math.floor(v)) < 0.33 else (
                (60, 90, 200) if (v - math.floor(v)) < 0.66 else (240, 220, 120))
            ell(d, bx + cx2 - 1.6, by + cy2 - 1.6, bx + cx2 + 1.6, by + cy2 + 1.6,
                fill=col + (230,))
    # pitch + boundary rope
    vgrad3(d, bx + 8, by + 24, bx + bw - 8, by + 46, (222, 198, 150), (212, 188, 140),
           (200, 176, 128))
    for rx in range(10, int(bw) - 8, 12):
        line(d, [(bx + rx, by + 50), (bx + rx + 6, by + 50)], (250, 248, 240, 220), 1)
    # bat (angled polygon) + stumps + ball
    poly(d, [(bx + 26, by + 44), (bx + 34, by + 20), (bx + 40, by + 22),
             (bx + 34, by + 46)], fill=(214, 178, 120, 255))
    poly(d, [(bx + 34, by + 20), (bx + 36, by + 12), (bx + 40, by + 13),
             (bx + 38, by + 22)], fill=(120, 84, 50, 255))
    for sx in range(0, 3):
        d.rectangle(B(bx + bw - 34 + sx * 5, by + 26, bx + bw - 31 + sx * 5, by + 42),
                    fill=(240, 214, 110, 255))
    d.rectangle(B(bx + bw - 35, by + 24, bx + bw - 20, by + 26),
                fill=(240, 214, 110, 255))
    ell(d, bx + 66, by + 38, bx + 76, by + 48, fill=(178, 32, 32, 255))
    ell(d, bx + 68, by + 39, bx + 73, by + 44, fill=(230, 90, 80, 255))
    arc(d, bx + 66, by + 38, bx + 76, by + 48, 200, 340,
        fill=(255, 255, 255, 200), w=1)
    ell(d, bx + bw - 52, by + 44, bx + bw - 46, by + 50, fill=(178, 32, 32, 255))

def sc_health(bx, by, bw, bh):
    vgrad3(d, bx, by, bx + bw, by + bh, (245, 235, 225), (234, 219, 206), (222, 202, 186))
    cx, cy = bx + bw / 2, by + 28
    ell(d, cx - 34, by + 42, cx + 34, by + 50, fill=(0, 0, 0, 60))
    # capsule: red half + white half, highlight stripe
    ell(d, cx - 32, cy - 9, cx + 2, cy + 9, fill=(198, 40, 40, 255))
    ell(d, cx - 2, cy - 9, cx + 32, cy + 9, fill=(248, 248, 244, 255))
    ell(d, cx - 32, cy - 9, cx + 2, cy + 9, outline=(140, 20, 20, 255), width=S(1))
    ell(d, cx - 2, cy - 9, cx + 32, cy + 9, outline=(180, 175, 168, 255), width=S(1))
    ell(d, cx - 26, cy - 6, cx - 2, cy - 1, fill=(240, 110, 100, 255))
    ell(d, cx + 6, cy - 6, cx + 26, cy - 1, fill=(255, 255, 255, 255))
    # blister pack + small pills
    rr(d, bx + bw - 46, by + 34, bx + bw - 10, by + 50, 2, fill=(190, 186, 176, 255))
    for i in range(4):
        ell(d, bx + bw - 42 + i * 9, by + 38, bx + bw - 36 + i * 9, by + 46,
            fill=(255, 255, 255, 255))
    ell(d, bx + 12, by + 40, bx + 20, by + 48, fill=(200, 60, 60, 255))
    ell(d, bx + 24, by + 42, bx + 30, by + 48, fill=(240, 240, 236, 255))

def sc_california(bx, by, bw, bh):
    vgrad3(d, bx, by, bx + bw, by + bh, (230, 235, 240), (210, 218, 226), (190, 200, 210))
    # circuit traces across the band
    for ty in (12, 28, 44):
        line(d, [(bx + 4, by + ty), (bx + bw - 4, by + ty)],
             (150, 160, 60, 200), 1)
    for tx in (30, 70, 110):
        if tx < bw - 6:
            line(d, [(bx + tx, by + 8), (bx + tx, by + 48)], (150, 160, 60, 180), 1)
    for nx, ny in [(30, 12), (70, 28), (110, 44), (50, 44), (90, 12)]:
        if nx < bw - 4:
            ell(d, bx + nx - 2, by + ny - 2, bx + nx + 2, by + ny + 2,
                fill=(180, 150, 40, 255))
    # green chip with pins
    cx = bx + 34
    d.rectangle(B(cx - 14, by + 16, cx + 14, by + 40), fill=(16, 90, 60, 255))
    d.rectangle(B(cx - 9, by + 21, cx + 9, by + 35), fill=(40, 140, 95, 255))
    d.rectangle(B(cx - 9, by + 21, cx + 9, by + 27), fill=(70, 180, 125, 255))
    for px in range(-12, 13, 6):
        line(d, [(cx + px, by + 14), (cx + px, by + 16)], (200, 200, 190, 255), 1)
        line(d, [(cx + px, by + 40), (cx + px, by + 42)], (200, 200, 190, 255), 1)
    # magnifier
    mx, my = bx + bw - 30, by + 28
    ell(d, mx - 13, my - 13, mx + 13, my + 13, outline=(212, 160, 23, 255),
        width=S(3))
    ell(d, mx - 10, my - 10, mx + 10, my + 10, fill=(180, 220, 240, 110))
    ell(d, mx - 8, my - 8, mx - 1, my - 1, fill=(255, 255, 255, 130))
    line(d, [(mx + 9, my + 9), (mx + 18, my + 18)], (140, 100, 30, 255), 3)

def sc_games(bx, by, bw, bh):
    vgrad3(d, bx, by, bx + bw, by + bh, (92, 52, 142), (76, 41, 121), (60, 30, 100))
    grain(d, bx, by, bx + bw, by + bh, phase=17.3, alpha=12, step=5,
          base2=(30, 16, 60))
    for sx, sy in [(12, 8), (bw - 14, 10), (24, 46), (bw - 30, 44)]:
        poly(d, [(bx + sx, by + sy - 4), (bx + sx + 1.4, by + sy - 1),
                 (bx + sx + 4, by + sy), (bx + sx + 1.4, by + sy + 1.4),
                 (bx + sx, by + sy + 4), (bx + sx - 1.4, by + sy + 1.4),
                 (bx + sx - 4, by + sy), (bx + sx - 1.4, by + sy - 1)],
             fill=(255, 214, 110, 255))
    for cx2, cy2 in [(16, 30), (bw - 18, 32)]:
        ell(d, bx + cx2 - 6, by + cy2 - 6, bx + cx2 + 6, by + cy2 + 6,
            fill=(240, 190, 60, 255))
        ell(d, bx + cx2 - 4, by + cy2 - 4, bx + cx2 + 4, by + cy2 + 4,
            fill=(255, 220, 110, 255))
        txt(d, bx + cx2, by + cy2 - 5, "$", sans_b(8), (150, 100, 20),
            anchor="ma")
    # controller
    cx, cy = bx + bw / 2, by + 28
    ell(d, cx - 30, by + 40, cx + 30, by + 48, fill=(0, 0, 0, 70))
    rr(d, cx - 28, cy - 10, cx + 28, cy + 12, 8, fill=(32, 32, 40, 255))
    rr(d, cx - 28, cy - 10, cx + 28, cy - 2, 8, fill=(58, 58, 72, 255))
    for bx2, by2, col in [(-18, -3, (220, 220, 220)), (-12, -3, (220, 220, 220)),
                          (14, -4, (90, 200, 90)), (20, 2, (220, 80, 80)),
                          (14, 8, (90, 140, 230)), (8, 2, (240, 200, 60))]:
        ell(d, cx + bx2 - 2.6, cy + by2 - 2.6, cx + bx2 + 2.6, cy + by2 + 2.6,
            fill=col + (255,))
    ell(d, cx - 22, cy + 2, cx - 16, cy + 8, fill=(20, 20, 26, 255))
    ell(d, cx + 16, cy + 2, cx + 22, cy + 8, fill=(20, 20, 26, 255))

ROW1 = [
    (4, "BRUSSELS", "EU", ["UK and EU seal a 'reset'", "deal in Brussels"],
     "EUROPE", sc_brussels),
    (5, "POLAND", "EU", ["Russian cruise missile", "lands in a Polish field"],
     "EUROPE", sc_poland),
    (6, "ANTALYA", "GL", ["COP31 ends its last day", "with no deal"],
     "GLOBAL", sc_cop31),
    (7, "SPACE", "SP", ["BepiColombo reaches", "Mercury after 8 years"],
     "GLOBAL", sc_space),
    (8, "ROME", "EU", ["Italy hit by general strike", "over budget"],
     "EUROPE", sc_italy),
]
ROW2 = [
    (9, "TURKANA", "AF", ["Kenya drills its first oil", "in Turkana"],
     "AFRICA", sc_kenya),
    (10, "SAN SALVADOR", "AM", ["Bukele files to run for a", "third term"],
     "AMERICAS", sc_salvador),
    (11, "CRICKET", "OC", ["Phillips hits 118 as NZ", "make 368"],
     "OCEANIA", sc_cricket),
    (12, "HEALTH", "GL", ["Cancer pill shrinks", "tumours in trial"],
     "GLOBAL", sc_health),
    (13, "CALIFORNIA", "AM", ["California probes Nvidia", "over chips"],
     "AMERICAS", sc_california),
    (14, "GAMES", "GL", ["GTA VI sales top $2.36bn", "at launch"],
     "GLOBAL", sc_games),
]

def draw_row(y0, items):
    n = len(items)
    w = (CW - (n - 1) * 8) / n
    x = M
    for (num, loc, code, hl, tag, scene) in items:
        card(x, y0, w, num, loc, code, hl, tag, scene)
        x += w + 8

draw_row(436, ROW1)
draw_row(566, ROW2)

# ---------------------------------------------------------------- map + list
MAP_X, MAP_Y, MAP_W, MAP_H = M, 696, 565, 266
LIST_X = 601

def ll(lon, lat):
    return (MAP_X + (lon + 170) / 360.0 * MAP_W,
            MAP_Y + (75 - lat) / 130.0 * MAP_H)

vgrad3(d, MAP_X, MAP_Y, MAP_X + MAP_W, MAP_Y + MAP_H, (20, 50, 90), (16, 40, 74),
       (10, 28, 54))
for gx in range(MAP_X + 47, MAP_X + MAP_W, 47):
    line(d, [(gx, MAP_Y), (gx, MAP_Y + MAP_H)], (255, 255, 255, 22), 1)
for gy in range(MAP_Y + 44, MAP_Y + MAP_H, 44):
    line(d, [(MAP_X, gy), (MAP_X + MAP_W, gy)], (255, 255, 255, 22), 1)
grain(d, MAP_X, MAP_Y, MAP_X + MAP_W, MAP_Y + MAP_H, phase=13.5, alpha=12,
      step=5, base2=(120, 140, 170))
# soft edge shading on the map ocean (true alpha, on the overlay)
orect(MAP_X, MAP_Y, MAP_X + 14, MAP_Y + MAP_H, (6, 14, 30, 16))
orect(MAP_X + MAP_W - 14, MAP_Y, MAP_X + MAP_W, MAP_Y + MAP_H, (6, 14, 30, 16))
orect(MAP_X, MAP_Y, MAP_X + MAP_W, MAP_Y + 12, (6, 14, 30, 14))
orect(MAP_X, MAP_Y + MAP_H - 12, MAP_X + MAP_W, MAP_Y + MAP_H, (6, 14, 30, 12))

CONT = (201, 180, 137)
CONT_D = (168, 146, 106)
def continent(pts, fill=CONT):
    poly(d, [ll(lon, lat) for lon, lat in pts], fill=fill + (255,),
         outline=CONT_D + (255,))

continent([(30, 70), (40, 68), (60, 69), (80, 72), (100, 76), (120, 72),
           (140, 72), (160, 70), (170, 66), (178, 65), (170, 60), (162, 55),
           (158, 50), (150, 45), (142, 40), (135, 35), (130, 32), (127, 35),
           (122, 38), (120, 32), (115, 25), (110, 20), (108, 10), (105, 8),
           (100, 8), (97, 15), (95, 20), (90, 22), (85, 20), (80, 15),
           (75, 10), (72, 20), (65, 25), (60, 25), (55, 26), (50, 28),
           (48, 30), (42, 35), (38, 36), (35, 36), (30, 36), (30, 42),
           (28, 45), (30, 50), (30, 60)])
continent([(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (32, 31),
           (35, 28), (43, 12), (48, 11), (51, 10), (44, 0), (40, -10),
           (35, -20), (32, -28), (20, -35), (15, -30), (12, -18), (9, -2),
           (9, 4), (-8, 5), (-13, 10), (-17, 15)])
continent([(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 69), (-85, 66),
           (-80, 60), (-75, 45), (-70, 42), (-75, 35), (-80, 26), (-84, 30),
           (-90, 21), (-97, 16), (-105, 20), (-115, 28), (-125, 40),
           (-125, 49), (-140, 60), (-155, 58), (-165, 60)])
continent([(-80, 10), (-75, 5), (-70, 10), (-60, 5), (-50, 0), (-40, -5),
           (-35, -10), (-40, -20), (-48, -28), (-55, -35), (-65, -45),
           (-70, -52), (-73, -40), (-73, -30), (-80, -20), (-80, -10),
           (-77, 0)])
continent([(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57),
           (10, 59), (18, 56), (21, 55), (24, 58), (28, 60), (30, 62),
           (30, 70), (20, 70), (18, 66), (12, 65), (5, 60), (0, 55),
           (-5, 50), (-10, 45)])
continent([(114, -22), (114, -30), (120, -35), (130, -32), (140, -38),
           (150, -37), (153, -27), (146, -19), (142, -11), (136, -12),
           (132, -11), (126, -14), (122, -17), (114, -22)])
continent([(-55, 60), (-45, 60), (-40, 70), (-30, 70), (-25, 76), (-55, 76)])
continent([(-5, 50), (-3, 53), (-5, 58), (-2, 58), (0, 53), (-1, 50)])
continent([(130, 31), (132, 33), (135, 34), (138, 35), (140, 38), (141, 41),
           (140, 44), (142, 44), (143, 42), (141, 39), (139, 36), (136, 33),
           (132, 31)])
for ilon, ilat in [(95, 5), (100, 0), (105, -2), (110, -5), (115, -7),
                   (120, -8), (125, -8), (130, -5), (135, -4), (140, -6)]:
    x0, y0 = ll(ilon, ilat)
    ell(d, x0 - 3, y0 - 2, x0 + 3, y0 + 2, fill=CONT + (255,))

txt(d, MAP_X + 8, MAP_Y + 8, "WHERE IT HAPPENED", sans_b(11), WHITE, anchor="la")
txt(d, MAP_X + MAP_W - 8, MAP_Y + 10, "38 PINS \u2014 ONE PER STORY", sans(9),
    (210, 220, 235), anchor="ra")

# space badge (story 7) in the ocean, bottom-left
_sb = "7 \u00b7 SPACE \u2014 Mercury"
_sbw = tw(d, _sb, sans_b(9)) + 16
rr(d, MAP_X + 10, MAP_Y + MAP_H - 26, MAP_X + 10 + _sbw, MAP_Y + MAP_H - 8, 7,
   fill=RED + (255,))
txt(d, MAP_X + 18, MAP_Y + MAP_H - 21.5, _sb, sans_b(9), WHITE, anchor="la")

# compass rose in the South Atlantic (clear of pins)
_ccx, _ccy = MAP_X + 250, MAP_Y + 238
ell(d, _ccx - 10, _ccy - 10, _ccx + 10, _ccy + 10,
    outline=(255, 255, 255, 200), width=S(1))
poly(d, [(_ccx, _ccy - 8), (_ccx + 3, _ccy + 4), (_ccx - 3, _ccy + 4)],
     fill=(255, 255, 255, 230))
txt(d, _ccx, _ccy - 20, "N", sans_b(9), WHITE, anchor="ma")

# pins with greedy badge solver (deterministic)
PINS = [
    (1, 30.5, 50.4), (2, 84.9, 19.3), (3, 121.5, 25.0), (4, 4.4, 50.8),
    (5, 22.6, 51.2), (6, 30.7, 36.9), (8, 12.5, 41.9), (9, 35.6, 3.5),
    (10, -89.2, 13.7), (11, 174.8, -41.3), (12, -0.1, 51.5),
    (13, -121.9, 37.35), (14, -80.2, 25.8), (15, 139.7, 35.7),
    (16, 127.0, 37.5), (17, -122.4, 37.8), (18, -74.0, 40.7),
    (19, -77.0, 38.9), (20, -77.0, 38.9), (21, 46.7, 24.7),
    (22, 24.7, 59.4), (23, 57.0, 25.5), (24, 56.3, 26.6),
    (25, 34.5, 31.5), (26, 77.2, 28.6), (27, -58.4, -34.6),
    (28, 149.1, -35.3), (29, 92.0, 21.4), (30, 24.0, 49.8),
    (31, 35.5, 33.9), (32, 29.5, 12.5), (33, 33.8, -13.96),
    (34, -4.0, 5.3), (35, -115.1, 36.2), (36, 127.0, 37.5),
    (37, 139.7, 35.7), (38, 7.7, 45.07),
]
_OFFSETS = [(0, -17), (15, -11), (17, 0), (15, 11), (0, 17), (-15, 11),
            (-17, 0), (-15, -11), (0, -27), (26, -19), (26, 19), (-26, -19),
            (-26, 19), (0, 27), (34, 0), (-34, 0)]
_placed = []
for num, lon, lat in PINS:
    px, py = ll(lon, lat)
    bx, by = px, py - 17
    for dx, dy in _OFFSETS:
        cx, cy = px + dx, py + dy
        if not (MAP_X + 10 <= cx <= MAP_X + MAP_W - 10 and
                MAP_Y + 10 <= cy <= MAP_Y + MAP_H - 10):
            continue
        if all((cx - ox) ** 2 + (cy - oy) ** 2 >= 16.5 ** 2 for ox, oy in _placed):
            bx, by = cx, cy
            break
    _placed.append((bx, by))
    if abs(bx - px) > 10 or abs(by - py) > 10:
        line(d, [(px, py), (bx, by)], (255, 255, 255, 190), 1)
    ell(d, px - 3.5, py - 3.5, px + 3.5, py + 3.5, fill=(200, 40, 32, 255))
    ell(d, px - 5, py - 5, px + 5, py + 5, outline=(255, 255, 255, 255),
        width=S(1))
    # Europe-cluster badges are slightly smaller so the cluster breathes
    _eur = -11 <= lon <= 41 and 35 <= lat <= 71
    _br = 7.0 if _eur else 7.5
    _fs = 7.5 if _eur else 8
    ell(d, bx - _br, by - _br, bx + _br, by + _br, fill=WHITE + (255,),
        outline=(60, 60, 60, 255), width=S(1))
    txt(d, bx, by - (5.0 if _eur else 5.5), str(num), sans_b(_fs), INK, anchor="ma")

# ---------------------------------------------------------------- list panel
vgrad3(d, LIST_X, MAP_Y, W - M, MAP_Y + MAP_H, (255, 253, 246), (250, 246, 234),
       (244, 238, 222))
rr(d, LIST_X, MAP_Y, W - M, MAP_Y + MAP_H, 2, outline=(205, 192, 168), width=1)
txt(d, LIST_X + 8, MAP_Y + 6, "ALSO ON FRIDAY 20 NOVEMBER \u2014 24 MORE STORIES",
    sans_b(11), RED, anchor="la")
LIST = [
    (15, "Japan inflation 2.3%, core 2.2%; Dec rate rise in view. (Reuters)"),
    (16, "Seoul ruling party moves to impeach top judge. (Korea Herald)"),
    (17, "Anthropic Nasdaq debut: $83 \u2192 $97.17 (+17%); $81.3B, largest IPO ever."),
    (18, "Bitcoin near $61,700, lowest since July, third day down."),
    (19, "US Senate blocks Iran war-powers resolution 51-48."),
    (20, "Trump in no rush on Iran: \u2018see what happens after January 1\u2019."),
    (21, "Houthi missile damages Riyadh\u2019s tallest tower; no injuries."),
    (22, "Estonia to shut Russia border from 1 Dec, for at least 6 months."),
    (23, "Tanker ablaze off Oman near Hormuz, no casualties. (UKMTO)"),
    (24, "Hormuz: Brent $92.50; 46 ships waiting."),
    (25, "Gaza: Israeli strikes kill 6 despite truce."),
    (26, "Pakistan minister visits New Delhi, first since May 2025. (PTI)"),
    (27, "Argentina country risk jumps to 1,070, up 15%. (JPM)"),
    (28, "Australia: Xi hails \u2018full turnaround\u2019 in China ties."),
    (29, "Rohingya camps weep and pray after ICJ ruling. (Al Jazeera)"),
    (30, "Lviv railway station strike kills 2. (BBC)"),
    (31, "Lebanon: Israeli strikes hit south and east."),
    (32, "Sudan army claims gains in West Kordofan."),
    (33, "Malawi fuel crisis brings night-long petrol queues. (Al Jazeera)"),
    (34, "AfDB: 22 African states near debt distress. (allAfrica)"),
    (35, "Las Vegas: Russell fastest in wet Grand Prix practice. (Autosport)"),
    (36, "Seoul: 111 students caught cheating in Suneung exam."),
    (37, "Tokyo: SoftBank shares fall 14% in a day. (Al Jazeera)"),
    (38, "Turin: ATP backs plan to lift player pay past $350m. (Anadolu)"),
]
_ly = MAP_Y + 22
for num, s in LIST:
    txt(d, LIST_X + 8, _ly, str(num), sans_b(9), RED, anchor="la")
    txt(d, LIST_X + 8 + tw(d, str(num) + "  ", sans_b(9)), _ly, s, sans(9),
        INK, anchor="la")
    _ly += 10.1

# ---------------------------------------------------------------- date check + footer
DC_Y0, DC_Y1 = 968, 1000
vgrad3(d, M, DC_Y0, W - M, DC_Y1, (253, 238, 232), (251, 233, 226), (248, 228, 220))
rr(d, M, DC_Y0, W - M, DC_Y1, 2, outline=RED, width=1)
txt(d, M + 8, DC_Y0 + 3, "DATE CHECK \u2014 WHAT WE LEFT OUT", sans_b(10), RED,
    anchor="la")
txt(d, M + 8, DC_Y0 + 14,
    "Thursday 19 Nov news: World Court ruling on Myanmar \u00b7 three-leader "
    "declaration in Shenzhen \u00b7 Tonga drought emergency \u00b7 Anthropic $83 IPO pricing.",
    sans(9), BODY, anchor="la")
txt(d, M + 8, DC_Y0 + 24,
    "Not yet happened by Friday night: BepiColombo\u2019s Mercury orbit entry "
    "\u00b7 COP31 final text \u00b7 ATP Finals final.",
    sans(9), BODY, anchor="la")

txt(d, W / 2, 1004,
    "Every story here happened, or was first reported, on Friday 20 November 2026. "
    "Officials\u2019 counts are attributed.",
    sans(8.5), GREY, anchor="ma")
txt(d, W / 2, 1013,
    "Sources: Reuters, AP, AFP, BBC, Al Jazeera, Kyiv Independent, IMD, Deccan Herald, "
    "ESA, UN News \u2014 original vector drawings.",
    sans(8.5), GREY, anchor="ma")

# ---------------------------------------------------------------- downscale + save
import os
# true alpha compositing for the searchlight beams (ImageDraw replaces
# pixels on RGBA instead of blending, so translucent fills drawn earlier
# would render at full strength)
if BEAMS:
    _ov = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    _od = ImageDraw.Draw(_ov)
    for _pts, _al in BEAMS:
        _od.polygon([(S(x), S(y)) for x, y in _pts],
                    fill=(255, 240, 200, _al))
    img = Image.alpha_composite(img, _ov)
img = Image.alpha_composite(img, ov)
out = img.convert("RGB").resize((W, H), Image.LANCZOS)
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
out.save(path, "PNG", optimize=True)
colors = out.getcolors(maxcolors=10000000)
ncolors = len(colors) if colors is not None else -1
print("saved", path, out.size, os.path.getsize(path), "bytes,",
      ncolors, "unique colours")
