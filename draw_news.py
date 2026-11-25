#!/usr/bin/env python3
"""Draw the 25 November 2026 world-news front page and save entry.png.

All artwork is drawn with Pillow shapes only; no external images, no
network. Output is deterministic: same input -> same bytes.
"""
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024
PAPER = (247, 243, 232)   # warm newsprint
INK = (18, 18, 18)
WHITE = (255, 255, 255)
RED = (178, 34, 34)
TEAL = (0, 110, 110)
NAVY = (25, 55, 110)
ORANGE = (200, 90, 0)
PURPLE = (95, 60, 140)
GREEN = (35, 110, 55)
GREY = (90, 90, 90)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap using real pixel widths."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_text_block(draw, x, y, lines, fnt, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


# ---------------------------------------------------------------- icons
def icon_ship(d, x, y, s, c):
    # hull
    d.polygon([(x, y + 58), (x + 96, y + 58), (x + 84, y + 82),
               (x + 12, y + 82)], fill=c)
    d.rectangle([x + 28, y + 34, x + 62, y + 58], fill=c)
    d.rectangle([x + 44, y + 16, x + 50, y + 34], fill=c)
    # waves
    for i, wy in enumerate((y + 92, y + 102)):
        d.arc([x - 6 + i * 4, wy, x + 30 + i * 4, wy + 12], 0, 180, fill=c, width=4)
        d.arc([x + 48 + i * 4, wy, x + 82 + i * 4, wy + 12], 0, 180, fill=c, width=4)
    # explosion star above the ship
    cx, cy = x + 78, y + 14
    d.polygon([(cx, cy - 14), (cx + 4, cy - 4), (cx + 14, cy - 6),
               (cx + 6, cy + 2), (cx + 12, cy + 12), (cx + 2, cy + 8),
               (cx - 2, cy + 16), (cx - 6, cy + 6), (cx - 16, cy + 8),
               (cx - 8, cy), (cx - 14, cy - 10), (cx - 4, cy - 6)],
              fill=(220, 60, 30))


def icon_globe(d, x, y, s, c):
    cx, cy, r = x + 48, y + 52, 42
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c, width=5)
    d.ellipse([cx - r // 2, cy - r, cx + r // 2, cy + r], outline=c, width=3)
    d.line([cx - r, cy, cx + r, cy], fill=c, width=3)
    d.arc([cx - r + 8, cy - r + 14, cx + r - 8, cy + r - 14], 200, 340, fill=c, width=3)
    d.arc([cx - r + 8, cy - r + 14, cx + r - 8, cy + r - 14], 20, 160, fill=c, width=3)
    # red cross-out for "no deal"
    d.line([cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2], fill=RED, width=7)
    d.line([cx + r + 2, cy - r - 2, cx - r - 2, cy + r + 2], fill=RED, width=7)


def icon_scales(d, x, y, s, c):
    d.line([x + 48, y + 12, x + 48, y + 84], fill=c, width=5)
    d.line([x + 12, y + 26, x + 84, y + 26], fill=c, width=5)
    d.line([x + 48, y + 84, x + 28, y + 96], fill=c, width=5)
    d.line([x + 48, y + 84, x + 68, y + 96], fill=c, width=5)
    for px in (12, 84):
        d.line([x + px, y + 26, x + px - 10, y + 58], fill=c, width=3)
        d.line([x + px, y + 26, x + px + 10, y + 58], fill=c, width=3)
        d.arc([x + px - 16, y + 52, x + px + 16, y + 74], 0, 180, fill=c, width=4)
    d.ellipse([x + 42, y + 6, x + 54, y + 18], fill=c)


def icon_tower(d, x, y, s, c):
    # tapering skyscraper
    d.polygon([(x + 34, y + 100), (x + 40, y + 14), (x + 58, y + 14),
               (x + 64, y + 100)], fill=c)
    for wy in range(y + 26, y + 96, 12):
        d.line([x + 40, wy, x + 58, wy], fill=WHITE, width=3)
    d.rectangle([x + 46, y + 4, x + 52, y + 14], fill=c)
    # blast at the top
    cx, cy = x + 49, y + 2
    d.polygon([(cx, cy - 12), (cx + 4, cy - 3), (cx + 13, cy - 5),
               (cx + 6, cy + 3), (cx + 11, cy + 11), (cx + 2, cy + 7),
               (cx - 2, cy + 15), (cx - 6, cy + 6), (cx - 15, cy + 7),
               (cx - 7, cy), (cx - 13, cy - 9), (cx - 4, cy - 5)],
              fill=(220, 60, 30))
    d.line([x + 8, y + 100, x + 88, y + 100], fill=c, width=4)


def icon_plane(d, x, y, s, c):
    # AWACS side view: fuselage + radar dome + tail fin + wing
    d.polygon([(x + 10, y + 58), (x + 82, y + 58), (x + 92, y + 64),
               (x + 82, y + 70), (x + 10, y + 70)], fill=c)  # fuselage
    d.polygon([(x + 10, y + 58), (x + 16, y + 38), (x + 26, y + 58)], fill=c)  # tail fin
    d.polygon([(x + 38, y + 70), (x + 56, y + 88), (x + 64, y + 70)], fill=c)  # wing
    d.line([x + 48, y + 44, x + 48, y + 58], fill=c, width=4)  # dome strut
    d.ellipse([x + 34, y + 24, x + 62, y + 46], fill=c)  # radar dome
    # motion lines
    for i, ly in enumerate((y + 56, y + 64, y + 72)):
        d.line([x + 2, ly, x + 8 - i * 2, ly], fill=c, width=3)


def icon_candle(d, x, y, s, c):
    # remembrance candle
    d.polygon([(x + 48, y + 6), (x + 58, y + 22), (x + 48, y + 32),
               (x + 38, y + 22)], fill=(230, 120, 20))
    d.ellipse([x + 40, y + 10, x + 56, y + 26], outline=(230, 120, 20), width=3)
    d.rectangle([x + 34, y + 38, x + 62, y + 96], fill=c)
    d.rectangle([x + 26, y + 96, x + 70, y + 104], fill=c)
    d.line([x + 48, y + 32, x + 48, y + 38], fill=INK, width=3)


STORIES = [
    ("UKRAINE HITS RUSSIAN SHIPS",
     "Sea drones sank a warship off Libya and hit a cargo ship in the Gulf of Finland.",
     icon_ship, NAVY),
    ("COP31 ENDS WITH NO DEAL",
     "Climate talks in Antalya collapsed as oil states blocked fossil-fuel language.",
     icon_globe, TEAL),
    ("HUAWEI FOUND GUILTY",
     "US jury convicts Huawei on 10 of 12 counts over its Iran business and fraud.",
     icon_scales, PURPLE),
    ("RIYADH TOWER STRUCK",
     "Houthi drone hits the capital's tallest tower for a second time; 11 wounded.",
     icon_tower, ORANGE),
    ("NATO SENDS AWACS TO POLAND",
     "Radar planes to watch the eastern flank after Russian missiles landed in Poland.",
     icon_plane, RED),
    ("GAZA TOLL: 74,746",
     "Gaza health ministry toll rises; UN agencies warn of a deepening humanitarian crisis.",
     icon_candle, GREEN),
]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W - 1, H - 1], outline=INK, width=6)

    # ---- masthead ----
    f_mast = font(SERIF_B, 92)
    d.text((W // 2, 18), "WORLD NEWS", font=f_mast, fill=INK, anchor="ma")
    f_date = font(SANS_B, 34)
    d.text((W // 2, 128), "Wednesday, 25 November 2026",
           font=f_date, fill=INK, anchor="ma")
    d.line([36, 178, W - 36, 178], fill=INK, width=3)
    d.line([36, 184, W - 36, 184], fill=INK, width=1)
    f_tag = font(SANS, 22)
    d.text((W // 2, 192), "THE DAY IN SIX STORIES",
           font=f_tag, fill=GREY, anchor="ma")

    # ---- story panels: 2 columns x 3 rows ----
    margin, gutter = 28, 20
    col_w = (W - 2 * margin - gutter) // 2
    top, bottom = 232, H - 28
    row_h = (bottom - top - 2 * gutter) // 3
    f_head = font(SANS_B, 27)
    f_sum = font(SANS, 21)

    for i, (headline, summary, icon_fn, accent) in enumerate(STORIES):
        col, row = i % 2, i // 2
        x0 = margin + col * (col_w + gutter)
        y0 = top + row * (row_h + gutter)
        x1, y1 = x0 + col_w, y0 + row_h
        d.rectangle([x0, y0, x1, y1], fill=WHITE, outline=INK, width=2)
        d.rectangle([x0, y0, x0 + 8, y1], fill=accent)

        # icon zone
        ix, iy = x0 + 22, y0 + 18
        d.rectangle([ix - 6, iy - 6, ix + 102, iy + 108],
                    outline=accent, width=2)
        icon_fn(d, ix, iy, 96, accent)

        # text zone
        tx = ix + 122
        tw = x1 - 14 - tx
        head_lines = wrap(d, headline, f_head, tw)
        y = y0 + 20
        y = draw_text_block(d, tx, y, head_lines, f_head, INK, 32)
        sum_lines = wrap(d, summary, f_sum, tw)
        draw_text_block(d, tx, y + 10, sum_lines, f_sum, (40, 40, 40), 26)

    img.save(OUT, "PNG", optimize=True)
    print("wrote", OUT, img.size, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
