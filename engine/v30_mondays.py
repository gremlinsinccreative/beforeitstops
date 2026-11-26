"""v6 FACT 030 Live to 80: how many Mondays do you get? 13 s, no teaser (even number).
Human-scale time arm of the topic test. Pure arithmetic on a premise stated on screen (live to 80); no life-expectancy
or health claim. Gregorian average year 365.25 days -> 80 x 365.25 / 7 = 4,174.3 -> 4,174 Mondays.
Milestones: age 18 -> 939 Mondays; age 40 -> 2,087. Twist: 4,174 days of Mondays / 365.25 = 11.4 years.
Hero: a life grid, one row per year (52 weeks) plus a last row of 14, so exactly 4,174 cells; each cell is one Monday
and fills gold as the count rises. One number: Mondays so far."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from scipy.interpolate import PchipInterpolator
from lib import *
from lib2 import big_text
from brand2 import *

DUR, T_STOP, T_TWIST = 13.0, 9.6, 11.0
LIFE, YEAR_D = 80, 365.25
TOTAL = int(LIFE * YEAR_D / 7)
assert TOTAL == 4174 and LIFE * 52 + 14 == TOTAL
M18, M40 = round(18 * YEAR_D / 7), round(40 * YEAR_D / 7)
assert M18 == 939 and M40 == 2087
assert round(TOTAL / YEAR_D, 1) == 11.4

KEYS = [(0, 0.0), (1.4, 130.0), (3.1, 880.0), (3.8, 975.0), (5.9, 2030.0), (6.6, 2140.0), (8.7, 4080.0), (9.6, float(TOTAL))]
_P = PchipInterpolator([k[0] for k in KEYS], [k[1] for k in KEYS])


def mondays(t):
    return float(_P(min(max(t, 0.0), T_STOP)))


def t_at(v):
    lo, hi = 0.0, T_STOP
    for _ in range(40):
        md = (lo + hi) / 2
        lo, hi = (lo, md) if mondays(md) >= v else (md, hi)
    return hi


MILESTONES = [(M18, t_at(M18), ['Age 18', '939 Mondays gone']),
              (M40, t_at(M40), ['Age 40', 'half of them used'])]
assert M40 * 2 >= TOTAL - 1
BR = Brand2(30, ['Live to 80: how many', 'Mondays do you get?'], 'Live to 80: how many Mondays do you get?',
            [('A', '40,000'), ('B', '400'), ('C', '4,000')],
            [('4,174 Mondays', BLACK, 104, GOLD), ('80 years × 365.25 days ÷ 7', BOLD, 38, WHITE)],
            [('All your Mondays together:', BOLD, 48, WHITE), ('11.4 years', BLACK, 80, GOLD)], T_STOP, T_TWIST, DUR,
            sub='Wait for the last Monday', cta='Comment your letter', q_size=76)
RESULT = {'A': 'out', 'B': 'out', 'C': 'win'}

COLS, PX, PY_ = 52, 13.0, 8.0
GX = (W - COLS * PX) / 2 + 20
GY = 662
ROWS = LIFE + 1


def cell_xy(i):
    r, c = divmod(i, COLS)
    return GX + c * PX, GY + r * PY_


def grid(fill):
    c = Canvas()
    for i in range(TOTAL):
        x, y = cell_xy(i)
        c.rect([x, y, x + PX - 2.6, y + PY_ - 2.4], fill=fill, radius=1.5)
    return c.down()


def background():
    ys = np.linspace(0, 1, H)[:, None, None]
    top, bot = np.array((10, 10, 26)), np.array((20, 16, 40))
    arr = np.broadcast_to(top * (1 - ys) + bot * ys, (H, W, 3)).astype(np.uint8)
    img = Image.fromarray(np.ascontiguousarray(arr), 'RGB').convert('RGBA')
    img.alpha_composite(grid((52, 58, 86, 255)))
    d = ImageDraw.Draw(img)
    for age in (0, 18, 40, 80):
        y = GY + age * PY_ + PY_ / 2 - 1
        d.text((GX - 14, y), str(age), font=font(SEMI, 24), fill=(170, 176, 200), anchor='rm')
    return img


BG_IMG, FULL = background(), grid((255, 204, 51, 255))


def frame_core(t):
    m = mondays(t)
    n = TOTAL if t >= T_STOP else int(m)
    img = BG_IMG.copy()
    mask = Image.new('L', (W, H), 0)
    md = ImageDraw.Draw(mask)
    r, c = divmod(n, COLS)
    if r > 0:
        md.rectangle([0, 0, W, int(GY + r * PY_) - 1], fill=255)
    if c > 0:
        md.rectangle([0, int(GY + r * PY_) - 1, int(GX + c * PX) - 2, int(GY + (r + 1) * PY_)], fill=255)
    filled = FULL.copy()
    filled.putalpha(Image.composite(FULL.getchannel('A'), Image.new('L', (W, H), 0), mask))
    dim = 1 - 0.6 * ease_io(ramp(t, T_TWIST - 0.1, T_TWIST + 0.3))
    comp(img, filled, 0.92 * dim)
    hc = Canvas()                                         # the current Monday, glowing
    if n < TOTAL:
        x, y = cell_xy(n)
        hc.rect([x - 3, y - 3, x + PX, y + PY_], fill=(255, 246, 210, 255), radius=2)
    comp(img, glow(hc.down(), radius=16, strength=1.2), dim)
    for vv, tp, txt in MILESTONES:
        al = ease_io(ramp(t, tp - 0.2, tp + 0.05)) * (1 - ease_io(ramp(t, tp + 0.9, tp + 1.15)))
        if al > 0.02 and t < T_STOP:
            lb, _ = big_text([(txt[0], XB, 54, WHITE), (txt[1], BOLD, 42, GOLD)], 0)
            sub = lb.crop(lb.getbbox())
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            lay.alpha_composite(sub, ((W - sub.width) // 2, 530))
            comp(img, lay, al)
    ca = 1 - ramp(t, T_TWIST - 0.1, T_TWIST + 0.2)
    if ca > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(lay)
        val = f'{n:,}'
        dd.rounded_rectangle([300, 1324, 780, 1440], radius=40, fill=(6, 10, 22, 215))
        dd.text((W / 2 + 4, 1360), val, font=font(BLACK, 80), fill=(0, 0, 0, 150), anchor='mm')
        dd.text((W / 2, 1356), val, font=font(BLACK, 80), fill=GOLD if t >= T_STOP else WHITE, anchor='mm')
        dd.text((W / 2, 1420), 'Mondays', font=font(BOLD, 26), fill=(200, 206, 225), anchor='mm')
        comp(img, lay, ca)
    return BR.overlay(img, t, RESULT)


render_frame = looped(frame_core, DUR, xf=0.5)


def music(mu):
    from brand import drum_track, ding, drop_hit
    lvl = lambda tt: mondays(tt) / TOTAL
    mu.bed(0, T_STOP, cutoff=lambda tt: 0.05 + 0.06 * lvl(tt), vol=lambda tt: (0.015 + 0.04 * lvl(tt)) * clamp(tt / 0.05), seed=30)
    drum_track(mu, T_STOP - 0.32, lvl, bpm0=96, bpm1=150, key=3, roll=1.4)
    for vv, tp, _ in MILESTONES:
        ding(mu, tp, key=3, vol=0.15, pan=0.4 if vv < 1500 else -0.4)
    mu.silence(T_STOP - 0.32, T_STOP)
    drop_hit(mu, T_STOP, key=3)
    mu.bed(T_STOP + 0.4, DUR, cutoff=lambda tt: 0.02, vol=lambda tt: 0.01, seed=19)
    mu.bell(T_TWIST, 659.25, 0.16, -0.3); mu.bell(T_TWIST + 0.1, 987.77, 0.16, 0.3)


if __name__ == '__main__':
    main(render_frame, DUR, music, sys.argv)
