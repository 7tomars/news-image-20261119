#!/usr/bin/env python3
"""Newspaper poster generator for Thursday 19 November 2026.

Draws a one-page English newspaper poster (1024x1024 PNG) covering eight
verified world stories from Thursday 19 November 2026.

Standard library only, no network access. The PNG encoder and the bitmap
font below are written from scratch in this file, so the program runs on
any Python 3.12+ with nothing to install.

Output: entry.png inside $MAKEFUN_OUTPUT_DIR when set, otherwise /output.
The render is fully deterministic: no timestamps, no randomness, stable
iteration order, so repeated runs produce byte-identical files.
"""

import hashlib
import os
import struct
import sys
import time
import zlib

WIDTH = 1024
HEIGHT = 1024

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
DARK_RED = (139, 0, 0)
GREY = (110, 110, 110)
LIGHT_GREY = (210, 210, 210)
PAPER = (252, 250, 244)

# ---------------------------------------------------------------------------
# 5x7 bitmap font (uppercase only; every glyph is 7 rows of 5 pixels).
# "1" is an inked pixel, "0" is empty. Glyphs are hand-drawn for this file.
# ---------------------------------------------------------------------------

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
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "—": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
}

GLYPH_W = 5
GLYPH_H = 7


class Canvas:
    """An RGB pixel buffer with simple rectangle and bitmap-text drawing."""

    def __init__(self, width, height, background):
        self.width = width
        self.height = height
        self.pixels = bytearray(background * (width * height))

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        r, g, b = color
        for yy in range(y0, y1):
            base = (yy * self.width + x0) * 3
            for xx in range(x0, x1):
                off = base + (xx - x0) * 3
                self.pixels[off] = r
                self.pixels[off + 1] = g
                self.pixels[off + 2] = b

    def text_width(self, text, scale):
        """Advance width in pixels of `text` drawn at `scale`."""
        return len(text) * (GLYPH_W + 1) * scale

    def draw_text(self, x, y, text, scale, color):
        """Draw uppercase text; unknown glyphs render as a blank space."""
        cx = x
        for ch in text:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(GLYPH_H):
                bits = glyph[row]
                for col in range(GLYPH_W):
                    if bits[col] == "1":
                        self.fill_rect(
                            cx + col * scale, y + row * scale, scale, scale, color
                        )
            cx += (GLYPH_W + 1) * scale
        return cx

    def draw_text_centered(self, y, text, scale, color, x0=0, x1=None):
        if x1 is None:
            x1 = self.width
        w = self.text_width(text, scale)
        return self.draw_text(x0 + (x1 - x0 - w) // 2, y, text, scale, color)


def wrap_text(text, max_width_px, scale):
    """Greedy word wrap; returns a list of lines that fit max_width_px."""
    char_w = (GLYPH_W + 1) * scale
    max_chars = max(1, max_width_px // char_w)
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        line = ""
        for word in words:
            trial = word if not line else line + " " + word
            if len(trial) <= max_chars:
                line = trial
            else:
                if line:
                    lines.append(line)
                # A single over-long word is split so nothing overflows.
                while len(word) > max_chars:
                    lines.append(word[:max_chars])
                    word = word[max_chars:]
                line = word
        if line:
            lines.append(line)
    return lines


def draw_wrapped(canvas, x, y, text, scale, color, max_width_px, line_gap=4):
    lines = wrap_text(text, max_width_px, scale)
    line_h = GLYPH_H * scale + line_gap
    for i, line in enumerate(lines):
        canvas.draw_text(x, y + i * line_h, line, scale, color)
    return y + len(lines) * line_h


# ---------------------------------------------------------------------------
# Content: eight verified stories from Thursday 19 November 2026.
# Headlines are uppercase by design (newspaper style); sub-decks are also
# set in capitals because the built-in font only carries capitals.
# Date discipline, checked against the sources in README.md:
#  - Kerch: the road span fell in the 17 Nov strike; 19 Nov hit only the
#    railway section, so the poster says so and never claims a 19 Nov fall.
#  - Anthropic: the $83 IPO price was set Wed 18 Nov; 19 Nov is the first
#    day of trading (ticker ANT), so the poster says "debut", not "priced".
#  - Bangladesh: Yunus's ancestral home was torched late Wed 18 Nov and
#    the four deaths span Tue-Thu; the lockdown itself is Thu 19 Nov.
# ---------------------------------------------------------------------------

MASTHEAD = "THE WORLD TODAY"
DATE_LINE = "THURSDAY 19 NOVEMBER 2026"

LEAD_HEADLINE = "TRUMP, XI AND PUTIN HOLD FIRST THREE-WAY SUMMIT IN SHENZHEN"
LEAD_SUB = (
    "LEADERS MEET ON APEC SIDELINES AND ISSUE A JOINT DECLARATION ON "
    "DIALOGUE OVER NUCLEAR RISKS AND NON-PROLIFERATION; NO DEAL ON "
    "UKRAINE OR IRAN."
)

# (kicker, headline, sub-deck) for the seven stories below the lead.
STORIES = [
    (
        "THE HAGUE",
        "UN TOP COURT RULES MYANMAR COMMITTED GENOCIDE AGAINST ROHINGYA",
        "ICJ RULES IN THE GAMBIA'S CASE; FIRST TIME THE COURT HOLDS A "
        "STATE RESPONSIBLE FOR GENOCIDE, OVER THE 2017 CRACKDOWN.",
    ),
    (
        "BLACK SEA",
        "UKRAINE HITS KERCH BRIDGE RAIL LINE IN THIRD STRIKE IN FOUR DAYS",
        "NEPTUNE MISSILES STRIKE THE RAILWAY SECTION OVERNIGHT; TRAIN "
        "TRAFFIC HALTED. THE ROAD SPAN FELL IN THE 17 NOVEMBER STRIKE.",
    ),
    (
        "RIYADH",
        "HOUTHI MISSILE DAMAGES RIYADH'S PIF TOWER",
        "BLAST BLOWS OUT WINDOWS ACROSS SEVEN FLOORS OF SAUDI ARABIA'S "
        "SOVEREIGN WEALTH FUND HEADQUARTERS; NO INJURIES REPORTED.",
    ),
    (
        "WALL STREET",
        "ANTHROPIC DEBUTS ON NASDAQ IN RECORD $81.3 BILLION IPO",
        "SHARES BEGIN TRADING THURSDAY UNDER TICKER ANT. THE $83 IPO "
        "PRICE WAS SET ON WEDNESDAY 18 NOVEMBER.",
    ),
    (
        "COPENHAGEN",
        "DENMARK APPROVES GREENLAND SECURITY DEAL 109-0",
        "PARLIAMENT BACKS THE US-DENMARK-GREENLAND PACT EXPANDING US "
        "BASES, ENDING MONTHS OF TENSION OVER THE ISLAND.",
    ),
    (
        "DHAKA",
        "BANGLADESH SHUTS DOWN AS AWAMI LEAGUE LOCKDOWN TAKES HOLD",
        "FOUR DEAD IN TWO DAYS OF VIOLENCE; NOBEL LAUREATE MUHAMMAD "
        "YUNUS'S ANCESTRAL HOME IN CHATTOGRAM TORCHED.",
    ),
    (
        "ANTALYA",
        "COP31 DRAFT DROPS ALL MENTION OF FOSSIL FUELS",
        "ANTALYA TEXT CUT FROM 144 TO 80 PARAGRAPHS ON THURSDAY; 21 "
        "ISSUES STILL UNRESOLVED AS TALKS CLOSE FRIDAY.",
    ),
]

FOOTER = "EIGHT VERIFIED STORIES FROM THURSDAY 19 NOVEMBER 2026"


def render():
    c = Canvas(WIDTH, HEIGHT, PAPER)
    margin = 36
    inner = WIDTH - 2 * margin  # 952 px

    # --- Masthead -------------------------------------------------------
    y = 24
    c.draw_text_centered(y, MASTHEAD, 6, BLACK)
    y += GLYPH_H * 6 + 10

    # --- Date: dominant, deep red, full width ---------------------------
    # 26 chars at scale 6 = 936 px, centred inside the 952 px column.
    c.draw_text_centered(y, DATE_LINE, 6, DARK_RED)
    y += GLYPH_H * 6 + 8

    # Double rule under the date.
    c.fill_rect(margin, y, inner, 4, BLACK)
    y += 6
    c.fill_rect(margin, y, inner, 2, BLACK)
    y += 12

    # --- Lead story, full width ------------------------------------------
    c.draw_text(margin, y, "LEAD STORY", 2, DARK_RED)
    y += GLYPH_H * 2 + 6
    y = draw_wrapped(c, margin, y, LEAD_HEADLINE, 3, BLACK, inner, line_gap=5)
    y += 6
    y = draw_wrapped(c, margin, y, LEAD_SUB, 2, BLACK, inner, line_gap=3)
    y += 10
    c.fill_rect(margin, y, inner, 2, BLACK)
    y += 12

    # --- Seven stories in two columns ------------------------------------
    gap = 28
    col_w = (inner - gap) // 2  # 462 px
    col_x = [margin, margin + col_w + gap]

    # Rows of two; the last row holds a single story, centred column.
    rows = [STORIES[i : i + 2] for i in range(0, len(STORIES), 2)]
    for row in rows:
        row_top = y
        row_bottom = row_top
        for idx, (kicker, headline, sub) in enumerate(row):
            x = col_x[idx] if len(row) == 2 else margin + (inner - col_w) // 2
            cy = row_top
            c.draw_text(x, cy, kicker, 2, DARK_RED)
            cy += GLYPH_H * 2 + 4
            # Headline at scale 3: 25 chars per line in a 462 px column.
            cy = draw_wrapped(c, x, cy, headline, 3, BLACK, col_w, line_gap=5)
            cy += 4
            # Sub-deck at scale 2: 38 chars per line.
            cy = draw_wrapped(c, x, cy, sub, 2, BLACK, col_w, line_gap=2)
            row_bottom = max(row_bottom, cy)
        y = row_bottom + 8
        c.fill_rect(margin, y, inner, 1, LIGHT_GREY)
        y += 10

    # --- Footer -----------------------------------------------------------
    c.fill_rect(margin, y, inner, 3, BLACK)
    y += 10
    c.draw_text_centered(y, FOOTER, 2, GREY)

    return c


# ---------------------------------------------------------------------------
# Minimal PNG encoder: 8-bit RGB, no filtering, zlib level 9.
# ---------------------------------------------------------------------------

def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(canvas):
    ihdr = struct.pack(">IIBBBBB", canvas.width, canvas.height, 8, 2, 0, 0, 0)
    raw = bytearray()
    for yy in range(canvas.height):
        raw.append(0)  # filter type 0 (None) for every scanline
        start = yy * canvas.width * 3
        raw += canvas.pixels[start : start + canvas.width * 3]
    idat = zlib.compress(bytes(raw), 9)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", idat)
        + _chunk(b"IEND", b"")
    )


def output_path():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    return os.path.join(out_dir, "entry.png")


def main():
    started = time.monotonic()
    canvas = render()
    png = encode_png(canvas)
    path = output_path()
    with open(path, "wb") as fh:
        fh.write(png)
    elapsed = time.monotonic() - started
    digest = hashlib.sha256(png).hexdigest()
    print(f"wrote {path}")
    print(f"size: {len(png)} bytes")
    print(f"dimensions: {WIDTH}x{HEIGHT}")
    print(f"sha256: {digest}")
    print(f"runtime: {elapsed:.2f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
