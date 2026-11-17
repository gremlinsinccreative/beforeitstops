"""v4 TEST - FACT 019 Quake 9 vs quake 6: how much more energy?
USGS: each whole-number step = 10x amplitude, about 32x energy. 3 steps: 32^3 = 32,768 energy, 1,000x amplitude.
Hero: one smooth seismograph line (swing grows 10x per step, soft-limited to the screen) that freezes at the STOP.
Calm skyline below sways gently. One number: the energy multiple."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from lib import *
from brand2 import *

DUR, T_STOP, T_TWIST = 10.5, 7.3, 8.7
assert 32 ** 3 == 32768 and 10 ** 3 == 1000
BR = Brand2(19, ['Quake 9 vs quake 6:', 'how much more energy?'], 'Quake 9 vs 6: how much more energy?',
            [('A', '1,000×'), ('B', '32,000×'), ('C', '1,000,000×')],
            [('About 32,000×', BLACK, 120, GOLD), ('more energy  ·  Source: USGS', BOLD, 44, WHITE)],
            [('The shaking? Only', BOLD, 48, WHITE), ('1,000× bigger', BLACK, 96, GOLD)], T_STOP, T_TWIST, DUR,
            sub='Guess A, B or C · wait for the 9', cta='Comment your letter', q_size=84)
RESULT = {'A': 'out', 'B': 'win', 'C': 'out'}


def mag(t):
    if t >= T_STOP:
        return 9.0
    return 6.0 + 3.0 * (1 - (1 - max(0.0, t) / T_STOP) ** 1.8)


def lvl(t):
    return (mag(t) - 6) / 3


PEN, CYL, SPEED, HALF = 800, 760, 260.0, 300.0
GROUND = 1268
YY = np.linspace(0, 1, H)[:, None, None]
BGA = (np.array((14, 11, 28)) * (1 - YY) + np.array((5, 5, 12)) * YY)
BGA = np.broadcast_to(BGA, (H, W, 3)).astype(np.float32).copy()
yy, xx = np.mgrid[0:H, 0:W]
REDGLOW = (np.clip(1 - np.sqrt(((xx - 540) / 900) ** 2 + ((yy - 1500) / 700) ** 2), 0, 1) ** 2)[..., None] * np.array((150, 30, 20))
del yy, xx
rng = np.random.default_rng(9)
SKY = []
x = -30
while x < W + 30:
    w = int(rng.uniform(80, 150)); h = int(rng.uniform(60, 165))
    wins = [(int(rng.uniform(10, w - 22)), int(rng.uniform(18, h - 26))) for _ in range(max(1, w * h // 7000))]
    SKY.append((x, w, h, wins)); x += w + int(rng.uniform(6, 18))


def wave(tau):
    return (0.55 * math.sin(2 * math.pi * 2.3 * tau) + 0.30 * math.sin(2 * math.pi * 3.7 * tau + 1.0)
            + 0.22 * math.sin(2 * math.pi * 6.1 * tau + 2.0))


def amp(tau):
    raw = 0.6 * 10 ** (mag(tau) - 6) + 2.5
    return HALF * math.tanh(raw / HALF)


def fmt_mult(v):
    if v < 10:
        return f'×{v:.1f}'
    if v < 1000:
        return f'×{v:,.0f}'
    return f'×{int(round(v, -1 if v < 10000 else -2)):,}'


def frame_core(t):
    L = lvl(t)
    arr = BGA + REDGLOW * (0.25 + 0.9 * L)
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')
    tf = min(t, T_STOP)                           # the pen freezes at the STOP
    c = Canvas()
    for gy in (CYL - 300, CYL, CYL + 300):
        c.line([(40, gy), (1040, gy)], fill=(120, 110, 160, 28), width=2)
    pts = []
    for i in range(0, PEN - 30, 4):
        tau = tf - i / SPEED
        pts.append((PEN - i, CYL + amp(tau) * wave(tau)))
    hot = (255, int(70 + 110 * L), int(55 + 45 * L))
    c.line(pts, fill=hot + (255,), width=5)
    px, py = pts[0]
    c.circle(px, py, 11, fill=(255, 235, 220, 255))
    hero = glow(c.down(), radius=26, strength=1.0)
    comp(img, hero, 0.45 + 0.55 * ease_io(ramp(t, 1.0, 1.5)))
    # skyline: gentle sway only (no flicker, no collapse)
    sway = 14 * L ** 2 * math.sin(2 * math.pi * 1.1 * t) * (1 if t < T_STOP else max(0.0, 1 - (t - T_STOP) / 0.8))
    s = Canvas()
    for (bx, bw, bh, wins) in SKY:
        top = GROUND - bh
        s.polygon([(bx, GROUND), (bx + bw, GROUND), (bx + bw + sway, top), (bx + sway, top)], fill=(16, 13, 26, 255))
        for wx, wy in wins:
            f = 1 - wy / bh
            s.rect([bx + wx + sway * f, top + wy, bx + wx + 9 + sway * f, top + wy + 12], fill=(255, 200, 120, 120))
    s.rect([0, GROUND, W, H], fill=(9, 8, 15, 255))
    img.alpha_composite(s.down())
    # one number
    ca = 1 - ramp(t, T_TWIST - 0.1, T_TWIST + 0.2)
    if ca > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        m = mag(t)
        ld.text((W / 2, 1316), f'MAGNITUDE {m:.1f}', font=font(SEMI, 32), fill=(200, 200, 220), anchor='mm')
        ld.text((W / 2, 1382), '×32,768 energy' if t >= T_STOP else fmt_mult(32 ** (m - 6)) + ' energy',
                font=font(BLACK, 76), fill=GOLD if t >= T_STOP else WHITE, anchor='mm')
        comp(img, lay, ca)
    return BR.overlay(img, t, RESULT)


render_frame = looped(frame_core, DUR, xf=0.4)


def music(mu):
    mu.bed(0, T_STOP, cutoff=lambda tt: 0.03 + 0.12 * lvl(tt), vol=lambda tt: (0.03 + 0.12 * lvl(tt) ** 1.5) * clamp(tt / 0.05), seed=31)
    mu.drone(0, T_STOP, lambda tt: 38 + 10 * lvl(tt), vol=0.05)
    rate = lambda tt: 3.0 * 2 ** ((mag(tt) - 6) * 2.1)
    mu.click_train(0, T_STOP - 0.3, rate, vol=0.24, tone=1500)
    mu.click_train(3.5, T_STOP - 0.3, lambda tt: 2 * rate(tt), vol=0.06, tone=2400)
    for mm in (7, 8):
        lo, hi = 0.0, T_STOP
        for _ in range(30):
            md = (lo + hi) / 2
            lo, hi = (lo, md) if mag(md) >= mm else (md, hi)
        mu.boom(hi, 0.45, 1.2)
    for hb in (T_STOP - 1.5, T_STOP - 1.08, T_STOP - 0.72):
        mu.thump(hb, 0.5)
    mu.silence(T_STOP - 0.32, T_STOP)
    mu.stop_signature(T_STOP)
    mu.boom(T_STOP + 0.02, 0.9, 2.0)
    mu.bed(T_STOP + 0.4, DUR, cutoff=lambda tt: 0.02, vol=lambda tt: 0.012, seed=5)
    mu.bell(T_TWIST, 659.25, 0.2, -0.3); mu.bell(T_TWIST + 0.1, 987.77, 0.2, 0.3)


if __name__ == '__main__':
    main(render_frame, DUR, music, sys.argv)
