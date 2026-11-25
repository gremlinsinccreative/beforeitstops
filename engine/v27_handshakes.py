"""v6 FACT 027 30 people, everyone shakes hands once. How many handshakes? 13 s, + next-up teaser (odd number).
Non-human-scale arm of the topic test; "most people say X" counting puzzle like #018 ("204, not 64"): most say 900.
Pure arithmetic, no outside figure: 30 x 29 / 2 = 435 (each handshake has two people, so 30 x 29 counts each twice).
Milestones: person 1 shakes 29 hands; after the first 15 people, 29*15 - 15*14/2 = 330 handshakes are done.
Twist: 100 people -> 100 x 99 / 2 = 4,950.
Hero: 30 dots in a ring; a line appears for every handshake. One number: the count."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from scipy.interpolate import PchipInterpolator
from lib import *
from lib2 import big_text
from brand2 import *

DUR, T_STOP, T_TWIST = 13.0, 9.6, 11.0
N = 30
TOTAL = N * (N - 1) // 2
assert TOTAL == 435 and N * N == 900 and N * (N - 1) == 870
assert 29 * 15 - 15 * 14 // 2 == 330
assert 100 * 99 // 2 == 4950
PAIRS = [(i, j) for i in range(N) for j in range(i + 1, N)]          # in order: person 0 first, then 1, ...
assert len(PAIRS) == TOTAL and sum(1 for p in PAIRS if p[0] == 0) == 29 and sum(1 for p in PAIRS if p[0] < 15) == 330

KEYS = [(0, 0.0), (1.4, 10.0), (2.9, 27.0), (3.6, 31.0), (5.6, 318.0), (6.4, 336.0), (8.6, 425.0), (9.6, 435.0)]
_P = PchipInterpolator([k[0] for k in KEYS], [k[1] for k in KEYS])


def count(t):
    return float(_P(min(max(t, 0.0), T_STOP)))


def t_at(v):
    lo, hi = 0.0, T_STOP
    for _ in range(40):
        md = (lo + hi) / 2
        lo, hi = (lo, md) if count(md) >= v else (md, hi)
    return hi


MILESTONES = [(29, t_at(29), ['Person 1:', '29 handshakes']),
              (330, t_at(330), ['Half the people done:', '330 already'])]
BR = Brand2(27, ['30 people. Everyone shakes', 'hands once. How many?'], '30 people all shake hands. How many handshakes?',
            [('A', '900'), ('B', '870'), ('C', '435')],
            [('435, not 900', BLACK, 110, GOLD), ('30 × 29 ÷ 2: every handshake has two people', BOLD, 36, WHITE)],
            [('With 100 people:', BOLD, 48, WHITE), ('4,950 handshakes', BLACK, 74, GOLD)], T_STOP, T_TWIST, DUR,
            sub='Wait for the last handshake', cta='Comment your letter', q_size=76,
            next_line='Next: FACT 028 · Drive to the Sun: how long?')
RESULT = {'A': 'out', 'B': 'out', 'C': 'win'}

CX, CY, R = 540, 1085, 295
PTS = [(CX + R * math.cos(-math.pi / 2 + 2 * math.pi * k / N), CY + R * math.sin(-math.pi / 2 + 2 * math.pi * k / N)) for k in range(N)]


def background():
    ys = np.linspace(0, 1, H)[:, None, None]
    top, bot = np.array((8, 14, 22)), np.array((14, 34, 40))
    arr = np.broadcast_to(top * (1 - ys) + bot * ys, (H, W, 3)).astype(np.uint8)
    return Image.fromarray(np.ascontiguousarray(arr), 'RGB').convert('RGBA')


BG_IMG = background()


def frame_core(t):
    cnow = count(t)
    n = TOTAL if t >= T_STOP else int(cnow)
    img = BG_IMG.copy()
    hc = Canvas()
    for k, (i, j) in enumerate(PAIRS[:n]):
        fresh = 1.0 if k >= n - 6 else 0.0
        hc.line([PTS[i], PTS[j]], fill=(255, 214, 102, 120 + int(110 * fresh)), width=2.2 + 1.5 * fresh)
    if 0 < n < TOTAL:                                   # the line being drawn now grows from its first person
        i, j = PAIRS[n]
        f = cnow - n
        x = PTS[i][0] + (PTS[j][0] - PTS[i][0]) * f
        y = PTS[i][1] + (PTS[j][1] - PTS[i][1]) * f
        hc.line([PTS[i], (x, y)], fill=(255, 236, 170, 240), width=3.5)
    active = PAIRS[min(n, TOTAL - 1)][0] if t < T_STOP else -1
    for k, (x, y) in enumerate(PTS):
        hc.circle(x, y, 17 if k == active else 13, fill=(255, 246, 220, 255) if k == active else (200, 225, 235, 255))
    comp(img, glow(hc.down(), radius=14, strength=0.5), 1 - 0.7 * ease_io(ramp(t, T_TWIST - 0.1, T_TWIST + 0.3)))   # dim under the twist
    for vv, tp, txt in MILESTONES:
        al = ease_io(ramp(t, tp - 0.2, tp + 0.05)) * (1 - ease_io(ramp(t, tp + 0.9, tp + 1.15)))
        if al > 0.02 and t < T_STOP:
            lb, _ = big_text([(txt[0], XB, 54, WHITE), (txt[1], BOLD, 42, GOLD)], 0)
            sub = lb.crop(lb.getbbox())
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            lay.alpha_composite(sub, ((W - sub.width) // 2, 545))
            comp(img, lay, al)
    ca = 1 - ramp(t, T_TWIST - 0.1, T_TWIST + 0.2)
    if ca > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(lay)
        val = f'{n:,}'
        dd.ellipse([CX - 125, CY - 85, CX + 125, CY + 85], fill=(6, 12, 20, 200))
        dd.text((CX + 4, CY + 4), val, font=font(BLACK, 110), fill=(0, 0, 0, 150), anchor='mm')
        dd.text((CX, CY), val, font=font(BLACK, 110), fill=GOLD if t >= T_STOP else WHITE, anchor='mm')
        comp(img, lay, ca)
    return BR.overlay(img, t, RESULT)


render_frame = looped(frame_core, DUR, xf=0.5)


def music(mu):
    from brand import drum_track, ding, drop_hit
    lvl = lambda tt: count(tt) / TOTAL
    mu.bed(0, T_STOP, cutoff=lambda tt: 0.05 + 0.06 * lvl(tt), vol=lambda tt: (0.015 + 0.04 * lvl(tt)) * clamp(tt / 0.05), seed=27)
    drum_track(mu, T_STOP - 0.32, lvl, bpm0=96, bpm1=150, key=0, roll=1.4)
    for vv, tp, _ in MILESTONES:
        ding(mu, tp, key=0, vol=0.15, pan=0.4 if vv == 29 else -0.4)
    mu.silence(T_STOP - 0.32, T_STOP)
    drop_hit(mu, T_STOP, key=0)
    mu.bed(T_STOP + 0.4, DUR, cutoff=lambda tt: 0.02, vol=lambda tt: 0.01, seed=13)
    mu.bell(T_TWIST, 659.25, 0.16, -0.3); mu.bell(T_TWIST + 0.1, 987.77, 0.16, 0.3)


if __name__ == '__main__':
    main(render_frame, DUR, music, sys.argv)
