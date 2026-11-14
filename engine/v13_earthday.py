"""FACT 013 - Earth's history as a single day. When do humans arrive? (clock engine)
Sources: age of the Earth 4.54 billion years (USGS, "Age of the Earth"); oldest Homo sapiens fossils
315 +/- 34 thousand years (Hublin et al., Nature 546, 2017, Jebel Irhoud).
Arithmetic: 315,000 / 4,540,000,000 x 86,400 s = 5.99 s before midnight -> 23:59:54.
The +/- 34 thousand years moves it between 5.3 and 6.6 s; "about 6 seconds" holds across the range."""
import sys, math
from PIL import Image, ImageDraw
from lib import *

DUR = 14.0
EARTH_Y, SAPIENS_Y = 4.54e9, 315_000
BEFORE = SAPIENS_Y / EARTH_Y * 86400
assert abs(BEFORE - 5.995) < 0.01 and 5.3 < 281_000 / EARTH_Y * 86400 and 349_000 / EARTH_Y * 86400 < 6.7
ARRIVE = 86400 - BEFORE                       # seconds after 00:00
T0, T1 = -0.3, 9.0
T_REV = T1 + 0.15
CX, CY, R, RW = W // 2, 1030, 300, 44
DARK = (26, 32, 48)


def tod(t):
    return ARRIVE * (1 - (1 - ramp(t, T0, T1)) ** 3)


HOOK, _ = text_layer([('FACT 013', SEMI, 30, MUTED), ("Earth's history in one day.", XB, 76, WHITE),
                      ('When do humans arrive?', XB, 76, WHITE), ('Guess before it stops.', SEMI, 40, GOLD)], 232)
REVEAL, _ = text_layer([('FACT 013', SEMI, 30, MUTED), ('23:59:54', BLACK, 128, GOLD),
                        ('6 seconds before midnight', XB, 64, WHITE),
                        ('Earth 4.54 billion years (USGS). Us about 315,000 (Nature, 2017)', MED, 28, MUTED)], 232)


def sim(t):
    lay, d = layer()
    s = tod(t)
    ang = 360 * s / 86400
    if ang > 0.3:
        d.arc([CX - R, CY - R, CX + R, CY + R], -90, -90 + ang, fill=BLUE + (255,), width=RW)
    a = math.radians(-90 + ang)
    hx, hy = CX + (R - RW / 2) * math.cos(a), CY + (R - RW / 2) * math.sin(a)
    done = ramp(t, T0, T1) >= 1
    d.ellipse([hx - 30, hy - 30, hx + 30, hy + 30], fill=(GOLD if done else WHITE) + (255,))
    si = int(s)
    d.text((CX, CY - 8), f'{si // 3600:02d}:{si // 60 % 60:02d}:{si % 60:02d}', font=font(BLACK, 96),
           fill=(GOLD if done else WHITE) + (255,), anchor='mm')
    d.text((CX, CY + 70), 'TIME OF DAY', font=font(SEMI, 26), fill=MUTED + (255,), anchor='mm')
    d.text((CX, CY - 90), f'{s / 86400 * EARTH_Y / 1e9:.2f} billion years in', font=font(MED, 28),
           fill=MUTED + (255,), anchor='mm')
    return lay


def render_frame(t):
    img = new_frame()
    d = ImageDraw.Draw(img)
    d.ellipse([CX - R, CY - R, CX + R, CY + R], fill=DARK)
    d.ellipse([CX - R + RW, CY - R + RW, CX + R - RW, CY + R - RW], fill=BG)
    for h in range(24):
        a = math.radians(-90 + h * 15)
        big = h % 6 == 0
        r0, r1 = R + 12, R + (34 if big else 22)
        d.line([(CX + r0 * math.cos(a), CY + r0 * math.sin(a)), (CX + r1 * math.cos(a), CY + r1 * math.sin(a))],
               fill=WHITE if big else MUTED, width=3)
        if big:
            d.text((CX + (R + 68) * math.cos(a), CY + (R + 68) * math.sin(a)), f'{h:02d}:00' if h else 'midnight',
                   font=font(MED, 26), fill=WHITE, anchor='mm')
    loop_sim(img, sim, t, DUR)
    loop_text(img, HOOK, REVEAL, t, T_REV)
    return img


def audio(au):
    last = 0
    for i in range(int((T1 - T0) * 200)):
        t = T0 + i / 200
        h = int(tod(t) // 3600)
        if h > last:
            last = h
            au.tick(max(t, 0), freq=330 * 2 ** (h / 12), vol=0.22, dur=0.09)
    for k in range(1, 9):                     # the last minute crawls: soft ticks
        au.tick(5.0 + k * 0.45, freq=1320, vol=0.1, dur=0.05)
    au.thunk(T1, freq=80, vol=0.6, dur=0.35)
    au.ding(T_REV)
    au.whoosh(13.05, dur=0.8, vol=0.2, up=False)


if __name__ == '__main__':
    run(render_frame, DUR, 'fact013_earthday', audio, sys.argv)
