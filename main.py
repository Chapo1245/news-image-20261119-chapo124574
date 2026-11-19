#!/usr/bin/env python3
"""news-image-20261119 — sum up Thursday 19 November 2026 world news in one image.

Pure Python 3 standard library. Draws a 1024x1024 PNG procedurally
(own 5x7 bitmap font, flat vector icons, hand-rolled PNG encoder)
and writes it to $MAKEFUN_OUTPUT_DIR/entry.png (default ./output).

Usage: python3 main.py [grid|hero|frontpage] [outdir]
Default variant is "grid". Output is fully deterministic:
running twice produces byte-identical PNGs.

Stories below were picked from news reported on 19 November 2026
(BBC, NYT, Al Jazeera, Reuters and wire reports read the same morning).
"""

import os
import struct
import sys
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 234)
INK = (20, 24, 32)
NAVY = (20, 33, 61)
NAVY2 = (27, 58, 107)
WHITE = (255, 255, 255)
GOLD = (232, 184, 75)
RED = (193, 39, 45)
GREY = (90, 96, 108)
LIGHTGREY = (214, 208, 196)
CARD = (255, 255, 255)
BORDER = (200, 192, 176)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 cells, '#' = on. Uppercase, digits, punctuation.
FONT = {
    'A': [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    'B': ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    'C': [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    'D': ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    'E': ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    'F': ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    'G': [".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."],
    'H': ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    'I': [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    'J': ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    'K': ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    'L': ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    'M': ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    'N': ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    'O': [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    'P': ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    'Q': [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    'R': ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    'S': [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    'T': ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    'U': ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    'V': ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    'W': ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    'X': ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    'Y': ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    'Z': ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    '0': [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    '1': ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    '2': [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    '3': ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    '4': ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    '5': ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    '6': [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    '7': ["#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."],
    '8': [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    '9': [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    ' ': [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    '.': [".....", ".....", ".....", ".....", ".....", ".##..", ".##.."],
    ',': [".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."],
    '-': [".....", ".....", ".....", ".###.", ".....", ".....", "....."],
    "'": ["..#..", "..#..", ".....", ".....", ".....", ".....", "....."],
    '(': ["...#.", "..#..", "..#..", "..#..", "..#..", "..#..", "...#."],
    ')': [".#...", "..#..", "..#..", "..#..", "..#..", "..#..", ".#..."],
    '/': ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."],
    '$': ["..#..", ".####", "#.#.#", ".###.", "..#.#", "####.", "..#.."],
    '%': ["##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"],
    '&': [".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"],
    '+': [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    '=': [".....", ".....", "#####", ".....", "#####", ".....", "....."],
    '?': [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    '!': ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    '"': [".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."],
    ':': [".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."],
    ';': [".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."],
    '\u2022': [".....", ".....", ".###.", ".###.", ".###.", ".....", "....."],
}

NORMALISE = {'\u2014': '-', '\u2013': '-', '\u2019': "'", '\u201c': '"',
             '\u201d': '"', '\u00d7': 'x'}


def text_width(s, scale):
    return len(s) * 6 * scale


def wrap_text(text, max_chars):
    """Greedy word wrap; returns list of lines, each <= max_chars."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= max_chars:
            cur += " " + w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w=W, h=H, bg=PAPER):
        self.w, self.h = w, h
        self.px = bytearray(bg) * (w * h)

    def _set(self, x, y, col):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = col

    def fill_rect(self, x, y, w, h, col):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = col

    def rect(self, x, y, w, h, col, t=1):
        self.fill_rect(x, y, w, t, col)
        self.fill_rect(x, y + h - t, w, t, col)
        self.fill_rect(x, y, t, h, col)
        self.fill_rect(x + w - t, y, t, h, col)

    def hline(self, x0, x1, y, col, t=1):
        self.fill_rect(x0, y, x1 - x0, t, col)

    def vline(self, x, y0, y1, col, t=1):
        self.fill_rect(x, y0, t, y1 - y0, col)

    def line(self, x0, y0, x1, y1, col, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            self.fill_rect(x, y, t, t, col)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, col, filled=True):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            if filled:
                self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, col)
            else:
                self._set(cx - dx, cy + dy, col)
                self._set(cx + dx, cy + dy, col)
                self._set(cx + dy, cy - dx, col)
                self._set(cx - dy, cy - dx, col)

    def text(self, s, x, y, scale, col, align="left"):
        s = "".join(NORMALISE.get(c, c) for c in s.upper())
        if align == "center":
            x -= text_width(s, scale) // 2
        elif align == "right":
            x -= text_width(s, scale)
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT[' '])
            for r in range(7):
                row = g[r]
                for c in range(5):
                    if row[c] == '#':
                        self.fill_rect(cx + c * scale, y + r * scale,
                                       scale, scale, col)
            cx += 6 * scale
        return cx

    def text_lines(self, lines, x, y, scale, col, leading=None):
        if leading is None:
            leading = 7 * scale + 4
        for ln in lines:
            self.text(ln, x, y, scale, col)
            y += leading
        return y


# ---------------------------------------------------------------- PNG encode
def png_bytes(cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    data = zlib.compress(bytes(raw), 6)

    def chunk(tag, payload):
        c = struct.pack(">I", len(payload)) + tag + payload
        return c + struct.pack(">I", zlib.crc32(tag + payload) & 0xffffffff)

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", data) + chunk(b"IEND", b""))


# ---------------------------------------------------------------- stories
# (tag, strip colour, headline, summary, source, icon key)
STORIES = [
    ("SUMMIT", NAVY2,
     "TRUMP, XI AND PUTIN MEET IN CHINA",
     "Rare trilateral talks at the APEC summit in Shenzhen as the three leaders gather in one room.",
     "NYT - BBC", "globe"),
    ("GAZA", (122, 31, 31),
     "ISRAEL LAUNCHES RARE GAZA GROUND RAID",
     "Troops cross the Yellow Line in a ground operation beyond the ceasefire line, the army says.",
     "BBC - REUTERS", "tank"),
    ("CRIMEA", (61, 90, 128),
     "CRIMEAN BRIDGE ATTACKED AGAIN",
     "Traffic is halted on the link to mainland Russia after another attack, the Crimean head says.",
     "BBC", "bridge"),
    ("AI IPO", (14, 124, 102),
     "ANTHROPIC IN BIGGEST IPO EVER",
     "The Claude maker raises $81.3bn and debuts on Nasdaq in the largest listing in history.",
     "AL JAZEERA - BBC", "chip"),
    ("GAMING", (108, 43, 217),
     "GTA VI ROLLS OUT WORLDWIDE",
     "Gamers finally enter Vice City as Rockstar's long-awaited sequel begins its global launch.",
     "BBC", "pad"),
    ("SPACE", (16, 24, 40),
     "VOYAGER 1 REACHES ONE LIGHT-DAY",
     "Fifty years after launch, NASA's probe is now a full light-day from Earth - a first.",
     "AL JAZEERA", "sat"),
    ("CYCLONE", (14, 116, 144),
     "CYCLONE AKVAN NEARS INDIA",
     "The storm is set to cross the coast between Machilipatnam and Puri in the coming hours.",
     "TOI - APSDMA", "storm"),
    ("JUSTICE", (138, 109, 27),
     "MYANMAR FACES GENOCIDE VERDICT",
     "The UN court rules today on the Rohingya case - a historic first genocide verdict.",
     "BBC - ICJ", "scales"),
    ("ART", (180, 83, 9),
     "VAN GOGH SELLS FOR $190.4M",
     "A record price at auction after a long row over the painting's Nazi-era history.",
     "BBC", "art"),
]


# ---------------------------------------------------------------- icons
def draw_icon(cv, key, cx, cy, col, s=1):
    """Flat white icon centred at (cx, cy), ~56*s px box."""
    if key == "globe":
        cv.circle(cx, cy, 22 * s, col, filled=False)
        cv.vline(cx, cy - 22 * s, cy + 22 * s, col, 2)
        cv.hline(cx - 22 * s, cx + 22 * s, cy, col, 2)
        cv.hline(cx - 17 * s, cx + 17 * s, cy - 11 * s, col, 2)
        cv.hline(cx - 17 * s, cx + 17 * s, cy + 11 * s, col, 2)
    elif key == "tank":
        cv.fill_rect(cx - 24 * s, cy - 2 * s, 48 * s, 14 * s, col)
        cv.fill_rect(cx - 10 * s, cy - 13 * s, 20 * s, 11 * s, col)
        cv.hline(cx + 8 * s, cx + 32 * s, cy - 9 * s, col, 4)
        for dx in (-16, 0, 16):
            cv.circle(cx + dx * s, cy + 16 * s, 4 * s, col)
    elif key == "bridge":
        cv.hline(cx - 28 * s, cx + 28 * s, cy + 12 * s, col, 3)
        cv.fill_rect(cx - 23 * s, cy - 16 * s, 5 * s, 28 * s, col)
        cv.fill_rect(cx + 18 * s, cy - 16 * s, 5 * s, 28 * s, col)
        for t in range(9):
            fx = -28 + t * 7
            fy = 12 - int(26 * (1 - (fx / 28.0) ** 2))
            cv._set(cx + fx * s, cy + fy * s, col)
            cv._set(cx + fx * s, cy + (fy + 1) * s, col)
        for dx in (-14, 0, 14):
            cv.vline(cx + dx * s, cy - 2 * s, cy + 12 * s, col, 2)
    elif key == "chip":
        cv.rect(cx - 20 * s, cy - 20 * s, 40 * s, 40 * s, col, 3)
        cv.fill_rect(cx - 8 * s, cy - 8 * s, 16 * s, 16 * s, col)
        for dx in (-12, 0, 12):
            cv.fill_rect(cx + dx * s - 2, cy - 27 * s, 4 * s, 7 * s, col)
            cv.fill_rect(cx + dx * s - 2, cy + 20 * s, 4 * s, 7 * s, col)
            cv.fill_rect(cx - 27 * s, cy + dx * s - 2, 7 * s, 4 * s, col)
            cv.fill_rect(cx + 20 * s, cy + dx * s - 2, 7 * s, 4 * s, col)
    elif key == "pad":
        cv.rect(cx - 26 * s, cy - 13 * s, 52 * s, 26 * s, col, 3)
        cv.fill_rect(cx - 19 * s, cy - 4 * s, 12 * s, 4 * s, col)
        cv.fill_rect(cx - 15 * s, cy - 8 * s, 4 * s, 12 * s, col)
        cv.circle(cx + 12 * s, cy - 5 * s, 3 * s, col)
        cv.circle(cx + 20 * s, cy + 4 * s, 3 * s, col)
    elif key == "sat":
        cv.fill_rect(cx - 10 * s, cy - 8 * s, 20 * s, 16 * s, col)
        cv.fill_rect(cx - 34 * s, cy - 6 * s, 20 * s, 12 * s, col)
        cv.fill_rect(cx + 14 * s, cy - 6 * s, 20 * s, 12 * s, col)
        cv.line(cx, cy - 8 * s, cx + 10 * s, cy - 20 * s, col, 2)
        cv.circle(cx + 12 * s, cy - 21 * s, 3 * s, col)
        cv.circle(cx - 28 * s, cy - 20 * s, 2 * s, col)
        cv.circle(cx + 30 * s, cy + 18 * s, 2 * s, col)
    elif key == "storm":
        for r in (8, 15, 22):
            cv.circle(cx, cy, r * s, col, filled=False)
        cv.circle(cx, cy, 3 * s, col)
        cv.hline(cx + 24 * s, cx + 34 * s, cy - 18 * s, col, 2)
        cv.hline(cx - 34 * s, cx - 24 * s, cy + 18 * s, col, 2)
    elif key == "scales":
        cv.vline(cx, cy - 22 * s, cy + 20 * s, col, 3)
        cv.hline(cx - 22 * s, cx + 22 * s, cy - 22 * s, col, 3)
        cv.hline(cx - 8 * s, cx + 8 * s, cy + 20 * s, col, 3)
        for dx in (-22, 22):
            cv.line(cx + dx * s, cy - 22 * s, cx + (dx - 7) * s, cy + 2 * s, col, 2)
            cv.line(cx + dx * s, cy - 22 * s, cx + (dx + 7) * s, cy + 2 * s, col, 2)
            cv.hline(cx + (dx - 7) * s, cx + (dx + 7) * s, cy + 2 * s, col, 2)
    elif key == "art":
        cv.rect(cx - 24 * s, cy - 20 * s, 48 * s, 40 * s, col, 3)
        cv.circle(cx + 10 * s, cy - 9 * s, 6 * s, col)
        cv.hline(cx - 19 * s, cx + 19 * s, cy + 6 * s, col, 2)
        cv.line(cx - 19 * s, cy + 15 * s, cx - 4 * s, cy - 2 * s, col, 2)
        cv.line(cx - 4 * s, cy - 2 * s, cx + 19 * s, cy + 15 * s, col, 2)


# ---------------------------------------------------------------- shared bits
def masthead(cv):
    cv.fill_rect(0, 0, W, 168, NAVY)
    cv.text("THE WORLD IN ONE IMAGE", W // 2, 16, 2, GOLD, align="center")
    cv.text("19 NOVEMBER 2026", W // 2, 48, 7, WHITE, align="center")
    cv.fill_rect(W // 2 - 300, 110, 600, 3, GOLD)
    cv.text("THURSDAY - NINE STORIES THAT DEFINED THE DAY",
            W // 2, 126, 2, (200, 208, 220), align="center")


def footer(cv, y=994):
    cv.text("ALL STORIES REPORTED ON 19 NOVEMBER 2026  -  SOURCES: BBC, NYT, "
            "AL JAZEERA, REUTERS", W // 2, y, 1, GREY, align="center")


def story_card(cv, x, y, w, h, st, head_scale=2, sum_scale=2,
               strip_h=72, max_head=3, max_sum=5, show_source=True):
    tag, colour, headline, summary, source, icon = st
    cv.fill_rect(x, y, w, h, CARD)
    cv.rect(x, y, w, h, BORDER, 1)
    # icon strip
    cv.fill_rect(x, y, w, strip_h, colour)
    cv.text(tag, x + 14, y + strip_h // 2 - 7, 2, WHITE)
    draw_icon(cv, icon, x + w - 40, y + strip_h // 2, WHITE)
    inner = w - 24
    # headline
    hc = max(1, inner // (6 * head_scale))
    hlines = wrap_text(headline, hc)[:max_head]
    ty = y + strip_h + 12
    ty = cv.text_lines(hlines, x + 12, ty, head_scale, INK,
                       leading=7 * head_scale + 4)
    # summary
    sc = max(1, inner // (6 * sum_scale))
    slines = wrap_text(summary, sc)[:max_sum]
    cv.text_lines(slines, x + 12, ty + 6, sum_scale, (52, 58, 70),
                  leading=7 * sum_scale + 4)
    # source line at the bottom
    if show_source:
        cv.hline(x + 12, x + w - 12, y + h - 26, LIGHTGREY, 1)
        cv.text("SOURCE: " + source, x + 12, y + h - 18, 1, GREY)


# ---------------------------------------------------------------- variants
def render_grid(cv):
    masthead(cv)
    cw, ch, gx, gy = 329, 264, 8, 8
    for i, st in enumerate(STORIES):
        x = 10 + (i % 3) * (cw + gx)
        y = 176 + (i // 3) * (ch + gy)
        story_card(cv, x, y, cw, ch, st)
    footer(cv)


def render_hero(cv):
    masthead(cv)
    st = STORIES[0]
    cv.fill_rect(10, 176, 1004, 322, CARD)
    cv.rect(10, 176, 1004, 322, BORDER, 1)
    cv.fill_rect(10, 176, 1004, 10, RED)
    cv.text("TOP STORY - APEC SUMMIT, SHENZHEN", 34, 208, 2, RED)
    cv.text_lines(wrap_text(st[2], 21), 34, 244, 4, INK, leading=32)
    cv.text_lines(wrap_text(st[3], 40), 34, 330, 2, (52, 58, 70),
                  leading=18)
    cv.text("SOURCE: " + st[4], 34, 452, 1, GREY)
    draw_icon(cv, "globe", 880, 340, NAVY2, 3)
    cw, ch = 245, 240
    for i, st in enumerate(STORIES[1:]):
        x = 10 + (i % 4) * (cw + 8)
        y = 506 + (i // 4) * (ch + 8)
        story_card(cv, x, y, cw, ch, st, head_scale=2, sum_scale=1,
                   strip_h=56, max_head=3, max_sum=5, show_source=False)
    footer(cv, y=1000)


def render_frontpage(cv):
    masthead(cv)
    st = STORIES[0]
    cv.text(st[2], W // 2, 190, 4, INK, align="center")
    cv.text("RARE TRILATERAL TALKS AT THE APEC SUMMIT IN SHENZHEN",
            W // 2, 232, 2, RED, align="center")
    cv.fill_rect(W // 2 - 300, 262, 600, 3, RED)
    for i, ln in enumerate(wrap_text(st[3], 78)):
        cv.text(ln, W // 2, 278 + i * 18, 2, (52, 58, 70), align="center")
    cw, ch = 245, 320
    for i, st in enumerate(STORIES[1:]):
        x = 10 + (i % 4) * (cw + 8)
        y = 330 + (i // 4) * (ch + 8)
        story_card(cv, x, y, cw, ch, st, head_scale=2, sum_scale=2,
                   strip_h=60, max_head=3, max_sum=5, show_source=True)


def main():
    variant = (sys.argv[1] if len(sys.argv) > 1 else
               os.environ.get("MAKEFUN_VARIANT", "grid")).lower()
    outdir = (sys.argv[2] if len(sys.argv) > 2 else
              os.environ.get("MAKEFUN_OUTPUT_DIR", "output"))
    cv = Canvas()
    if variant == "hero":
        render_hero(cv)
    elif variant == "frontpage":
        render_frontpage(cv)
    else:
        render_grid(cv)
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(png_bytes(cv))
    print(f"wrote {path} ({variant})")


if __name__ == "__main__":
    main()
