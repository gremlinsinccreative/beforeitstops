"""FACT 014 - You are sitting still. How far did you just move? (real-time odometer engine)
Source: Earth's mean orbital velocity 29.78 km/s (NASA NSSDCA Earth Fact Sheet; min 29.29, max 30.29).
Arithmetic: 29.78 km/s x 9 s = 268 km (264 to 273 km across the year). The counter runs in real time."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from lib import *

DUR = 14.0
V, T1 = 29.78, 9.0
KM = V * T1
assert round(KM) == 268 and round(29.29 * 9) == 264 and round(30.29 * 9) == 273
T_REV = T1 + 0.15
EX, EY, ER = 330, 800, 46
TY, PXKM = 960, 12.0                          # tape y, pixels per km
rng = np.random.default_rng(14)
STARS = [(float(rng.uniform(0, W)), float(rng.uniform(640, 900)), float(rng.uniform(0.25, 1.0))) for _ in range(70)]


def km_at(t):
    return V * clamp(t, 0, T1)


HOOK, _ = text_layer([('FACT 014', SEMI, 30, MUTED), ("You're sitting still.", XB, 84, WHITE),
                      ('How far did you just move?', XB, 72, WHITE), ('Guess before it stops.', SEMI, 40, GOLD)], 232)
REVEAL, _ = text_layer([('FACT 014', SEMI, 30, MUTED), ('268 km', BLACK, 128, GOLD),
                        ('in 9 seconds, around the Sun', XB, 60, WHITE),
                        ("Earth's orbital speed: 29.78 km/s (NASA)", MED, 32, MUTED)], 232)


def sim(t):
    lay, d = layer()
    km = km_at(t)
    moving = t < T1
    off = V * min(t, T1)
    for sx, sy, z in STARS:
        x = (sx - off * PXKM * z * 0.6) % W
        ln = 46 * z if moving else 3
        if 710 < sy < 860 and EX - 170 < x < EX + 120:
            continue
        d.line([(x, sy), (x + ln, sy)], fill=WHITE + (int(70 + 150 * z),), width=3)
    for k in range(int(km // 10) * 10 - 40, int(km) + 80, 10):   # scrolling distance tape
        if k < 0:
            continue
        x = EX + (k - km) * PXKM
        if not 100 <= x <= 980:
            continue
        big = k % 50 == 0
        d.line([(x, TY), (x, TY + (30 if big else 16))], fill=(WHITE if big else MUTED) + (255,), width=3)
        if big:
            d.text((x, TY + 56), f'{k} km', font=font(MED, 26), fill=WHITE + (255,), anchor='mm')
    d.polygon([(EX, TY - 6), (EX - 12, TY - 26), (EX + 12, TY - 26)], fill=GOLD + (255,))
    d.text((W / 2, 1160), f'{km:,.0f} km', font=font(BLACK, 170), fill=(WHITE if t < T1 else GOLD) + (255,), anchor='mm')
    d.text((W / 2, 1290), f'{clamp(t, 0, T1):.1f} seconds', font=font(BOLD, 54), fill=WHITE + (255,), anchor='mm')
    d.text((W / 2, 1360), 'DISTANCE TRAVELLED AROUND THE SUN', font=font(SEMI, 26), fill=MUTED + (255,), anchor='mm')
    return lay


def render_frame(t):
    img = new_frame()
    d = ImageDraw.Draw(img)
    d.line([(100, TY), (980, TY)], fill=MUTED, width=3)
    d.ellipse([EX - ER, EY - ER, EX + ER, EY + ER], fill=(40, 120, 220))
    for cx, cy, r in ((-16, -14, 17), (14, 4, 14), (-6, 22, 11)):
        d.ellipse([EX + cx - r, EY + cy - r, EX + cx + r, EY + cy + r], fill=(70, 170, 110))
    d.text((EX, EY - ER - 30), 'YOU ARE HERE', font=font(SEMI, 24), fill=MUTED, anchor='mm')
    loop_sim(img, sim, t, DUR)
    loop_text(img, HOOK, REVEAL, t, T_REV)
    return img


def audio(au):
    for k in range(10, int(KM) + 1, 10):
        au.tick(k / V, freq=(520 if k % 50 else 780) * 2 ** (k / 600), vol=0.2 if k % 50 else 0.3, dur=0.08)
    au.whoosh(0.0, dur=1.2, vol=0.12, up=True)
    au.thunk(T1, freq=80, vol=0.6, dur=0.35)
    au.ding(T_REV)
    au.whoosh(13.05, dur=0.8, vol=0.2, up=False)


if __name__ == '__main__':
    run(render_frame, DUR, 'fact014_orbit', audio, sys.argv)
