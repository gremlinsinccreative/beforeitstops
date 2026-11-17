"""v3.1 FACT 012 - How old is the sunlight you see?
1 au = 149,597,870,700 m (IAU 2012 B2); c = 299,792,458 m/s -> 499.0 s = 8 min 19 s.
Chips: A 8 seconds (struck when the clock passes 0:08), B 8 minutes (correct), C 8 hours (struck at the stop).
Passed on the way: Mercury's orbit 57.91 million km (193 s = 3:13), Venus's orbit 108.21 million km (361 s = 6:01),
NASA planetary fact sheet mean distances. Twist: moonlight is 1.3 s old (384,400 km / c = 1.28 s).
The clock is time-lapsed; photon position always matches the clock reading."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from lib import *
from brand import *

DUR, T_STOP, T_TWIST, T_WARP = 10.5, 7.3, 8.7, 1.35
AU, C = 149597870700, 299792458
TOTAL = AU / C
assert abs(TOTAL - 499.0) < 0.01 and round(384400e3 / C, 1) == 1.3
assert round(57.91e9 / C) == 193 and round(108.21e9 / C) == 361
BR = Brand(12, ['How old is the', 'sunlight you see?'], [('A', '8 seconds'), ('B', '8 minutes'), ('C', '8 hours')],
           [('8 min 19 s', BLACK, 132, GOLD), ('old, every time you see it', BOLD, 46, WHITE)],
           [('Moonlight is only', BOLD, 48, WHITE), ('1.3 seconds old', BLACK, 92, GOLD)], T_STOP, T_TWIST, DUR)


def clock(t):
    """Seconds of light travel shown at video time t: fast, then slows into the stop."""
    if t >= T_STOP:
        return TOTAL
    if t < T_WARP:
        return 8.6 * (t / T_WARP) ** 1.3
    u = (t - T_WARP) / (T_STOP - T_WARP)
    return 8.6 + (TOTAL - 8.6) * (1 - (1 - u) ** 1.9)


def t_at(sec):
    lo, hi = 0.0, T_STOP
    for _ in range(40):
        m = (lo + hi) / 2
        lo, hi = (lo, m) if clock(m) >= sec else (m, hi)
    return hi


SUN = (540, 1560)     # rising from the bottom; its lower half sits behind the platform captions
EARTH = (540, 600)
SUN_R, EARTH_R = 330, 46
P0, P1 = SUN[1] - SUN_R, EARTH[1] + EARTH_R
ORBITS = [('Mercury', 57.91e9), ('Venus', 108.21e9)]
PASS = {name: t_at(d / C) for name, d in ORBITS}
T8 = t_at(8)


def ypos(sec):
    return P0 + (P1 - P0) * sec / TOTAL


def mmss(s):
    s = int(s)
    return f'{s // 60}:{s % 60:02d}'


rng = np.random.default_rng(7)
STARS = [(rng.uniform(0, W), rng.uniform(0, 1440), rng.uniform(0.8, 2.6)) for _ in range(220)]
YY = np.linspace(0, 1, H)[:, None, None]
BGA = (np.array((10, 6, 22)) * (1 - YY) + np.array((2, 3, 10)) * YY)
BGA = np.broadcast_to(BGA, (H, W, 3)).astype(np.float32).copy()
yy, xx = np.mgrid[0:H, 0:W]
dsun = np.sqrt((xx - SUN[0]) ** 2 + (yy - SUN[1]) ** 2)
SUNGLOW = np.clip(1 - (dsun - SUN_R) / 620, 0, 1)[..., None] ** 2.2 * np.array((255, 120, 30))[None, None]
_core = np.clip(1 - dsun / SUN_R, 0, 1)[..., None]
SUNBODY = (dsun <= SUN_R)[..., None] * (np.array((255, 120, 20)) + _core * np.array((0, 120, 120)))
del yy, xx, dsun, _core


def states(t):
    st = {'A': 'out' if t >= T8 else 'idle', 'B': 'win' if t >= T_STOP else 'idle', 'C': 'out' if t >= T_STOP else 'idle'}
    pops = {'A': math.exp(-(t - T8) * 6) if t >= T8 else 0, 'B': math.exp(-(t - T_STOP) * 5) if t >= T_STOP else 0}
    return st, pops


def frame_core(t):
    flick = 1 + 0.05 * math.sin(t * 7) + 0.03 * math.sin(t * 13.3)
    arr = BGA + SUNGLOW * 0.55 * flick
    m_ = SUNBODY.any(axis=2, keepdims=True)
    arr = np.where(m_, SUNBODY, arr)
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')
    d = ImageDraw.Draw(img, 'RGBA')
    for sx, sy, sr in STARS:
        if math.hypot(sx - SUN[0], sy - SUN[1]) > SUN_R + 120:
            v = int(150 + 100 * math.sin(sx * 3 + t * 2))
            d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(v, v, v, 200))
    # slow rays off the sun's limb
    for k in range(18):
        a = math.pi + (k + 0.5) / 18 * math.pi + 0.03 * math.sin(t * 1.3 + k)
        l = 60 + 50 * (0.5 + 0.5 * math.sin(t * 2.1 + k * 1.7))
        x0, y0 = SUN[0] + SUN_R * math.cos(a), SUN[1] + SUN_R * math.sin(a)
        x1, y1 = SUN[0] + (SUN_R + l) * math.cos(a), SUN[1] + (SUN_R + l) * math.sin(a)
        d.line([x0, y0, x1, y1], fill=(255, 190, 90, 70), width=6)
    # light path + orbit rings crossing it
    d.line([SUN[0], P0, EARTH[0], P1], fill=(255, 220, 150, 40), width=2)
    for name, dist in ORBITS:
        y = ypos(dist / C)
        r = SUN[1] - y
        d.ellipse([SUN[0] - r, SUN[1] - r, SUN[0] + r, SUN[1] + r], outline=(150, 160, 215, 70), width=2)
    # earth
    ex, ey = EARTH
    ea = ease_io(ramp(t, 0.95, 1.4))
    el = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d0, d = d, ImageDraw.Draw(el)
    d.ellipse([ex - EARTH_R - 10, ey - EARTH_R - 10, ex + EARTH_R + 10, ey + EARTH_R + 10], fill=(80, 150, 255, 60))
    d.ellipse([ex - EARTH_R, ey - EARTH_R, ex + EARTH_R, ey + EARTH_R], fill=(50, 120, 230))
    d.chord([ex - EARTH_R, ey - EARTH_R, ex + EARTH_R, ey + EARTH_R], 200, 330, fill=(70, 170, 90))
    comp(img, el, ea if t < 5 else 1.0)
    d = d0
    # photon + trail
    sec = clock(t)
    py = ypos(sec)
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for j in range(24):
        s2 = clock(max(0.0, t - j / 90))
        y2 = ypos(s2)
        a = int(200 * (1 - j / 24))
        gd.ellipse([SUN[0] - 9, y2 - 9, SUN[0] + 9, y2 + 9], fill=(255, 240, 200, a))
    gd.ellipse([SUN[0] - 26, py - 26, SUN[0] + 26, py + 26], fill=(255, 230, 160, 160))
    glow = glow.filter(ImageFilter.GaussianBlur(8))
    img.alpha_composite(glow)
    d = ImageDraw.Draw(img, 'RGBA')
    d.ellipse([SUN[0] - 11, py - 11, SUN[0] + 11, py + 11], fill=(255, 255, 245))
    if t >= T_STOP:
        k = clamp((t - T_STOP) / 1.2)
        rr = 50 + 110 * ease_out(k)
        if k < 0.98:
            d.ellipse([ex - rr, ey - rr, ex + rr, ey + rr], outline=(255, 230, 160, int(200 * (1 - k))), width=6)
    # orbit label while crossing
    for name, dist in ORBITS:
        y = ypos(dist / C)
        a = clamp(1 - abs(py - y) / 90)
        if a > 0.02 and t < T_STOP:
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(lay).text((SUN[0] + 60, y), f"{name}'s orbit", font=font(XB, 48), fill=WHITE, anchor='lm')
            comp(img, lay, a)
    # the stopwatch: one big number
    d = ImageDraw.Draw(img, 'RGBA')
    ca = 1 - ramp(t, T_TWIST - 0.1, T_TWIST + 0.15)
    if ca > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        val = '8:19' if t >= T_STOP else mmss(sec)
        ImageDraw.Draw(lay).text((290, 900), val, font=font(BLACK, 116), fill=GOLD if t >= T_STOP else WHITE, anchor='mm')
        comp(img, lay, ca)
    st, pops = states(t)
    BR.overlay(img, t, st, pops)
    return punch(img, t, T_STOP)


render_frame = looped(frame_core, DUR)


def music(m):
    # deep solar rumble that recedes as the photon leaves the sun
    m.bed(0, T_STOP, cutoff=lambda tt: 0.08 + 0.1 * (1 - clock(tt) / TOTAL),
          vol=lambda tt: 0.09 * (1 - 0.75 * clock(tt) / TOTAL) * clamp(tt / 0.04), seed=11)
    # photon tone: pure, gliding up slowly
    m.drone(0, T_STOP, lambda tt: 440 + 220 * clock(tt) / TOTAL, vol=0.018)
    # stopwatch ticks: one per 20 seconds of light-time, panned centre
    nxt = 20
    for i in range(1, int(T_STOP * 600)):
        tt = i / 600
        if clock(tt) >= nxt:
            m.clack(tt, f=2200, vol=0.09, pan=0.15 if (nxt // 20) % 2 else -0.15)
            nxt += 20
    for name, pt in PASS.items():
        m.whoosh(pt - 0.3, 0.7, 0.22, -0.7, 0.7)
        m.bell(pt, 1174.66, 0.14, 0.3)
    m.bell(T8, 880.0, 0.12, -0.4)
    m.whoosh(T_WARP - 0.25, 0.9, 0.35, -0.2, 0.2, bright=1.4)
    for hb in (T_STOP - 1.5, T_STOP - 1.08, T_STOP - 0.72):
        m.thump(hb, 0.5)
    m.silence(T_STOP - 0.32, T_STOP)
    m.stop_signature(T_STOP)
    m.bed(T_STOP + 0.4, DUR, cutoff=lambda tt: 0.02, vol=lambda tt: 0.012, seed=5)
    m.bell(T_TWIST, 659.25, 0.2, -0.3); m.bell(T_TWIST + 0.1, 987.77, 0.2, 0.3)


if __name__ == '__main__':
    main(render_frame, DUR, music, sys.argv)
