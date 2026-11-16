"""FACT 016 - How many Earths fill the Sun's volume? (disc fill engine, 1 dot = 1,000 Earths)
Source: NASA NSSDCA Sun Fact Sheet: volume 1,412,000 x 10^12 km3 (Sun), 1.083 x 10^12 km3 (Earth),
ratio 1,304,000. Check: 1,412,000 / 1.083 = 1,303,786; (695,700 / 6,371)^3 = 1,302,000. By volume, not
packed spheres, so the question says "fill the Sun's volume"."""
import sys
import numpy as np
from PIL import Image, ImageDraw
from lib import *

DUR = 14.0
RATIO = 1304000
assert round(1412000 / 1.083, -3) == RATIO and abs((695700 / 6371) ** 3 / RATIO - 1) < 0.01
N = RATIO // 1000
P, CX, CY = 17, 540, 1000
T1 = 9.0
T_REV = T1 + 0.15
ORANGE = (255, 170, 60)
g = [(ix * P + P / 2, iy * P + P / 2) for ix in range(-30, 30) for iy in range(-30, 30)]
g.sort(key=lambda p: p[0] ** 2 + p[1] ** 2)
CELLS = sorted(g[:N], key=lambda p: (-p[1], p[0]))        # exactly N dots in a disc, filled bottom up
assert len(CELLS) == 1304


def n_at(t):
    return N * ramp(t, -0.15, T1) ** 1.4


HOOK, _ = text_layer([('FACT 016', SEMI, 30, MUTED), ('How many Earths', XB, 84, WHITE),
                      ("fill the Sun's volume?", XB, 84, WHITE), ('Guess before it stops.', SEMI, 40, GOLD)], 232)
REVEAL, _ = text_layer([('FACT 016', SEMI, 30, MUTED), ('1.3 million', BLACK, 128, GOLD),
                        ('Earths, by volume', XB, 60, WHITE),
                        ('Sun / Earth volume = 1,304,000 (NASA)', MED, 32, MUTED)], 232)

BASE = Image.new('RGBA', (W, H), (0, 0, 0, 0))
_bd = ImageDraw.Draw(BASE)
for x, y in CELLS:
    _bd.ellipse([CX + x - 6, CY + y - 6, CX + x + 6, CY + y + 6], fill=(22, 27, 40, 255))


def sim(t):
    lay, d = layer()
    n = n_at(t)
    k = int(n)
    for x, y in CELLS[:k]:
        d.ellipse([CX + x - 6, CY + y - 6, CX + x + 6, CY + y + 6], fill=ORANGE + (255,))
    shown = RATIO if t >= T1 else int(n * 1000) // 100 * 100
    d.text((W / 2, 1410), f'{shown:,}', font=font(BLACK, 84), fill=(GOLD if t >= T1 else WHITE) + (255,), anchor='mm')
    return lay


def render_frame(t):
    img = new_frame()
    img.alpha_composite(BASE)
    d = ImageDraw.Draw(img)
    d.text((W / 2, 624), 'THE SUN', font=font(SEMI, 26), fill=MUTED, anchor='mm')
    d.ellipse([368, 1468, 380, 1480], fill=(64, 150, 255))
    d.text((392, 1474), '1 dot = 1,000 Earths', font=font(MED, 28), fill=MUTED, anchor='lm')
    loop_sim(img, sim, t, DUR)
    loop_text(img, HOOK, REVEAL, t, T_REV)
    return img


def audio(au):
    t = 0.0
    while t < T1:
        x = t / T1
        au.tick(t, freq=500 + 1100 * x, vol=0.14, dur=0.05)
        t += 0.11 - 0.06 * x
    au.thunk(T1, freq=80, vol=0.6, dur=0.35)
    au.ding(T_REV)
    au.whoosh(13.05, dur=0.8, vol=0.2, up=False)


if __name__ == '__main__':
    run(render_frame, DUR, 'fact016_sunvolume', audio, sys.argv)
