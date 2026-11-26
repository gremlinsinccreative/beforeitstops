"""v6 FACT 028 Drive to the Sun at 100 km/h: how long? 13 s, no teaser (even number). Committed by #027's teaser.
Human-scale arm of the topic test (distance as a lifetime of driving).
1 AU = 149,597,870.7 km (IAU 2012 Resolution B2). At 100 km/h nonstop: 1,495,978.7 h = 170.7 years (Julian year 8,766 h).
Milestones (straight line towards the Sun, NASA planetary fact sheets, semi-major axes): Venus's orbit 108.21 million km
from the Sun -> crossed after (149.598 - 108.21) M km = 41.39 M km = 47.2 years; Mercury's 57.909 M km -> 91.69 M km = 104.6 years.
Twist: set off in 1856, arrive about now (2026.9 - 170.7 = 1856.2).
Hero: a small gold car driving from Earth to the Sun, its trail behind it. One number: years on the road."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.interpolate import PchipInterpolator
from lib import *
from lib2 import big_text
from brand2 import *

DUR, T_STOP, T_TWIST = 13.0, 9.6, 11.0
AU_KM, SPEED, YEAR_H = 149_597_870.7, 100.0, 8766.0
YEARS = AU_KM / SPEED / YEAR_H
assert round(AU_KM / SPEED) == 1_495_979 and round(YEARS, 1) == 170.7
VENUS_Y = (149.598 - 108.21) * 1e6 / SPEED / YEAR_H
MERC_Y = (149.598 - 57.909) * 1e6 / SPEED / YEAR_H
assert round(VENUS_Y, 1) == 47.2 and round(MERC_Y, 1) == 104.6
assert round(2026.9 - YEARS) == 1856

KEYS = [(0, 0.0), (1.4, 8.0), (3.0, 44.5), (3.7, 49.5), (5.8, 101.5), (6.5, 107.5), (8.6, 164.0), (9.6, YEARS)]
_P = PchipInterpolator([k[0] for k in KEYS], [k[1] for k in KEYS])


def years(t):
    return float(_P(min(max(t, 0.0), T_STOP)))


def t_at(v):
    lo, hi = 0.0, T_STOP
    for _ in range(40):
        md = (lo + hi) / 2
        lo, hi = (lo, md) if years(md) >= v else (md, hi)
    return hi


MILESTONES = [(VENUS_Y, t_at(VENUS_Y), ["Crossing Venus's orbit", '47 years in']),
              (MERC_Y, t_at(MERC_Y), ["Crossing Mercury's orbit", '105 years in'])]
BR = Brand2(28, ['Drive to the Sun', 'at 100 km/h.', 'How long?'], 'Drive to the Sun at 100 km/h: how long?',
            [('A', '17 years'), ('B', '170 years'), ('C', '1,700 years')],
            [('Over 170 years', BLACK, 104, GOLD), ('149.6 million km ÷ 100 km/h, nonstop (IAU)', BOLD, 34, WHITE)],
            [('Set off in 1856:', BOLD, 48, WHITE), ("you'd arrive about now", BLACK, 64, GOLD)], T_STOP, T_TWIST, DUR,
            sub='Wait for the Sun', cta='Comment your letter', q_size=80)
RESULT = {'A': 'out', 'B': 'win', 'C': 'out'}

PY = 1030                      # road line
EX, SX, SR_ = 150, 1035, 112   # Earth x, Sun centre x, Sun radius
X_END = SX - SR_ - 44          # car stops just short of the Sun's edge
VENUS_X = EX + (X_END - EX) * VENUS_Y / YEARS
MERC_X = EX + (X_END - EX) * MERC_Y / YEARS


def car_x(y):
    return EX + 46 + (X_END - EX - 46) * y / YEARS


def background():
    ys = np.linspace(0, 1, H)[:, None, None]
    xs = np.linspace(0, 1, W)[None, :, None]
    top, bot = np.array((6, 8, 20)), np.array((12, 14, 34))
    arr = top * (1 - ys) + bot * ys + np.array((40, 22, 4)) * np.clip(xs - 0.45, 0, 1) ** 2 * 1.4
    arr = np.broadcast_to(arr, (H, W, 3)).astype(np.uint8)
    img = Image.fromarray(np.ascontiguousarray(arr), 'RGB').convert('RGBA')
    c = Canvas()
    rng = np.random.default_rng(28)
    for _ in range(140):
        x, y = rng.uniform(0, W), rng.uniform(0, H * 0.74)
        c.circle(x, y, rng.uniform(0.8, 2.0), fill=(220, 226, 255, int(rng.uniform(50, 150))))
    # orbits of Venus and Mercury as faint arcs centred on the Sun, crossing the road
    for xr, col in [(VENUS_X, (240, 214, 170, 70)), (MERC_X, (200, 190, 180, 70))]:
        r = SX - xr
        pts = [(SX + r * math.cos(a), PY + r * math.sin(a)) for a in np.linspace(math.pi * 0.72, math.pi * 1.28, 80)]
        c.line(pts, fill=col, width=2.5)
    # Sun
    c.circle(SX, PY, SR_, fill=(255, 176, 60, 255))
    c.circle(SX, PY, SR_ * 0.82, fill=(255, 204, 92, 255))
    c.circle(SX, PY, SR_ * 0.55, fill=(255, 232, 150, 255))
    # Earth
    c.circle(EX, PY, 38, fill=(52, 120, 210, 255))
    c.ellipse([EX - 22, PY - 24, EX + 6, PY + 4], fill=(70, 170, 110, 220))
    c.ellipse([EX + 4, PY + 6, EX + 26, PY + 26], fill=(70, 170, 110, 200))
    # the road: dashed line
    for x in np.arange(EX + 46, SX - SR_ - 10, 26):
        c.line([(x, PY), (x + 12, PY)], fill=(150, 160, 190, 110), width=3)
    halo = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(halo).ellipse([SX - SR_ - 60, PY - SR_ - 60, SX + SR_ + 60, PY + SR_ + 60], fill=(255, 160, 50, 110))
    img.alpha_composite(halo.filter(ImageFilter.GaussianBlur(70)))
    img.alpha_composite(c.down())
    return img


BG_IMG = background()


def draw_car(c, x, y, s=1.0):
    c.rect([x - 30 * s, y - 20 * s, x + 30 * s, y - 2 * s], fill=(255, 214, 102, 255), radius=7 * s)
    c.rect([x - 16 * s, y - 34 * s, x + 14 * s, y - 16 * s], fill=(255, 226, 140, 255), radius=7 * s)
    c.rect([x - 11 * s, y - 30 * s, x + 9 * s, y - 20 * s], fill=(40, 60, 90, 255), radius=3 * s)
    for wx in (-17, 17):
        c.circle(x + wx * s, y - 1 * s, 8 * s, fill=(24, 24, 34, 255))
        c.circle(x + wx * s, y - 1 * s, 3.5 * s, fill=(190, 190, 200, 255))


def frame_core(t):
    yv = years(t)
    img = BG_IMG.copy()
    hc = Canvas()
    x = car_x(yv)
    hc.line([(EX + 46, PY), (x - 40, PY)], fill=(255, 204, 51, 210), width=5)       # trail: the distance driven
    draw_car(hc, x, PY - 4, 1.35)
    comp(img, glow(hc.down(), radius=14, strength=0.6), 1 - 0.65 * ease_io(ramp(t, T_TWIST - 0.1, T_TWIST + 0.3)))
    for vv, tp, txt in MILESTONES:
        al = ease_io(ramp(t, tp - 0.2, tp + 0.05)) * (1 - ease_io(ramp(t, tp + 0.9, tp + 1.15)))
        if al > 0.02 and t < T_STOP:
            lb, _ = big_text([(txt[0], XB, 52, WHITE), (txt[1], BOLD, 42, GOLD)], 0)
            sub = lb.crop(lb.getbbox())
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            lay.alpha_composite(sub, ((W - sub.width) // 2, 640))
            comp(img, lay, al)
    ca = 1 - ramp(t, T_TWIST - 0.1, T_TWIST + 0.2)
    if ca > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(lay)
        val = f'{YEARS:.1f}' if t >= T_STOP else f'{int(yv)}'
        dd.rounded_rectangle([290, 1160, 790, 1360], radius=40, fill=(6, 10, 22, 200))
        dd.text((W / 2 + 4, 1244), val, font=font(BLACK, 120), fill=(0, 0, 0, 150), anchor='mm')
        dd.text((W / 2, 1240), val, font=font(BLACK, 120), fill=GOLD if t >= T_STOP else WHITE, anchor='mm')
        dd.text((W / 2, 1330), 'years on the road', font=font(BOLD, 34), fill=(200, 206, 225), anchor='mm')
        comp(img, lay, ca)
    return BR.overlay(img, t, RESULT)


render_frame = looped(frame_core, DUR, xf=0.5)


def music(mu):
    from brand import drum_track, ding, drop_hit
    lvl = lambda tt: years(tt) / YEARS
    mu.bed(0, T_STOP, cutoff=lambda tt: 0.05 + 0.06 * lvl(tt), vol=lambda tt: (0.015 + 0.04 * lvl(tt)) * clamp(tt / 0.05), seed=28)
    drum_track(mu, T_STOP - 0.32, lvl, bpm0=96, bpm1=150, key=2, roll=1.4)
    for vv, tp, _ in MILESTONES:
        ding(mu, tp, key=2, vol=0.15, pan=0.4 if vv < 60 else -0.4)
    mu.silence(T_STOP - 0.32, T_STOP)
    drop_hit(mu, T_STOP, key=2)
    mu.bed(T_STOP + 0.4, DUR, cutoff=lambda tt: 0.02, vol=lambda tt: 0.01, seed=11)
    mu.bell(T_TWIST, 659.25, 0.16, -0.3); mu.bell(T_TWIST + 0.1, 987.77, 0.16, 0.3)


if __name__ == '__main__':
    main(render_frame, DUR, music, sys.argv)
