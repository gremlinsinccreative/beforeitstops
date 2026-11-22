"""v6 FACT 021 Walk to the Moon nonstop. How long? 13 s, no teaser (the teaser A/B test restarts with the 23 Nov batch).
Source: NASA, science.nasa.gov/moon/facts (read 22 Nov 2026): "The Moon is an average of 238,855 miles
(384,400 kilometers) away." Premise stated on screen and in the caption: a steady 5 km/h, day and night.
384,400 km / 5 km/h = 76,880 h = 3,203 days = 8.77 years ("almost 9 years"). Twist: by car at 100 km/h, 160 days.
Hero: one small walker on a gold path that arcs from Earth (bottom left) to the Moon (top right). One number: time walked."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from scipy.interpolate import PchipInterpolator
from lib import *
from lib2 import big_text
from brand2 import *

DUR, T_STOP, T_TWIST = 13.0, 9.6, 11.0
KM, KMH, CAR = 384_400, 5, 100
HOURS = KM / KMH
YEARS = HOURS / 24 / 365.25
assert HOURS == 76_880 and round(HOURS / 24) == 3203 and round(YEARS, 2) == 8.77
assert round(KM / CAR / 24, 1) == 160.2                       # twist: 160 days by car
Y1, Y5 = 1.0, 5.0                                             # milestones (years)
assert round(Y1 * 365.25 * 24 * KMH / KM * 100) == 11         # after 1 year: 11% of the way
assert round(Y5 * 365.25 * 24 * KMH / KM * 100) == 57         # after 5 years: 57%

KEYS = [(0, 0.0), (1.4, 0.32), (2.8, 0.96), (3.5, 1.04), (5.6, 4.9), (6.4, 5.08), (8.6, 8.55), (9.6, YEARS)]
_P = PchipInterpolator([k[0] for k in KEYS], [k[1] for k in KEYS])


def years(t):
    return float(_P(min(max(t, 0.0), T_STOP)))


def t_at(yv):
    lo, hi = 0.0, T_STOP
    for _ in range(40):
        md = (lo + hi) / 2
        lo, hi = (lo, md) if years(md) >= yv else (md, hi)
    return hi


MILESTONES = [(Y1, t_at(Y1), ['1 year of walking', 'only 11% of the way']),
              (Y5, t_at(Y5), ['5 years', 'just past halfway'])]
BR = Brand2(21, ['Walk to the Moon', 'nonstop. How long?'], 'Walk to the Moon nonstop. How long?',
            [('A', '9 months'), ('B', '9 years'), ('C', '90 years')],
            [('Almost 9 years', BLACK, 112, GOLD), ('384,400 km at 5 km/h  ·  Source: NASA', BOLD, 38, WHITE)],
            [('By car at 100 km/h:', BOLD, 48, WHITE), ('160 days nonstop', BLACK, 64, GOLD)], T_STOP, T_TWIST, DUR,
            sub='Wait for the Moon', cta='Comment your letter', q_size=84)
RESULT = {'A': 'out', 'B': 'win', 'C': 'out'}

EX, EY, ER = 210, 1290, 120                    # Earth
MX, MY, MR = 860, 850, 74                      # Moon
CX, CY = 330, 780                              # bezier control: the path bows up-left, labels sit bottom-right
rng = np.random.default_rng(21)
STARS = [(rng.uniform(0, W), rng.uniform(80, 1460), rng.uniform(0.9, 2.3), rng.uniform(0, 6.28)) for _ in range(150)]


def _bez(u):
    x = (1 - u) ** 2 * (EX + 70) + 2 * (1 - u) * u * CX + u ** 2 * (MX - 60)
    y = (1 - u) ** 2 * (EY - 100) + 2 * (1 - u) * u * CY + u ** 2 * (MY + 30)
    return x, y


_U = np.linspace(0, 1, 2001)
_XY = np.array([_bez(v) for v in _U])
_S = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(_XY, axis=0).T))])
_S /= _S[-1]


def bez(f):
    """Point at fraction f of the route's length (distance walked is linear in time)."""
    return _bez(float(np.interp(f, _S, _U)))


PATH = [bez(f) for f in np.linspace(0, 1, 240)]


def background():
    ys = np.linspace(0, 1, H)[:, None, None]
    top, bot = np.array((6, 8, 22)), np.array((16, 14, 40))
    arr = np.broadcast_to(top * (1 - ys) + bot * ys, (H, W, 3)).astype(np.uint8)
    return Image.fromarray(np.ascontiguousarray(arr), 'RGB').convert('RGBA')


BG_IMG = background()


def earth(c):
    c.circle(EX, EY, ER + 10, fill=(60, 130, 255, 40))
    c.circle(EX, EY, ER, fill=(36, 92, 190, 255))
    for dx, dy, rx, ry in [(-40, -30, 46, 30), (30, 20, 40, 52), (-10, 60, 30, 18), (55, -60, 26, 16)]:
        c.ellipse([EX + dx - rx, EY + dy - ry, EX + dx + rx, EY + dy + ry], fill=(70, 160, 95, 255))
    c.ellipse([EX - 80, EY - 88, EX + 10, EY - 74], fill=(240, 244, 250, 200))


def moon(c, k):
    c.circle(MX, MY, MR, fill=(214, 214, 206, 255))
    for dx, dy, r in [(-22, -18, 14), (20, 10, 10), (-6, 30, 8), (30, -30, 7)]:
        c.circle(MX + dx, MY + dy, r, fill=(180, 180, 172, 255))


def walker(c, x, y, t, a=255):
    ph = math.sin(2 * math.pi * t * 1.8)
    col = (255, 236, 190, a)
    k = 1.5
    c.circle(x, y - 46 * k, 10 * k, fill=col)                                       # head
    c.line([(x, y - 36 * k), (x, y - 8 * k)], fill=col, width=6 * k)                 # body
    c.line([(x, y - 30 * k), (x + 14 * k * ph, y - 16 * k)], fill=col, width=5 * k)  # arms
    c.line([(x, y - 30 * k), (x - 14 * k * ph, y - 16 * k)], fill=col, width=5 * k)
    c.line([(x, y - 8 * k), (x + 13 * k * ph, y + 14 * k)], fill=col, width=6 * k)   # legs
    c.line([(x, y - 8 * k), (x - 13 * k * ph, y + 14 * k)], fill=col, width=6 * k)


def frame_core(t):
    yv = years(t)
    u = clamp(yv / YEARS)
    img = BG_IMG.copy()
    c = Canvas()
    for sx, sy, sr, ph in STARS:
        c.circle(sx, sy, sr, fill=(255, 255, 255, int(160 * (0.75 + 0.25 * math.sin(ph + t * 0.6)))))
    earth(c)
    # the whole route, faint and dotted
    for i in range(0, len(PATH), 6):
        px, py = PATH[i]
        c.circle(px, py, 3, fill=(180, 190, 230, 70))
    img.alpha_composite(c.down())
    # hero: the walked part of the route in gold + the walker + the Moon (glow only here)
    hc = Canvas()
    n = max(2, int(u * (len(PATH) - 1)) + 1)
    hc.line(PATH[:n], fill=(255, 204, 51, 255), width=7)
    moon(hc, u)
    wx, wy = bez(u)
    walker(hc, wx, wy - 4, t)
    img.alpha_composite(glow(hc.down(), radius=22, strength=0.5))
    # milestone labels, bottom right (away from the path)
    for yy, tp, txt in MILESTONES:
        al = ease_io(ramp(t, tp - 0.2, tp + 0.05)) * (1 - ease_io(ramp(t, tp + 0.9, tp + 1.15)))
        if al > 0.02 and t < T_STOP:
            lb, _ = big_text([(txt[0], XB, 56, WHITE), (txt[1], BOLD, 40, GOLD)], 0)
            sub = lb.crop(lb.getbbox())
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            lay.alpha_composite(sub, (W - 70 - sub.width, 1000))
            comp(img, lay, al)
    ca = 1 - ramp(t, T_TWIST - 0.1, T_TWIST + 0.2)
    if ca > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(lay)
        if t >= T_STOP:
            val = '8.8 years'
        elif yv < 1:
            val = f'{yv * 365.25:.0f} days'
        else:
            val = f'{yv:.1f} years'
        x0 = W / 2 + 120
        dd.text((x0 + 4, 1324), val, font=font(BLACK, 100), fill=(0, 0, 0, 120), anchor='mm')
        dd.text((x0, 1320), val, font=font(BLACK, 100), fill=GOLD if t >= T_STOP else WHITE, anchor='mm')
        comp(img, lay, ca)
    return BR.overlay(img, t, RESULT)


render_frame = looped(frame_core, DUR, xf=0.5)


def music(mu):
    from brand import drum_track, ding, drop_hit
    lvl = lambda tt: years(tt) / YEARS
    mu.bed(0, T_STOP, cutoff=lambda tt: 0.05 + 0.06 * lvl(tt), vol=lambda tt: (0.015 + 0.04 * lvl(tt)) * clamp(tt / 0.05), seed=21)
    drum_track(mu, T_STOP - 0.32, lvl, bpm0=96, bpm1=150, key=0, roll=1.4)
    for yy, tp, _ in MILESTONES:
        ding(mu, tp, key=0, vol=0.15, pan=-0.4 if yy == Y1 else 0.4)
    mu.silence(T_STOP - 0.32, T_STOP)
    drop_hit(mu, T_STOP, key=0)
    mu.bed(T_STOP + 0.4, DUR, cutoff=lambda tt: 0.02, vol=lambda tt: 0.01, seed=6)
    mu.bell(T_TWIST, 659.25, 0.16, -0.3); mu.bell(T_TWIST + 0.1, 987.77, 0.16, 0.3)


if __name__ == '__main__':
    main(render_frame, DUR, music, sys.argv)
