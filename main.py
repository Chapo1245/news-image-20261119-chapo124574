#!/usr/bin/env python3
"""news-image-20261119 v2 — one image summing up Thursday 19 November 2026.

Fresh re-author for v2 (no v1 code, image or layout reused). Procedural drawing
with Python stdlib only; no network at runtime; deterministic output.

Variants (MAKEFUN_VARIANT env, default "A"):
  A PHOTO-GRID  — 3x3 grid of large photo panels, bold headlines, huge masthead.
  B HERO+STRIP  — one big Kerch Bridge hero + 8 small strip panels.
  C BROADSHEET  — newspaper front page, lead story + 2x3 grid.
The shipped default is the self-graded winner (A).

Stories: only the 9 verified 19 Nov 2026 stories from the research brief,
worded exactly as verified. No speculation, no invented events.
"""
import math
import os
import struct
import zlib

W, H = 1024, 1024
VARIANT = os.environ.get("MAKEFUN_VARIANT", "A")

# ---------------------------------------------------------------- font (5x7)
# Each glyph: 7 rows of 5 bits, '#' = on.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    "·": ("00000", "00000", "00000", "00000", "01100", "01100", "00000"),
    "•": ("00000", "00000", "01110", "11111", "11111", "01110", "00000"),
}


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def _glyph_rows(ch):
    return FONT.get(ch, FONT["?"])


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(bg * (w * h))

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:(yy * self.w + x1) * 3] = c * (x1 - x0)

    def hline(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.rect(x, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c, thick=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.rect(x0, y0, thick, thick, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            d = r * r - (yy - cy) ** 2
            if d < 0:
                continue
            dx = int(d ** 0.5)
            self.rect(cx - dx, yy, dx * 2 + 1, 1, c)

    def ring(self, cx, cy, r, c, thick=2):
        for t in range(thick):
            rr = r - t
            if rr <= 0:
                continue
            for a in range(0, 360, 2):
                x = cx + int(rr * math.cos(math.radians(a)))
                y = cy + int(rr * math.sin(math.radians(a)))
                self.px(x, y, c)

    def ellipse(self, cx, cy, rx, ry, c):
        if rx <= 0 or ry <= 0:
            return
        for yy in range(cy - ry, cy + ry + 1):
            t = 1 - ((yy - cy) / ry) ** 2
            if t <= 0:
                continue
            dx = int(rx * (t ** 0.5))
            self.rect(cx - dx, yy, dx * 2 + 1, 1, c)

    def triangle(self, p1, p2, p3, c):
        pts = sorted([p1, p2, p3], key=lambda p: p[1])
        (x1, y1), (x2, y2), (x3, y3) = pts
        for y in range(y1, y3 + 1):
            xs = []
            for (xa, ya), (xb, yb) in (((x1, y1), (x2, y2)), ((x2, y2), (x3, y3)), ((x1, y1), (x3, y3))):
                if ya <= y <= yb and ya != yb:
                    xs.append(xa + (xb - xa) * (y - ya) / (yb - ya))
                elif y == ya == yb:
                    xs.extend([xa, xb])
            if len(xs) >= 2:
                self.rect(int(min(xs)), y, int(max(xs)) - int(min(xs)) + 1, 1, c)

    def text(self, x, y, s, c, scale=2, bold=False):
        cx = x
        for ch in s:
            rows = _glyph_rows(ch)
            for gy, row in enumerate(rows):
                for gx, bit in enumerate(row):
                    if bit == "1":
                        self.rect(cx + gx * scale, y + gy * scale, scale, scale, c)
                        if bold:
                            self.rect(cx + gx * scale + 1, y + gy * scale, scale, scale, c)
            cx += 6 * scale
        return cx

    def text_center(self, cx, y, s, c, scale=2, bold=False):
        self.text(cx - text_w(s, scale) // 2, y, s, c, scale, bold)

    def wrap(self, s, max_w, scale):
        # Split overlong single words by character so no line ever overflows.
        max_chars = max(1, (max_w + scale) // (6 * scale))
        words = []
        for wd in s.split(" "):
            while len(wd) > max_chars:
                words.append(wd[:max_chars])
                wd = wd[max_chars:]
            if wd:
                words.append(wd)
        lines, cur = [], ""
        for wd in words:
            trial = (cur + " " + wd).strip()
            if text_w(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines


def lcg(seed):
    x = seed
    while True:
        x = (1103515245 * x + 12345) & 0x7FFFFFFF
        yield x


def speckle(cv, x, y, w, h, seed, frac=8, delta=9):
    """Sparse deterministic light/dark speckle for texture (keeps PNG small)."""
    gen = lcg(seed)
    for yy in range(y, y + h, 2):
        for xx in range(x, x + w, 2):
            if next(gen) % 100 < frac:
                i = (yy * cv.w + xx) * 3
                d = delta if next(gen) % 2 else -delta
                for k in range(3):
                    v = cv.buf[i + k] + d
                    cv.buf[i + k] = 255 if v > 255 else (0 if v < 0 else v)


def vgrad(cv, x, y, w, h, top, bot, bands=10):
    for b in range(bands):
        t = b / (bands - 1)
        c = bytes(round(top[k] + (bot[k] - top[k]) * t) for k in range(3))
        cv.rect(x, y + b * h // bands, w, h // bands + 1, c)


# ---------------------------------------------------------------- palette
INK = bytes((20, 24, 38))          # near-black navy
PAPER = bytes((245, 239, 227))     # newsprint cream
WHITE = bytes((255, 255, 255))
RED = bytes((185, 28, 28))
NAVY = bytes((20, 33, 61))
GREY = bytes((90, 96, 110))

# ---------------------------------------------------------------- stories
# Only verified 19 Nov 2026 stories, exact careful wording from research.
STORIES = [
    dict(id="jeffries", lines=["JEFFRIES", "NOMINATED"],
         sub="First Black Speaker-in-waiting", src="CNN",
         scene="capitol", sky=(186, 214, 235), ground=(196, 178, 140)),
    dict(id="summit", lines=["LEADERS GATHER", "IN CHINA"],
         sub="Trump, Xi, Putin shake hands", src="NYT",
         scene="handshake", sky=(214, 228, 240), ground=(170, 150, 120)),
    dict(id="kerch", lines=["BRIDGE HIT", "A 3RD TIME"],
         sub="Traffic halted", src="BBC",
         scene="bridge", sky=(232, 164, 120), ground=(70, 110, 150)),
    dict(id="gaza", lines=["ISRAEL GROUND", "OP IN GAZA"],
         sub="Beyond Yellow Line", src="THE HINDU",
         scene="tent", sky=(222, 210, 180), ground=(150, 132, 100)),
    dict(id="cyclone", lines=["CYCLONE AKVAN", "NEARS INDIA"],
         sub="Andhra-Odisha coast", src="THE HINDU",
         scene="cyclone", sky=(160, 190, 220), ground=(40, 90, 130)),
    dict(id="euloan", lines=["EU PROPOSES", "45BN EURO LOAN"],
         sub="Repaid after Russia pays", src="JAGRANJOSH",
         scene="coins", sky=(200, 210, 235), ground=(60, 80, 140)),
    dict(id="pew", lines=["MUSLIMS TO", "OUTNUMBER", "CHRISTIANS"],
         sub="By 2035 - Pew Research", src="NDTV",
         scene="chart", sky=(235, 228, 200), ground=(120, 110, 90)),
    dict(id="eisenkot", lines=["EISENKOT ASKED", "TO FORM GOVT"],
         sub="Bypassing Netanyahu", src="PARIS EYE",
         scene="govt", sky=(210, 220, 232), ground=(140, 140, 130)),
    dict(id="france", lines=["FRANCE PROTESTS", "4TH WEEKEND"],
         sub="Cost of living", src="PARIS EYE",
         scene="crowd", sky=(235, 200, 170), ground=(90, 90, 100)),
]


# ---------------------------------------------------------------- scenes
def scene_capitol(cv, x, y, w, h, st):
    vgrad(cv, x, y, w, h, st["sky"], (240, 236, 224))
    speckle(cv, x, y, w, h, 11)
    gy = y + h - 26
    cv.rect(x, gy, w, 26, st["ground"])
    cx, base = x + w // 2, gy
    cv.circle(cx, base - 58, 34, WHITE)
    cv.rect(cx - 34, base - 58, 68, 10, WHITE)
    cv.rect(cx - 3, base - 100, 6, 12, NAVY)
    cv.circle(cx, base - 102, 5, RED)
    for dx in (-46, -24, 24, 46):
        cv.rect(cx + dx - 6, base - 48, 12, 48, WHITE)
    cv.rect(cx - 58, base - 52, 116, 6, WHITE)
    cv.vline(x + w - 26, base - 84, 84, INK)
    cv.rect(x + w - 26, base - 84, 22, 13, RED)


def scene_handshake(cv, x, y, w, h, st):
    vgrad(cv, x, y, w, h, st["sky"], (238, 232, 214))
    speckle(cv, x, y, w, h, 23)
    gy = y + h - 24
    cv.rect(x, gy, w, 24, st["ground"])
    cx, cy = x + w // 2, y + h // 2 - 6
    cols = [NAVY, RED, bytes((30, 90, 60))]
    for k, dx in enumerate((-w // 3, 0, w // 3)):
        fx = cx + dx
        cv.circle(fx, cy - 26, 20, cols[k])
        cv.ellipse(fx, cy + 34, 34, 30, cols[k])
    cv.circle(cx, cy + 8, 13, bytes((232, 190, 150)))
    cv.line(cx - 26, cy + 30, cx - 8, cy + 12, bytes((232, 190, 150)), 7)
    cv.line(cx + 26, cy + 30, cx + 8, cy + 12, bytes((232, 190, 150)), 7)
    for k, col in enumerate((bytes((200, 40, 40)), bytes((220, 180, 40)), bytes((40, 90, 180)))):
        cv.rect(x + 14 + k * 26, y + 10, 20, 12, col)


def scene_bridge(cv, x, y, w, h, st):
    vgrad(cv, x, y, w, h, st["sky"], (240, 200, 150))
    speckle(cv, x, y, w, h, 37)
    wy = y + h - 52
    cv.rect(x, wy, w, 52, st["ground"])
    for k in range(3):
        cv.hline(x + 12 + k * 30, wy + 12 + k * 12, 60, bytes((200, 220, 235)))
    dy = y + h - 92
    cv.rect(x + 8, dy, w - 16, 10, INK)
    cv.line(x + 30, dy, x + w // 2, dy - 52, INK, 4)
    cv.line(x + w - 30, dy, x + w // 2, dy - 52, INK, 4)
    for px in (x + 60, x + w // 2 - 4, x + w - 68):
        cv.rect(px, dy + 10, 8, 30, INK)
    bx = x + w // 2
    cv.circle(bx, dy - 8, 16, bytes((240, 120, 40)))
    cv.circle(bx - 8, dy - 16, 11, bytes((250, 200, 60)))
    cv.circle(bx - 22, dy - 34, 14, bytes((120, 120, 120)))
    cv.circle(bx + 6, dy - 40, 17, bytes((100, 100, 100)))
    cv.circle(bx + 24, dy - 28, 11, bytes((140, 140, 140)))


def scene_tent(cv, x, y, w, h, st):
    vgrad(cv, x, y, w, h, st["sky"], (240, 228, 200))
    speckle(cv, x, y, w, h, 41)
    gy = y + h - 30
    cv.rect(x, gy, w, 30, st["ground"])
    cv.rect(x, gy - 6, w, 8, bytes((90, 140, 180)))
    cx = x + w // 2
    cv.triangle((cx - 70, gy), (cx, gy - 78), (cx + 70, gy), bytes((220, 220, 205)))
    cv.triangle((cx - 34, gy), (cx, gy - 78), (cx + 34, gy), bytes((190, 70, 50)))
    cv.line(cx, gy - 78, cx, gy - 92, INK, 3)
    cv.rect(cx + 2, gy - 92, 16, 10, RED)
    for bx, by in ((x + 22, gy - 18), (x + 46, gy - 18), (x + w - 58, gy - 18)):
        cv.rect(bx, by, 22, 18, bytes((230, 190, 90)))
        cv.rect(bx, by, 22, 4, RED)


def scene_cyclone(cv, x, y, w, h, st):
    vgrad(cv, x, y, w, h, st["sky"], (200, 220, 235))
    speckle(cv, x, y, w, h, 53)
    gy = y + h - 26
    cv.rect(x, gy, w, 26, bytes((30, 70, 110)))
    cx, cy = x + w // 2, y + h // 2 - 4
    # spiral arms, radii scaled so the spiral never leaves the scene
    rmax = min(66, max(20, h // 2 - 10))
    rs = rmax / 66.0
    for r0, col in ((66, WHITE), (52, bytes((220, 230, 240))), (38, WHITE), (24, bytes((200, 215, 235)))):
        cv.ring(cx, cy, max(8, int(r0 * rs)), col, 9)
    cv.circle(cx, cy, 10, bytes((240, 240, 245)))
    cv.rect(x, gy - 10, w, 10, bytes((200, 180, 130)))
    for hx in (x + 24, x + w - 60):
        cv.rect(hx, gy - 26, 26, 16, bytes((240, 230, 210)))
        cv.triangle((hx - 3, gy - 26), (hx + 13, gy - 40), (hx + 29, gy - 26), RED)


def scene_coins(cv, x, y, w, h, st):
    vgrad(cv, x, y, w, h, st["sky"], (225, 228, 240))
    speckle(cv, x, y, w, h, 59)
    gy = y + h - 24
    cv.rect(x, gy, w, 24, st["ground"])
    gold = bytes((230, 180, 60))
    dark = bytes((180, 130, 30))
    for sx, n in ((x + 44, 4), (x + w // 2 - 22, 6), (x + w - 88, 3)):
        for k in range(n):
            cv.ellipse(sx + 22, gy - 10 - k * 12, 22, 7, gold)
            cv.ellipse(sx + 22, gy - 12 - k * 12, 22, 6, dark)
    cx, cy = x + w // 2, y + 42
    cv.circle(cx, cy, 26, bytes((40, 70, 160)))
    for k in range(8):
        a = math.radians(k * 45)
        cv.circle(cx + int(17 * math.cos(a)), cy + int(17 * math.sin(a)), 3, bytes((250, 210, 60)))


def scene_chart(cv, x, y, w, h, st):
    vgrad(cv, x, y, w, h, st["sky"], (242, 236, 214))
    speckle(cv, x, y, w, h, 67)
    gy = y + h - 30
    cv.rect(x, gy, w, 30, st["ground"])
    ox, oy = x + 26, gy - 8
    cv.vline(ox, y + 26, oy - y - 26, INK)
    cv.hline(ox, oy, w - 52, INK)
    # bars and arrow scale with scene height so nothing leaves the scene
    bw = max(30, w // 6)
    bh1, bh2 = int(0.42 * h), int(0.52 * h)
    cv.rect(ox + 34, oy - bh1, bw, bh1, bytes((60, 100, 180)))
    cv.rect(ox + 34, oy - bh1, bw, 10, bytes((40, 70, 140)))
    cv.rect(ox + 116, oy - bh2, bw, bh2, bytes((40, 150, 90)))
    cv.rect(ox + 116, oy - bh2, bw, 10, bytes((20, 110, 60)))
    ax0, ay0 = ox + 20, oy - int(0.28 * h)
    ax1, ay1 = ox + 190, oy - int(0.62 * h)
    cv.line(ax0, ay0, ax1, ay1, RED, 4)
    cv.line(ax1, ay1, ax1 - 22, ay1, RED, 4)
    cv.line(ax1, ay1, ax1, ay1 + 22, RED, 4)
    cv.text(x + w - 74, y + 12, "2035", RED, 2, True)


def scene_govt(cv, x, y, w, h, st):
    vgrad(cv, x, y, w, h, st["sky"], (236, 238, 244))
    speckle(cv, x, y, w, h, 71)
    gy = y + h - 26
    cv.rect(x, gy, w, 26, st["ground"])
    cx, base = x + w // 2, gy
    # verticals scale with scene height so the roof never leaves the scene
    u = min(1.0, h / 160.0)
    bh, rh, ch, dh, fh = (int(v * u) for v in (92, 122, 84, 40, 118))
    cv.rect(cx - 78, base - bh, 156, bh, WHITE)
    cv.rect(cx - 78, base - bh, 156, 8, NAVY)
    cv.triangle((cx - 84, base - bh), (cx, base - rh), (cx + 84, base - bh), NAVY)
    for dx in (-58, -30, -2, 26, 54):
        cv.rect(cx + dx - 5, base - ch, 10, ch, NAVY)
    cv.rect(cx - 14, base - dh, 28, dh, RED)
    cv.vline(x + w - 24, base - fh, fh, INK)
    cv.rect(x + w - 24, base - fh, 20, 12, bytes((40, 90, 180)))


def scene_crowd(cv, x, y, w, h, st):
    vgrad(cv, x, y, w, h, st["sky"], (242, 214, 190))
    speckle(cv, x, y, w, h, 83)
    gy = y + h - 24
    cv.rect(x, gy, w, 24, st["ground"])
    for px, col in ((x + 30, RED), (x + w // 2 - 40, NAVY), (x + w - 96, bytes((30, 110, 60)))):
        cv.vline(px + 18, y + 44, 66, INK)
        cv.rect(px, y + 18, 40, 28, col)
        cv.rect(px + 4, y + 22, 32, 4, WHITE)
        cv.rect(px + 4, y + 30, 24, 4, WHITE)
    cols = [bytes((40, 60, 90)), bytes((120, 60, 40)), bytes((60, 100, 60)), bytes((90, 70, 110))]
    for k in range(7):
        hx = x + 26 + k * ((w - 52) // 6)
        cv.circle(hx, gy - 34, 13, cols[k % 4])
        cv.ellipse(hx, gy - 2, 20, 18, cols[k % 4])


SCENES = {
    "capitol": scene_capitol, "handshake": scene_handshake, "bridge": scene_bridge,
    "tent": scene_tent, "cyclone": scene_cyclone, "coins": scene_coins,
    "chart": scene_chart, "govt": scene_govt, "crowd": scene_crowd,
}


# ---------------------------------------------------------------- panels
def draw_panel(cv, x, y, w, h, st, hscale, sub_scale=2):
    cv.rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, 3, RED)
    tag = st["src"]
    chip_w = text_w(tag, 1) + 10
    # Wrap the sub-line so it never runs under the source chip.
    sub_lines = cv.wrap(st["sub"].upper(), w - 24 - chip_w, sub_scale) if st["sub"] else []
    text_h = len(st["lines"]) * (7 * hscale + 5) + len(sub_lines) * (7 * sub_scale + 4) + 12
    scene_h = h - text_h - 4
    SCENES[st["scene"]](cv, x + 4, y + 4, w - 8, scene_h, st)
    ty = y + scene_h + 10
    for ln in st["lines"]:
        cv.text(x + 12, ty, ln, NAVY, hscale, True)
        ty += 7 * hscale + 5
    for ln in sub_lines:
        cv.text(x + 12, ty + 2, ln, GREY, sub_scale)
        ty += 7 * sub_scale + 4
    cv.rect(x + w - chip_w - 8, y + h - 20, chip_w, 14, NAVY)
    cv.text(x + w - chip_w - 3, y + h - 17, tag, WHITE, 1)


def masthead(cv, date_scale=8, tagline=True):
    cv.rect(0, 0, W, 118, PAPER)
    cv.text_center(W // 2, 12, "THE WORLD IN ONE IMAGE", INK, 2, True)
    cv.text_center(W // 2, 36, "19 NOVEMBER 2026", INK, date_scale, True)
    if tagline:
        cv.text_center(W // 2, 36 + 7 * date_scale + 6, "NINE STORIES  ·  THURSDAY", RED, 2, True)
    cv.rect(16, 114, W - 32, 3, INK)


def layout_a(cv):
    """PHOTO-GRID: 3x3 large photo panels."""
    masthead(cv)
    mx, my, gap = 16, 128, 12
    pw = (W - 2 * mx - 2 * gap) // 3
    ph = (H - my - 16 - 2 * gap) // 3
    for i, st in enumerate(STORIES):
        px = mx + (i % 3) * (pw + gap)
        py = my + (i // 3) * (ph + gap)
        draw_panel(cv, px, py, pw, ph, st, 3)
    cv.rect(0, 0, W, 4, RED)


def layout_b(cv):
    """HERO+STRIP: big Kerch hero + 8 small strips."""
    masthead(cv)
    mx, my, gap = 16, 128, 12
    hero = STORIES[2]
    hw, hh = W - 2 * mx, 420
    cv.rect(mx, my, hw, hh, WHITE)
    cv.rect(mx, my, hw, 3, RED)
    SCENES[hero["scene"]](cv, mx + 4, my + 4, hw - 8, 300, hero)
    cv.text(mx + 16, my + 316, "BRIDGE HIT A 3RD TIME", NAVY, 5, True)
    cv.text(mx + 16, my + 316 + 7 * 5 + 8, "TRAFFIC HALTED  ·  BBC", GREY, 3)
    rest = [s for s in STORIES if s["id"] != "kerch"]
    sw = (W - 2 * mx - 3 * gap) // 4
    sh = (H - my - hh - gap - 16 - gap) // 2
    for i, st in enumerate(rest):
        px = mx + (i % 4) * (sw + gap)
        py = my + hh + gap + (i // 4) * (sh + gap)
        draw_panel(cv, px, py, sw, sh, st, 2)
    cv.rect(0, 0, W, 4, RED)


def layout_c(cv):
    """BROADSHEET: lead left, one story right, 4x2 grid + sources box below."""
    masthead(cv)
    mx, my, gap = 16, 128, 12
    lead = STORIES[2]
    lw, lh = 470, 360
    cv.rect(mx, my, lw, lh, WHITE)
    cv.rect(mx, my, lw, 3, RED)
    SCENES[lead["scene"]](cv, mx + 4, my + 4, lw - 8, 240, lead)
    cv.text(mx + 12, my + 254, "BRIDGE HIT", NAVY, 4, True)
    cv.text(mx + 12, my + 254 + 7 * 4 + 5, "A 3RD TIME", NAVY, 4, True)
    cv.text(mx + 12, my + 254 + 2 * (7 * 4 + 5) + 2, "TRAFFIC HALTED  ·  BBC", GREY, 2)
    rx = mx + lw + gap
    rw = W - mx - rx
    draw_panel(cv, rx, my, rw, lh, STORIES[0], 3)
    gy = my + lh + gap
    gh = (H - gy - 16 - gap) // 2
    gw = (W - 2 * mx - 3 * gap) // 4
    rest = [s for s in STORIES if s["id"] not in ("kerch", "jeffries")]
    for i, st in enumerate(rest):
        px = mx + (i % 4) * (gw + gap)
        py = gy + (i // 4) * (gh + gap)
        draw_panel(cv, px, py, gw, gh, st, 2)
    # sources box fills the 8th slot
    sx = mx + 3 * (gw + gap)
    sy = gy + (gh + gap)
    cv.rect(sx, sy, gw, gh, NAVY)
    cv.text(sx + 14, sy + 16, "SOURCES", WHITE, 2, True)
    cv.text(sx + 14, sy + 44, "CNN - NYT - BBC", WHITE, 1)
    cv.text(sx + 14, sy + 60, "THE HINDU - NDTV", WHITE, 1)
    cv.text(sx + 14, sy + 76, "PARIS EYE", WHITE, 1)
    cv.text(sx + 14, sy + 92, "JAGRANJOSH", WHITE, 1)
    cv.text(sx + 14, sy + 122, "ALL STORIES", bytes((250, 210, 60)), 2, True)
    cv.text(sx + 14, sy + 142, "VERIFIED", bytes((250, 210, 60)), 2, True)
    cv.rect(0, 0, W, 4, RED)


LAYOUTS = {"A": layout_a, "B": layout_b, "C": layout_c}


# ---------------------------------------------------------------- png
def png_bytes(cv):
    raw = bytearray()
    for yy in range(cv.h):
        raw.append(0)
        raw += cv.buf[yy * cv.w * 3:(yy + 1) * cv.w * 3]

    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        return c + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main():
    cv = Canvas(W, H, PAPER)
    LAYOUTS[VARIANT](cv)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "entry.png"), "wb") as f:
        f.write(png_bytes(cv))


if __name__ == "__main__":
    main()
