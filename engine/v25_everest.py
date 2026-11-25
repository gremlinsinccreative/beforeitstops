"""v6 FACT 025 Drop Everest into the deepest trench. Does it stick out? 13 s, + next-up teaser (odd number).
Non-human-scale arm of the topic test (geography / ocean); "settle it" style (most people say the peak sticks out).
Sources: Challenger Deep 10,935 m, NOAA (Greenaway et al., Deep-Sea Research Part I, 2021, 2020 voyage; via Live Science,
read 25 Nov 2026; NOAA NCEI's 2010 UNH survey gives 10,994 m +/- 40 m, and NCEI says "there would still be over a mile
of water over the top of it"). Everest 8,848.86 m, joint Nepal-China announcement, 8 Dec 2020 (AP / Al Jazeera).
Twist: NOAA Ocean Service, light "can be detected as far as 1,000 meters down" -> the summit sits in the dark.
Hero: cross-section; Everest sinks into the trench. One number: the summit's height relative to sea level."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from scipy.interpolate import PchipInterpolator
from lib import *
from lib2 import big_text
from brand2 import *

DUR, T_STOP, T_TWIST = 13.0, 9.6, 11.0
DEEP, EVEREST = 10935, 8849
assert DEEP - EVEREST == 2086 and 10994 - 8849 > 2000          # ~2 km of water above the summit with either survey
assert DEEP - EVEREST > 1609                                      # agrees with NCEI's "over a mile"
assert DEEP - EVEREST > 1000                                      # below NOAA's 1,000 m light limit

# summit height (m) over time: +8,849 -> -2,086, slowing at the two milestones
KEYS = [(0, 8849.0), (1.4, 8000.0), (2.9, 4700.0), (3.6, 4300.0), (5.6, 300.0), (6.4, -150.0), (8.6, -1900.0), (9.6, -2086.0)]
_P = PchipInterpolator([k[0] for k in KEYS], [k[1] for k in KEYS])


def summit(t):
    return float(_P(min(max(t, 0.0), T_STOP)))


def t_at(v):
    lo, hi = 0.0, T_STOP
    for _ in range(40):
        md = (lo + hi) / 2
        lo, hi = (md, hi) if summit(md) > v else (lo, md)
    return hi


HALF = EVEREST / 2
MILESTONES = [(HALF, t_at(HALF), ['Half of Everest', 'under the sea']),
              (0, t_at(0), ['Summit at sea level', 'still sinking'])]
BR = Brand2(25, ['Drop Everest into', 'the deepest trench.', 'Does it stick out?'],
            'Everest in the deepest trench: does it stick out?',
            [('A', 'Sticks out'), ('B', '2 km under'), ('C', 'Just under')],
            [('2 km under water', BLACK, 100, GOLD), ('Trench 10,935 m  ·  Everest 8,849 m  ·  NOAA', BOLD, 36, WHITE)],
            [('The summit would sit', BOLD, 46, WHITE), ('in total darkness', BLACK, 66, GOLD)], T_STOP, T_TWIST, DUR,
            sub='Wait for the seafloor', cta='Comment your letter', q_size=84,
            next_line='Next: FACT 026 · Your heart in one day')
RESULT = {'A': 'out', 'B': 'win', 'C': 'out'}

SEA_Y, PXM = 880, 0.075                 # sea surface y, pixels per metre (floor at 880 + 820 = 1700)
FLOOR_Y = SEA_Y + DEEP * PXM
MX, HALF_W = 400, 330                   # mountain centre x and half base width


def y_of(depth_m):
    return SEA_Y + depth_m * PXM


def background():
    arr = np.zeros((H, W, 3), np.float32)
    ys = np.arange(H)[:, None]
    sky = np.clip(ys / SEA_Y, 0, 1)
    sea = np.clip((ys - SEA_Y) / (FLOOR_Y - SEA_Y), 0, 1)
    sky_col = np.array((16, 22, 44)) * (1 - sky[..., None]) + np.array((44, 62, 96)) * sky[..., None]
    sea_col = np.array((14, 52, 92)) * (1 - sea[..., None]) + np.array((2, 6, 16)) * sea[..., None]
    arr[:] = np.where((ys < SEA_Y)[..., None], sky_col, sea_col)
    img = Image.fromarray(arr.astype(np.uint8), 'RGB').convert('RGBA')
    c = Canvas()
    # trench walls (seabed) on both sides, a V cut down to the floor
    c.polygon([(0, y_of(4200)), (150, y_of(4400)), (MX - HALF_W - 40, y_of(9800)), (MX - HALF_W + 30, FLOOR_Y),
               (MX + HALF_W - 30, FLOOR_Y), (MX + HALF_W + 60, y_of(9600)), (850, y_of(4600)), (W, y_of(4100)),
               (W, H), (0, H)], fill=(30, 26, 34, 255))
    c.line([(0, y_of(4200)), (150, y_of(4400)), (MX - HALF_W - 40, y_of(9800)), (MX - HALF_W + 30, FLOOR_Y),
            (MX + HALF_W - 30, FLOOR_Y), (MX + HALF_W + 60, y_of(9600)), (850, y_of(4600)), (W, y_of(4100))],
           fill=(80, 74, 92, 255), width=4)
    c.line([(0, SEA_Y), (W, SEA_Y)], fill=(150, 200, 235, 200), width=4)
    img.alpha_composite(c.down())
    return img


BG_IMG = background()


def frame_core(t):
    s = summit(t)
    img = BG_IMG.copy()
    peak_y = SEA_Y - s * PXM
    base_y = peak_y + EVEREST * PXM
    hc = Canvas()
    hc.polygon([(MX, peak_y), (MX + HALF_W, base_y), (MX - HALF_W, base_y)], fill=(118, 112, 126, 255))
    hc.polygon([(MX, peak_y), (MX + 40, peak_y + 30), (MX - 38, peak_y + 30)], fill=(250, 250, 255, 255))     # snow cap
    hc.polygon([(MX, peak_y), (MX + HALF_W, base_y), (MX + 40, base_y)], fill=(92, 86, 102, 255))              # shaded face
    hero = hc.down()
    img.alpha_composite(glow(hero, radius=16, strength=0.4))
    # water over the submerged part: a translucent blue veil below the sea line
    veil = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    vy = int(SEA_Y)
    veil.paste((10, 40, 80, 120), (0, vy, W, H))
    img.alpha_composite(veil)
    c = Canvas()
    c.line([(0, SEA_Y), (W, SEA_Y)], fill=(170, 215, 245, 230), width=4)
    img.alpha_composite(c.down())
    for vv, tp, txt in MILESTONES:
        al = ease_io(ramp(t, tp - 0.2, tp + 0.05)) * (1 - ease_io(ramp(t, tp + 0.9, tp + 1.15)))
        if al > 0.02 and t < T_STOP:
            lb, _ = big_text([(txt[0], XB, 54, WHITE), (txt[1], BOLD, 40, GOLD)], 0)
            sub = lb.crop(lb.getbbox())
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            lay.alpha_composite(sub, (W - 60 - sub.width, 640))
            comp(img, lay, al)
    ca = 1 - ramp(t, T_TWIST - 0.1, T_TWIST + 0.2)
    if ca > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(lay)
        v = -2086 if t >= T_STOP else int(round(s))
        val = f'{v:+,} m'.replace('-', '−')
        x0, y0 = 800, 1010
        dd.text((x0, y0 - 74), 'summit', font=font(SEMI, 34), fill=(190, 205, 230), anchor='mm')
        dd.text((x0 + 4, y0 + 4), val, font=font(BLACK, 84), fill=(0, 0, 0, 140), anchor='mm')
        dd.text((x0, y0), val, font=font(BLACK, 84), fill=GOLD if t >= T_STOP else WHITE, anchor='mm')
        comp(img, lay, ca)
    return BR.overlay(img, t, RESULT)


render_frame = looped(frame_core, DUR, xf=0.5)


def music(mu):
    from brand import drum_track, ding, drop_hit
    lvl = lambda tt: (EVEREST - summit(tt)) / DEEP
    mu.bed(0, T_STOP, cutoff=lambda tt: 0.05 + 0.06 * lvl(tt), vol=lambda tt: (0.015 + 0.045 * lvl(tt)) * clamp(tt / 0.05), seed=25)
    drum_track(mu, T_STOP - 0.32, lvl, bpm0=96, bpm1=150, key=0, roll=1.4)
    for vv, tp, _ in MILESTONES:
        ding(mu, tp, key=0, vol=0.15, pan=0.4)
    mu.silence(T_STOP - 0.32, T_STOP)
    drop_hit(mu, T_STOP, key=0)
    mu.bed(T_STOP + 0.4, DUR, cutoff=lambda tt: 0.02, vol=lambda tt: 0.01, seed=11)
    mu.bell(T_TWIST, 659.25, 0.16, -0.3); mu.bell(T_TWIST + 0.1, 987.77, 0.16, 0.3)


if __name__ == '__main__':
    main(render_frame, DUR, music, sys.argv)
