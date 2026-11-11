"""FACT 006 - Everyone ever born: how many are alive? (drop engine)
Source: Population Reference Bureau, 2022: ~117 billion ever born, ~8 billion alive (nearly 7%)."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from lib import *

DUR = 14.0
PITCH, R = 88, 40
X0 = (W - 10 * PITCH) // 2
YB = 1470
YT = YB - 10 * PITCH
G = 5200.0
GREY, DIM = (150, 160, 182), (58, 66, 86)
T_REV = 8.5

rng = np.random.default_rng(5)
slots = []
for r in range(10):
    for c in rng.permutation(10):
        slots.append((int(c), r))
REL = [-0.32 + i * 0.077 for i in range(100)]
ALIVE = list(range(93, 100))
PENTA = [392.0, 440.0, 523.3, 587.3, 659.3, 784.0, 880.0, 1046.5, 1174.7, 1318.5]


def sprite(color, rad):
    S = 4
    n = (rad * 2 + 4) * S
    im = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([2 * S, 2 * S, n - 2 * S, n - 2 * S], fill=color + (255,))
    hl = tuple(min(255, int(c + (255 - c) * 0.38)) for c in color)
    d.ellipse([n * 0.26, n * 0.2, n * 0.56, n * 0.46], fill=hl + (150,))
    return im.resize((n // S, n // S), Image.LANCZOS)


def mix(a, b, x):
    return tuple(int(a[i] + (b[i] - a[i]) * x) for i in range(3))


SPR = {}


def get_sprite(kind, step, rad=R):
    k = (kind, step, rad)
    if k not in SPR:
        base = GREY
        col = mix(base, GOLD if kind == 'gold' else DIM, step / 8)
        SPR[k] = sprite(col, rad)
    return SPR[k]


def ball_pos(i, t):
    """Return (x, y, scale) or None if not yet released."""
    c, r = slots[i]
    x = X0 + c * PITCH + PITCH // 2
    y_rest = YB - r * PITCH - PITCH // 2
    y0 = YT - 24
    tau = t - REL[i]
    if tau < 0:
        return None
    t_fall = math.sqrt(2 * (y_rest - y0) / G)
    if tau < t_fall:
        return x, y0 + 0.5 * G * tau * tau, clamp(tau / 0.08, 0.3, 1)
    u = tau - t_fall
    return x, y_rest - 20 * abs(math.sin(u * 17)) * math.exp(-u * 9), 1.0


def land_time(i):
    c, r = slots[i]
    return REL[i] + math.sqrt(2 * ((YB - r * PITCH - PITCH // 2) - (YT - 24)) / G)


HOOK, _ = text_layer([('FACT 006', SEMI, 30, MUTED),
                      ('Everyone ever born:', XB, 84, WHITE),
                      ('how many are alive?', XB, 84, WHITE),
                      ('Guess before it stops.', SEMI, 40, GOLD)], 232)
REVEAL, _ = text_layer([('FACT 006', SEMI, 30, MUTED),
                        ('About 7 in 100', BLACK, 112, GOLD),
                        ('8 billion alive today', XB, 58, WHITE),
                        ('117 billion ever born', XB, 58, MUTED)], 232)
SOURCE, _ = text_layer([('Source: Population Reference Bureau (2022)', MED, 28, MUTED)], YB + 34)


def draw_ball(img, x, y, kind, step, scale=1.0):
    rad = R if abs(scale - 1) < 0.01 else max(6, int(R * scale))
    sp = get_sprite(kind, step, rad)
    img.alpha_composite(sp, (int(x - sp.width / 2), int(y - sp.height / 2)))


def render_frame(t):
    img = new_frame()
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([X0 - 14, YT - 14, X0 + 10 * PITCH + 14, YB + 14], radius=30,
                        outline=(44, 54, 78), width=4, fill=(14, 17, 26))
    for i in range(100):
        p = ball_pos(i, t)
        if p is None:
            continue
        x, y, sc = p
        kind, step = 'dim', 0
        if t >= T_REV:
            if i in ALIVE:
                k = ALIVE.index(i)
                a = ramp(t, T_REV + k * 0.13, T_REV + k * 0.13 + 0.18)
                kind, step = 'gold', int(round(8 * a))
                sc = 1 + 0.22 * math.sin(math.pi * a) if 0 < a < 1 else 1.0
            else:
                kind, step = 'dim', int(round(8 * ease_io(ramp(t, T_REV, T_REV + 0.6))))
        if t >= 12.95:                       # floor opens: everything drops out
            c, r = slots[i]
            u = t - 12.95 - 0.012 * c - 0.02 * r
            if u > 0:
                y += 0.5 * 13000 * u * u
            if y > H + 80:
                continue
        draw_ball(img, x, y, kind, step, sc)
    if t > 13.5:                             # next cycle's first balls (matches frame 0)
        for i in range(100):
            p = ball_pos(i, t - DUR)
            if p:
                draw_ball(img, p[0], p[1], 'dim', 0, p[2])
    rev_in = ease_io(ramp(t, T_REV + 0.15, T_REV + 0.5))
    comp(img, HOOK, (1 - rev_in) if t < 13 else ease_io(ramp(t, 13.5, 13.9)))
    comp(img, REVEAL, rev_in * (1 - ease_io(ramp(t, 13.0, 13.4))))
    comp(img, SOURCE, ease_io(ramp(t, T_REV + 1.2, T_REV + 1.6)) * (1 - ease_io(ramp(t, 12.9, 13.2))))
    return img


def audio(au):
    for i in range(100):
        au.tick(land_time(i), freq=PENTA[slots[i][1]], vol=0.2, dur=0.09)
    for k in range(7):
        au.ding(T_REV + k * 0.13, freqs=(1046.5 * (1 + 0.06 * k), 1568.0), vol=0.14, dur=0.5)
    au.ding(T_REV + 1.0)
    au.whoosh(12.9, dur=0.8, vol=0.22, up=False)
    for i in range(100):
        lt = land_time(i) + DUR
        if lt < DUR:
            au.tick(lt, freq=PENTA[slots[i][1]], vol=0.2, dur=0.09)


if __name__ == '__main__':
    run(render_frame, DUR, 'fact006_everborn', audio, sys.argv)
