"""HELD 24 Nov (T&S: a deadly real Ebola outbreak in DR Congo is in the news; renumber before use). v6 FACT 023 1 zombie, 1 bite per hour: when are there 1 million? 13 s, + next-up teaser (odd number).
Non-human-scale arm of the topic test; Marketing's zombie-outbreak meme ride (21 Nov), presented as plain doubling
maths with the premise on screen (no disease names, no real numbers, no 'your city'; T&S 20 Nov item 2).
Every zombie bites one new person every hour -> the count doubles each hour: 2^20 = 1,048,576 after 20 hours.
Twist: 2^33 = 8.6 billion > everyone alive (more than 8 billion, UN), 2^32 = 4.3 billion is not -> hour 33.
Hero: the outbreak's area, which doubles every hour (radius grows by sqrt 2), spreading over a sleeping town."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from scipy.interpolate import PchipInterpolator
from lib import *
from lib2 import big_text
from brand2 import *

DUR, T_STOP, T_TWIST = 13.0, 9.6, 11.0
H_END = 20
assert 2 ** 20 == 1_048_576 and 2 ** 19 < 1_000_000 < 2 ** 20      # 1 million passed in hour 20
assert 2 ** 32 < 8_000_000_000 < 8_300_000_000 < 2 ** 33            # everyone (8.0-8.3 billion): hour 33
assert 2 ** 10 == 1024 and 2 ** 15 == 32_768

KEYS = [(0, 0.0), (1.4, 3.0), (2.9, 9.6), (3.6, 10.1), (5.6, 14.6), (6.4, 15.1), (8.6, 19.3), (9.6, 20.0)]
_P = PchipInterpolator([k[0] for k in KEYS], [k[1] for k in KEYS])


def hours(t):
    return float(_P(min(max(t, 0.0), T_STOP)))


def t_at(v):
    lo, hi = 0.0, T_STOP
    for _ in range(40):
        md = (lo + hi) / 2
        lo, hi = (lo, md) if hours(md) >= v else (md, hi)
    return hi


MILESTONES = [(10, t_at(10), ['Hour 10: 1,024', 'still one street']),
              (15, t_at(15), ['Hour 15: 32,768', 'a small town'])]
BR = Brand2(23, ['1 zombie. 1 bite an hour.', 'When are there', '1 million?'], '1 bite an hour: when 1 million zombies?',
            [('A', '20 hours'), ('B', '20 days'), ('C', '2 years')],
            [('20 hours', BLACK, 120, GOLD), ('Doubled 20 times = 1,048,576', BOLD, 40, WHITE)],
            [('Everyone on Earth?', BOLD, 48, WHITE), ('Hour 33', BLACK, 80, GOLD)], T_STOP, T_TWIST, DUR,
            sub='Wait for the million', cta='Comment your letter', q_size=78,
            next_line='Next: FACT 024 · Your life as one day')
RESULT = {'A': 'win', 'B': 'out', 'C': 'out'}

CX, CY, RMAX = 540, 975, 385
rng = np.random.default_rng(23)
HOUSES = []
for _ in range(360):
    x, y = rng.uniform(40, W - 40), rng.uniform(560, 1380)
    HOUSES.append((x, y, rng.uniform(10, 20), rng.uniform(0, 1)))


def radius(h):
    return RMAX * math.sqrt(2 ** h / 2 ** H_END)


def background():
    ys = np.linspace(0, 1, H)[:, None, None]
    top, bot = np.array((8, 10, 18)), np.array((14, 20, 26))
    arr = np.broadcast_to(top * (1 - ys) + bot * ys, (H, W, 3)).astype(np.uint8)
    return Image.fromarray(np.ascontiguousarray(arr), 'RGB').convert('RGBA')


BG_IMG = background()


def frame_core(t):
    h = hours(t)
    r = radius(h)
    img = BG_IMG.copy()
    c = Canvas()
    for x, y, s, lit in HOUSES:
        inside = math.hypot(x - CX, y - CY) < r
        col = (60, 150, 80, 255) if inside else ((70, 74, 92, 255) if lit < 0.8 else (200, 170, 90, 230))
        c.rect([x - s / 2, y - s / 2, x + s / 2, y + s / 2], fill=col, radius=2)
    img.alpha_composite(c.down())
    hc = Canvas()
    rr = max(r, 5)
    hc.circle(CX, CY, rr, fill=(110, 230, 120, 70))
    hc.circle(CX, CY, rr, outline=(150, 255, 150, 230), width=4)
    hc.circle(CX, CY, 5, fill=(170, 255, 160, 255))
    img.alpha_composite(glow(hc.down(), radius=20, strength=0.5))
    for vv, tp, txt in MILESTONES:
        al = ease_io(ramp(t, tp - 0.2, tp + 0.05)) * (1 - ease_io(ramp(t, tp + 0.9, tp + 1.15)))
        if al > 0.02 and t < T_STOP:
            lb, _ = big_text([(txt[0], XB, 56, WHITE), (txt[1], BOLD, 40, GOLD)], 0)
            sub = lb.crop(lb.getbbox())
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            lay.alpha_composite(sub, (70, 1150) if vv == 10 else (W - 70 - sub.width, 1150))
            comp(img, lay, al)
    ca = 1 - ramp(t, T_TWIST - 0.1, T_TWIST + 0.2)
    if ca > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(lay)
        n = 2 ** H_END if t >= T_STOP else int(2 ** math.floor(h + 1e-9))
        val = f'{n:,}'
        dd.text((W / 2 + 4, 1404), val, font=font(BLACK, 84), fill=(0, 0, 0, 140), anchor='mm')
        dd.text((W / 2, 1400), val, font=font(BLACK, 84), fill=GOLD if t >= T_STOP else WHITE, anchor='mm')
        comp(img, lay, ca)
    return BR.overlay(img, t, RESULT)


render_frame = looped(frame_core, DUR, xf=0.5)


def music(mu):
    from brand import drum_track, ding, drop_hit
    lvl = lambda tt: hours(tt) / H_END
    mu.bed(0, T_STOP, cutoff=lambda tt: 0.04 + 0.07 * lvl(tt), vol=lambda tt: (0.015 + 0.05 * lvl(tt) ** 1.5) * clamp(tt / 0.05), seed=23)
    drum_track(mu, T_STOP - 0.32, lvl, bpm0=96, bpm1=150, key=-5, roll=1.4)
    for vv, tp, _ in MILESTONES:
        ding(mu, tp, key=-5, vol=0.15, pan=-0.4 if vv == 10 else 0.4)
    mu.silence(T_STOP - 0.32, T_STOP)
    drop_hit(mu, T_STOP, key=-5)
    mu.bed(T_STOP + 0.4, DUR, cutoff=lambda tt: 0.02, vol=lambda tt: 0.01, seed=8)
    mu.bell(T_TWIST, 659.25 * 2 ** (-5 / 12), 0.16, -0.3); mu.bell(T_TWIST + 0.1, 987.77 * 2 ** (-5 / 12), 0.16, 0.3)


if __name__ == '__main__':
    main(render_frame, DUR, music, sys.argv)
