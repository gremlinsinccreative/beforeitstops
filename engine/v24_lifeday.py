"""v6 FACT 024 Your 80 years as one day. How long is 1 year? 13 s, no teaser (even number).
Human-scale time arm of the topic test ("X as one day"). Pure arithmetic on a premise stated on screen
(an 80-year life squeezed into 24 hours); no health or life-expectancy claim is made.
1,440 min / 80 = 18 min per year. Age 18 = 05:24, age 40 = 12:00. Twist: one real day = 1,440 min x 60 / 29,220 days = 2.96 s -> 3 s.
Hero: a 24-hour dial (midnight top, noon bottom) filling clockwise in gold from midnight to midnight. One number: the clock time."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from scipy.interpolate import PchipInterpolator
from lib import *
from lib2 import big_text
from brand2 import *

DUR, T_STOP, T_TWIST = 13.0, 9.6, 11.0
LIFE, DAY_MIN = 80, 24 * 60
PER_YEAR = DAY_MIN / LIFE
assert PER_YEAR == 18
assert 18 * PER_YEAR == 5 * 60 + 24 and 40 * PER_YEAR == 12 * 60
assert round(DAY_MIN * 60 / (LIFE * 365.25), 2) == 2.96          # twist: each real day = 3 s

KEYS = [(0, 0.0), (1.4, 5.5), (2.9, 17.4), (3.6, 18.2), (5.6, 39.2), (6.4, 40.4), (8.6, 77.6), (9.6, 80.0)]
_P = PchipInterpolator([k[0] for k in KEYS], [k[1] for k in KEYS])


def age(t):
    return float(_P(min(max(t, 0.0), T_STOP)))


def t_at(v):
    lo, hi = 0.0, T_STOP
    for _ in range(40):
        md = (lo + hi) / 2
        lo, hi = (lo, md) if age(md) >= v else (md, hi)
    return hi


MILESTONES = [(18, t_at(18), ['Age 18: 5:24 am', 'before sunrise']),
              (40, t_at(40), ['Age 40: noon', 'half the day gone'])]
BR = Brand2(24, ['Your 80 years as one day.', 'How long is 1 year?'], 'Your 80 years as one day. How long is 1 year?',
            [('A', '18 seconds'), ('B', '18 minutes'), ('C', '3 hours')],
            [('18 minutes', BLACK, 120, GOLD), ('24 hours ÷ 80 years', BOLD, 42, WHITE)],
            [('Each day you live:', BOLD, 48, WHITE), ('3 seconds', BLACK, 80, GOLD)], T_STOP, T_TWIST, DUR,
            sub='Wait for midnight', cta='Comment your letter', q_size=74)
RESULT = {'A': 'out', 'B': 'win', 'C': 'out'}

CX, CY, R = 540, 1010, 300


def clock_min(a):
    return a * PER_YEAR


def background(k):
    ys = np.linspace(0, 1, H)[:, None, None]
    night_t, night_b = np.array((6, 8, 24)), np.array((14, 14, 40))
    day_t, day_b = np.array((18, 34, 70)), np.array((30, 40, 72))
    top = night_t * (1 - k) + day_t * k
    bot = night_b * (1 - k) + day_b * k
    arr = np.broadcast_to(top * (1 - ys) + bot * ys, (H, W, 3)).astype(np.uint8)
    return Image.fromarray(np.ascontiguousarray(arr), 'RGB').convert('RGBA')


BGS = [background(k) for k in np.linspace(0, 1, 21)]


def frame_core(t):
    a = age(t)
    m = clock_min(a)
    daylight = max(0.0, math.sin(math.pi * (m / DAY_MIN)))            # 0 at midnight, 1 at noon
    img = BGS[int(round(daylight * 20))].copy()
    c = Canvas()
    c.circle(CX, CY, R + 18, fill=(10, 12, 26, 200))
    for hh in range(24):
        ang = -math.pi / 2 + 2 * math.pi * hh / 24
        r0 = R - (26 if hh % 6 == 0 else 14)
        c.line([(CX + r0 * math.cos(ang), CY + r0 * math.sin(ang)), (CX + R * math.cos(ang), CY + R * math.sin(ang))],
               fill=(190, 196, 220, 200), width=5 if hh % 6 == 0 else 3)
    img.alpha_composite(c.down())
    d0 = ImageDraw.Draw(img)
    for hh, lab in [(6, '6 am'), (12, 'noon'), (18, '6 pm')]:
        ang = -math.pi / 2 + 2 * math.pi * hh / 24
        rr = R - 70
        d0.text((CX + rr * math.cos(ang), CY + rr * math.sin(ang)), lab, font=font(SEMI, 30), fill=(170, 176, 200), anchor='mm')
    hc = Canvas()
    frac = m / DAY_MIN
    if frac > 0.002:
        n = max(2, int(frac * 360))
        pts = [(CX + R * math.cos(-math.pi / 2 + 2 * math.pi * frac * i / n), CY + R * math.sin(-math.pi / 2 + 2 * math.pi * frac * i / n))
               for i in range(n + 1)]
        hc.line(pts, fill=(255, 204, 51, 255), width=16)
    ang = -math.pi / 2 + 2 * math.pi * frac
    hc.circle(CX + R * math.cos(ang), CY + R * math.sin(ang), 15, fill=(255, 236, 190, 255))
    img.alpha_composite(glow(hc.down(), radius=18, strength=0.5))
    for vv, tp, txt in MILESTONES:
        al = ease_io(ramp(t, tp - 0.2, tp + 0.05)) * (1 - ease_io(ramp(t, tp + 0.9, tp + 1.15)))
        if al > 0.02 and t < T_STOP:
            lb, _ = big_text([(txt[0], XB, 56, WHITE), (txt[1], BOLD, 40, GOLD)], 0)
            sub = lb.crop(lb.getbbox())
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            lay.alpha_composite(sub, (W - 70 - sub.width, 470) if vv == 18 else (70, 470))
            comp(img, lay, al)
    ca = 1 - ramp(t, T_TWIST - 0.1, T_TWIST + 0.2)
    if ca > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(lay)
        mm = int(round(m)) if t >= T_STOP else int(m)
        val = '24:00' if t >= T_STOP else f'{mm // 60:02d}:{mm % 60:02d}'
        dd.text((CX + 4, CY + 4), val, font=font(BLACK, 88), fill=(0, 0, 0, 140), anchor='mm')
        dd.text((CX, CY), val, font=font(BLACK, 88), fill=GOLD if t >= T_STOP else WHITE, anchor='mm')
        comp(img, lay, ca)
    return BR.overlay(img, t, RESULT)


render_frame = looped(frame_core, DUR, xf=0.5)


def music(mu):
    from brand import drum_track, ding, drop_hit
    lvl = lambda tt: age(tt) / LIFE
    mu.bed(0, T_STOP, cutoff=lambda tt: 0.05 + 0.06 * lvl(tt), vol=lambda tt: (0.015 + 0.04 * lvl(tt)) * clamp(tt / 0.05), seed=24)
    drum_track(mu, T_STOP - 0.32, lvl, bpm0=96, bpm1=150, key=0, roll=1.4)
    for vv, tp, _ in MILESTONES:
        ding(mu, tp, key=0, vol=0.15, pan=0.4 if vv == 18 else -0.4)
    mu.silence(T_STOP - 0.32, T_STOP)
    drop_hit(mu, T_STOP, key=0)
    mu.bed(T_STOP + 0.4, DUR, cutoff=lambda tt: 0.02, vol=lambda tt: 0.01, seed=9)
    mu.bell(T_TWIST, 659.25, 0.16, -0.3); mu.bell(T_TWIST + 0.1, 987.77, 0.16, 0.3)


if __name__ == '__main__':
    main(render_frame, DUR, music, sys.argv)
