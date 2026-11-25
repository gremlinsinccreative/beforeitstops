"""v6 FACT 026 Your heart in one day: how many beats? 13 s, no teaser (even number).
Human-scale time arm of the topic test ("X in one day"). Physiology fact only: no health claim or advice.
Sources: British Heart Foundation, "How your heart works" (bhf.org.uk, read 25 Nov 2026): "Each day, your heart beats
around 100,000 times." Cleveland Clinic, "30 Facts About Your Heart" (22 Aug 2023): "beats about 100,000 times per day";
"During the average person's lifetime, their heart beats more than 2.6 billion times" (twist).
Milestones are straight proportions of 100,000 over 24 h: noon = 50,000, 6 pm = 75,000.
Hero: one glowing heart that beats gently, a thin 24-hour arc under it. One number: the beat count."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from scipy.interpolate import PchipInterpolator
from lib import *
from lib2 import big_text
from brand2 import *

DUR, T_STOP, T_TWIST = 13.0, 9.6, 11.0
PER_DAY = 100_000
assert PER_DAY * 12 // 24 == 50_000 and PER_DAY * 18 // 24 == 75_000
assert 60 < PER_DAY / (24 * 60) < 70                 # ~69 a minute, inside the usual resting range

KEYS = [(0, 0.0), (1.4, 9000.0), (2.9, 47000.0), (3.6, 51000.0), (5.6, 73000.0), (6.4, 76500.0), (8.6, 97000.0), (9.6, 100000.0)]
_P = PchipInterpolator([k[0] for k in KEYS], [k[1] for k in KEYS])


def beats(t):
    return float(_P(min(max(t, 0.0), T_STOP)))


def t_at(v):
    lo, hi = 0.0, T_STOP
    for _ in range(40):
        md = (lo + hi) / 2
        lo, hi = (lo, md) if beats(md) >= v else (md, hi)
    return hi


MILESTONES = [(50000, t_at(50000), ['Noon: 50,000', 'half a day of beats']),
              (75000, t_at(75000), ['6 pm: 75,000', 'still going'])]
BR = Brand2(26, ['Your heart in one day.', 'How many beats?'], 'Your heart in one day: how many beats?',
            [('A', '10,000'), ('B', '100,000'), ('C', '1 million')],
            [('About 100,000', BLACK, 110, GOLD), ('Source: British Heart Foundation', BOLD, 40, WHITE)],
            [('In a lifetime:', BOLD, 48, WHITE), ('over 2.6 billion', BLACK, 74, GOLD)], T_STOP, T_TWIST, DUR,
            sub='Wait for midnight', cta='Comment your letter', q_size=84)
RESULT = {'A': 'out', 'B': 'win', 'C': 'out'}

CX, CY, S = 540, 1000, 230        # heart centre and size


def heart_pts(cx, cy, s, n=120):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x = 16 * math.sin(a) ** 3
        y = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
        pts.append((cx + x * s / 17, cy - y * s / 17))
    return pts


def background():
    ys = np.linspace(0, 1, H)[:, None, None]
    top, bot = np.array((14, 8, 18)), np.array((40, 12, 26))
    arr = np.broadcast_to(top * (1 - ys) + bot * ys, (H, W, 3)).astype(np.uint8)
    return Image.fromarray(np.ascontiguousarray(arr), 'RGB').convert('RGBA')


BG_IMG = background()
AR_Y, AR_X0, AR_X1 = 1330, 170, 910        # the day bar (midnight -> midnight)


def frame_core(t):
    b = beats(t)
    frac = b / PER_DAY
    img = BG_IMG.copy()
    ca = 1 - ramp(t, T_TWIST - 0.1, T_TWIST + 0.2)
    if ca > 0:                                   # day bar, faded out under the twist card
        c = Canvas()
        c.rect([AR_X0, AR_Y - 6, AR_X1, AR_Y + 6], fill=(70, 50, 70, 255), radius=6)
        for hh in (0, 12, 24):
            x = AR_X0 + (AR_X1 - AR_X0) * hh / 24
            c.line([(x, AR_Y - 18), (x, AR_Y + 18)], fill=(170, 150, 175, 220), width=3)
        c.rect([AR_X0, AR_Y - 6, AR_X0 + (AR_X1 - AR_X0) * frac, AR_Y + 6], fill=(255, 204, 51, 255), radius=6)
        c.circle(AR_X0 + (AR_X1 - AR_X0) * frac, AR_Y, 13, fill=(255, 236, 190, 255))
        bar = c.down()
        d0 = ImageDraw.Draw(bar)
        for hh, lab in [(0, '0:00'), (12, 'noon'), (24, '24:00')]:
            x = AR_X0 + (AR_X1 - AR_X0) * hh / 24
            d0.text((x, AR_Y + 46), lab, font=font(SEMI, 30), fill=(175, 160, 185), anchor='mm')
        comp(img, bar, ca)
    hc = Canvas()
    # gentle beat: ~1.2 beats/s, a soft swell (no flicker)
    ph = (t * 1.2) % 1.0
    pulse = 1 + 0.06 * math.exp(-((ph - 0.08) / 0.07) ** 2) + 0.035 * math.exp(-((ph - 0.3) / 0.08) ** 2)
    if t >= T_STOP:
        pulse = 1.0
    hc.polygon(heart_pts(CX, CY, S * pulse), fill=(226, 52, 78, 255))
    img.alpha_composite(glow(hc.down(), radius=22, strength=0.45 + 0.25 * (pulse - 1) / 0.06))
    for vv, tp, txt in MILESTONES:
        al = ease_io(ramp(t, tp - 0.2, tp + 0.05)) * (1 - ease_io(ramp(t, tp + 0.9, tp + 1.15)))
        if al > 0.02 and t < T_STOP:
            lb, _ = big_text([(txt[0], XB, 56, WHITE), (txt[1], BOLD, 40, GOLD)], 0)
            sub = lb.crop(lb.getbbox())
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            lay.alpha_composite(sub, ((W - sub.width) // 2, 590))
            comp(img, lay, al)
    if ca > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(lay)
        v = PER_DAY if t >= T_STOP else int(b)
        val = f'{v:,}'
        dd.text((CX + 4, CY + 4), val, font=font(BLACK, 92), fill=(0, 0, 0, 150), anchor='mm')
        dd.text((CX, CY), val, font=font(BLACK, 92), fill=GOLD if t >= T_STOP else WHITE, anchor='mm')
        comp(img, lay, ca)
    return BR.overlay(img, t, RESULT)


render_frame = looped(frame_core, DUR, xf=0.5)


def music(mu):
    from brand import drum_track, ding, drop_hit
    lvl = lambda tt: beats(tt) / PER_DAY
    mu.bed(0, T_STOP, cutoff=lambda tt: 0.05 + 0.06 * lvl(tt), vol=lambda tt: (0.015 + 0.04 * lvl(tt)) * clamp(tt / 0.05), seed=26)
    drum_track(mu, T_STOP - 0.32, lvl, bpm0=96, bpm1=150, key=0, roll=1.4)
    for vv, tp, _ in MILESTONES:
        ding(mu, tp, key=0, vol=0.15, pan=0.4 if vv == 50000 else -0.4)
    mu.silence(T_STOP - 0.32, T_STOP)
    drop_hit(mu, T_STOP, key=0)
    mu.bed(T_STOP + 0.4, DUR, cutoff=lambda tt: 0.02, vol=lambda tt: 0.01, seed=12)
    mu.bell(T_TWIST, 659.25, 0.16, -0.3); mu.bell(T_TWIST + 0.1, 987.77, 0.16, 0.3)


if __name__ == '__main__':
    main(render_frame, DUR, music, sys.argv)
