#!/usr/bin/env python3
"""Rebuild the 20 November 2026 world-news front page, 1024x1024 PNG.

Layout: masthead, ticker strip, six story panels in a 2x3 grid, and a
timeline footer. Every story was verified against live reporting as a
20 November 2026 story before it was drawn:
 1. Kyiv barrage, 400+ drones / 110+ missiles, 8 killed (AP, Reuters, ISW)
 2. Cyclone Akvan landfall near Gopalpur, 300,000 evacuated (IMD, Hindu BL)
 3. Markets slide a seventh day; Nikkei -5.06% (Reuters, 20 Nov)
 4. Red Sea escalation: coalition bombs Hodeidah, Houthis warn airlines
    off Saudi skies (Reuters, 20 Nov)
 5. Haiti police kill 34 gang suspects in Martissant raid, reported 20 Nov
    (AP, Reuters)
 6. Sydney terror raids: man, 35, charged over IS car-bomb plot (AFP, ABC)
Deterministic: fixed geometry, fixed fonts, no randomness, no network.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

SIZE = 1024
PAPER = (248, 246, 239)
INK = (18, 18, 18)
RED = (139, 30, 30)
GREY = (92, 90, 84)
LIGHT = (221, 218, 209)

SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"


def load(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(draw, text, font, width):
    """Greedy word wrap returning a list of lines that fit width."""
    out, current = [], ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=font) <= width:
            current = trial
        else:
            if current:
                out.append(current)
            current = word
    if current:
        out.append(current)
    return out


def fit_headline(draw, text, width, start_size=28, limit=2):
    """Shrink the headline until it wraps into at most `limit` lines."""
    size = start_size
    while size > 16:
        fnt = load(SERIF_BOLD, size)
        lines = wrap_text(draw, text, fnt, width)
        if len(lines) <= limit:
            return fnt, lines
        size -= 1
    fnt = load(SERIF_BOLD, size)
    return fnt, wrap_text(draw, text, fnt, width)[:limit]


def wave(draw, x0, x1, y, amp=3, step=4):
    pts = [(x, y + amp * math.sin(x / 14.0)) for x in range(x0, x1, step)]
    draw.line(pts, fill=GREY, width=2)


def burst(draw, cx, cy, outer, inner=8, spikes=12):
    for k in range(spikes):
        a = math.radians(k * 360.0 / spikes)
        r = outer if k % 2 == 0 else outer * 0.62
        draw.line([(cx + inner * math.cos(a), cy + inner * math.sin(a)),
                   (cx + r * math.cos(a), cy + r * math.sin(a))],
                  fill=RED, width=3)
    draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=RED)


# ---------------- illustrations ----------------
def pic_kyiv(d, x0, y0, x1, y1):
    # skyline, a bridge with a gap in its deck, red burst over the gap
    base = y1 - 16
    for bx, bw, bh in ((x0 + 8, 42, 34), (x0 + 58, 30, 52), (x0 + 96, 36, 44),
                       (x1 - 130, 34, 58), (x1 - 88, 30, 40), (x1 - 52, 40, 30)):
        d.rectangle([bx, base - bh, bx + bw, base], fill=INK)
    mid = (x0 + x1) // 2
    d.line([(x0 + 4, base), (mid - 34, base)], fill=INK, width=4)
    d.line([(mid + 34, base), (x1 - 4, base)], fill=INK, width=4)
    for tx in (x0 + 70, x1 - 70):
        d.line([(tx, y0 + 8), (tx, base)], fill=INK, width=4)
        d.line([(tx - 12, y0 + 8), (tx + 12, y0 + 8)], fill=INK, width=3)
    burst(d, mid, base - 42, 30)
    wave(d, x0 + 6, x1 - 6, y1 - 6)


def pic_cyclone(d, x0, y0, x1, y1):
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2 - 8
    pts = []
    for t in range(0, 700, 5):
        a = math.radians(t)
        r = 2 + t * 0.068
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a) * 0.85))
    d.line(pts, fill=INK, width=3)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=RED)
    for i in range(5):
        xx = x0 + 22 + i * 30
        d.line([(xx, y1 - 30), (xx - 7, y1 - 12)], fill=INK, width=3)
    wave(d, x0 + 6, x1 - 6, y1 - 4)


def pic_markets(d, x0, y0, x1, y1):
    base = y1 - 14
    d.line([(x0 + 24, y0 + 8), (x0 + 24, base)], fill=INK, width=2)
    d.line([(x0 + 24, base), (x1 - 10, base)], fill=INK, width=2)
    steps = [(x0 + 34, y0 + 18), (x0 + 90, y0 + 26), (x0 + 146, y0 + 22),
             (x0 + 202, y0 + 40), (x0 + 258, y0 + 34), (x0 + 314, y0 + 56),
             (x0 + 370, y0 + 52), (x1 - 34, y0 + 74)]
    d.line(steps, fill=INK, width=3)
    d.line([(x0 + 52, y0 + 10), (x1 - 30, y0 + 78)], fill=RED, width=5)
    ang = math.atan2(y0 + 78 - (y0 + 10), (x1 - 30) - (x0 + 52))
    for da in (2.6, -2.6):
        d.line([(x1 - 30, y0 + 78),
                (x1 - 30 + 20 * math.cos(ang + da),
                 y0 + 78 + 20 * math.sin(ang + da))], fill=RED, width=5)
    d.text((x1 - 118, y0 + 2), "-5.06%", font=load(SANS_BOLD, 22), fill=RED)


def pic_redsea(d, x0, y0, x1, y1):
    # cargo ship with containers, a port crane, smoke over the water
    base = y1 - 18
    d.rectangle([x0 + 20, base - 26, x1 - 120, base - 6], fill=INK)
    d.polygon([(x0 + 20, base - 6), (x1 - 120, base - 6), (x1 - 96, base + 8),
               (x0 + 44, base + 8)], fill=INK)
    for i, col in enumerate((RED, INK, GREY)):
        bx = x0 + 40 + i * 52
        d.rectangle([bx, base - 52, bx + 44, base - 26], outline=INK, width=2)
        d.line([(bx, base - 39), (bx + 44, base - 39)], fill=col, width=2)
    d.line([(x1 - 96, y0 + 6), (x1 - 96, base - 6)], fill=INK, width=5)
    d.line([(x1 - 96, y0 + 6), (x1 - 44, y0 + 6)], fill=INK, width=5)
    d.line([(x1 - 96, y0 + 6), (x1 - 62, base - 6)], fill=INK, width=2)
    for ox, oy, r in ((0, 0, 9), (14, -8, 12), (30, -2, 10)):
        d.ellipse([x0 + 150 + ox - r, y0 + 22 + oy - r,
                   x0 + 150 + ox + r, y0 + 22 + oy + r],
                  outline=GREY, width=2)
    wave(d, x0 + 6, x1 - 6, y1 - 4)


def pic_haiti(d, x0, y0, x1, y1):
    # shield with a star, a striped barricade, and the toll as a badge
    cx = (x0 + x1) // 2 - 70
    cy = (y0 + y1) // 2 - 4
    shield = [(cx, cy - 44), (cx + 42, cy - 28), (cx + 42, cy + 8),
              (cx, cy + 46), (cx - 42, cy + 8), (cx - 42, cy - 28)]
    d.polygon(shield, outline=INK, width=4)
    star = []
    for k in range(10):
        a = math.radians(-90 + k * 36)
        rr = 15 if k % 2 == 0 else 6.5
        star.append((cx + rr * math.cos(a), cy - 2 + rr * math.sin(a)))
    d.polygon(star, fill=INK)
    bx0, by = cx + 62, cy - 16
    d.rectangle([bx0, by, x1 - 10, by + 24], fill=INK)
    for i in range(5):
        xx = bx0 + 6 + i * 24
        d.line([(xx, by + 24), (xx + 12, by)], fill=PAPER, width=5)
    d.text((bx0, by + 32), "MARTISSANT", font=load(SANS_BOLD, 15), fill=INK)
    d.ellipse([cx - 52, y1 - 34, cx + 52, y1 - 2], fill=RED)
    d.text((cx - 16, y1 - 31), "34", font=load(SANS_BOLD, 22), fill=PAPER)


def pic_sydney(d, x0, y0, x1, y1):
    # shield with a star, police tape running diagonally across the corner
    cx = (x0 + x1) // 2 - 60
    cy = (y0 + y1) // 2 - 4
    shield = [(cx, cy - 44), (cx + 42, cy - 28), (cx + 42, cy + 8),
              (cx, cy + 46), (cx - 42, cy + 8), (cx - 42, cy - 28)]
    d.polygon(shield, outline=INK, width=4)
    star = []
    for k in range(10):
        a = math.radians(-90 + k * 36)
        rr = 15 if k % 2 == 0 else 6.5
        star.append((cx + rr * math.cos(a), cy - 2 + rr * math.sin(a)))
    d.polygon(star, fill=INK)
    tx0, ty = cx + 58, y0 + 14
    d.rectangle([tx0, ty, x1 - 10, ty + 26], fill=INK)
    for i in range(6):
        xx = tx0 + 6 + i * 24
        d.line([(xx, ty + 26), (xx + 12, ty)], fill=PAPER, width=5)
    d.text((tx0, ty + 34), "RAIDS FROM 5AM", font=load(SANS_BOLD, 15), fill=INK)
    d.text((tx0, ty + 56), "10 SUBURBS", font=load(SANS_BOLD, 15), fill=GREY)


STORIES = [
    ("EUROPE \u2014 UKRAINE \u2022 20 NOV",
     "RUSSIA'S BIGGEST BARRAGE HITS KYIV",
     ("400+ drones, 110+ missiles; 8 killed",
      "Three Dnipro bridges hit; missiles in Poland"),
     pic_kyiv),
    ("ASIA \u2014 INDIA \u2022 20 NOV",
     "CYCLONE AKVAN SLAMS ODISHA",
     ("Landfall near Gopalpur, 02:00 UTC",
      "300,000 evacuated; 69 trains cancelled"),
     pic_cyclone),
    ("MARKETS \u2014 ASIA \u2022 20 NOV",
     "MARKETS SLIDE FOR A SEVENTH DAY",
     ("Nikkei \u22125.06%; Asia's worst week since 2020",
      "Anthropic \u221213.5% premarket on day two"),
     pic_markets),
    ("MIDDLE EAST \u2022 20 NOV",
     "RED SEA ESCALATION",
     ("Coalition bombs Hodeidah port",
      "Houthis warn airlines off Saudi skies"),
     pic_redsea),
    ("AMERICAS \u2014 HAITI \u2022 20 NOV",
     "HAITI POLICE KILL 34 IN GANG RAID",
     ("Martissant corridor retaken after 5 years",
      "No police or civilian casualties reported"),
     pic_haiti),
    ("OCEANIA \u2014 AUSTRALIA \u2022 20 NOV",
     "SYDNEY TERROR RAIDS",
     ("Man, 35, charged over IS car-bomb plot",
      "Raids from 5am; two others also charged"),
     pic_sydney),
]


def draw_panel(d, x0, y0, x1, y1, tag, headline, details, picture):
    d.rectangle([x0, y0, x1, y1], outline=INK, width=2)
    pad = 14
    ix0, ix1 = x0 + pad, x1 - pad
    d.text((ix0, y0 + 8), tag, font=load(SANS_BOLD, 15), fill=RED)
    picture(d, ix0, y0 + 30, ix1, y0 + 118)
    d.line([(ix0, y0 + 124), (ix1, y0 + 124)], fill=INK, width=1)
    hf, lines = fit_headline(d, headline, ix1 - ix0)
    yy = y0 + 130
    for line in lines:
        d.text((ix0, yy), line, font=hf, fill=INK)
        yy += hf.size + 1
    d.line([(ix0, yy + 3), (ix1, yy + 3)], fill=INK, width=1)
    yy += 11
    df = load(SANS, 16)
    for line in details:
        d.text((ix0, yy), line, font=df, fill=INK)
        yy += 20


def main():
    img = Image.new("RGB", (SIZE, SIZE), PAPER)
    d = ImageDraw.Draw(img)

    title = "THE WORLD TODAY"
    tf = load(SERIF_BOLD, 60)
    d.text(((SIZE - d.textlength(title, font=tf)) / 2, 10), title,
           font=tf, fill=INK)
    dateline = "FRIDAY 20 NOVEMBER 2026  \u2022  GLOBAL EDITION  \u2022  SIX STORIES, ONE DAY"
    df2 = load(SANS_BOLD, 18)
    d.text(((SIZE - d.textlength(dateline, font=df2)) / 2, 84), dateline,
           font=df2, fill=INK)
    d.line([(24, 118), (SIZE - 24, 118)], fill=INK, width=3)
    d.line([(24, 123), (SIZE - 24, 123)], fill=INK, width=1)

    # ticker band: the day in one line
    d.rectangle([24, 132, SIZE - 24, 162], fill=INK)
    ticker = "KYIV UNDER FIRE  \u2022  AKVAN LANDFALL  \u2022  MARKETS IN FREEFALL  \u2022  RED SEA ESCALATION  \u2022  HAITI RAID  \u2022  SYDNEY RAIDS"
    tf3 = load(SANS_BOLD, 16)
    d.text(((SIZE - d.textlength(ticker, font=tf3)) / 2, 139), ticker,
           font=tf3, fill=PAPER)

    # six panels, 2 columns x 3 rows
    m, g = 24, 12
    pw = (SIZE - 2 * m - g) // 2
    top, bottom = 174, 936
    ph = (bottom - top - 2 * g) // 3
    for i, (tag, head, details, picture) in enumerate(STORIES):
        col, row = i % 2, i // 2
        x0 = m + col * (pw + g)
        y0 = top + row * (ph + g)
        draw_panel(d, x0, y0, x0 + pw, y0 + ph, tag, head, details, picture)

    # timeline footer
    d.line([(24, 950), (SIZE - 24, 950)], fill=INK, width=2)
    tf4 = load(SANS_BOLD, 15)
    timeline = ("02:00 UTC  Akvan landfall, Gopalpur   \u2022   05:00 SYDNEY  raids begin"
                "   \u2022   15:00 TOKYO  Nikkei closes \u22125.06%")
    d.text((24, 960), timeline, font=tf4, fill=INK)
    timeline2 = ("FRIDAY  coalition strikes Hodeidah   \u2022   FRIDAY  Haiti toll announced"
                 "   \u2022   OVERNIGHT  Kyiv barrage begins")
    d.text((24, 982), timeline2, font=tf4, fill=INK)
    foot = "EVERY STORY DATED 20 NOVEMBER 2026  \u2022  SOURCES: AP, REUTERS, IMD, AFP, ABC"
    d.text(((SIZE - d.textlength(foot, font=tf4)) / 2, 1006), foot,
           font=tf4, fill=GREY)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, format="PNG")
    print("saved", out)


if __name__ == "__main__":
    main()
