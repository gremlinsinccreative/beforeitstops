"""TEST B - Quake 9 vs quake 6: how much more energy?
USGS (Earthquake Hazards Program, 'Earthquake Magnitude, Energy Release, and Shaking Intensity'): each whole-number
step = 10x measured amplitude and about 32x more energy. 3 steps: 32^3 = 32,768 (about 32,000x) energy;
10^3 = 1,000x amplitude. Chips: A 1,000x (the amplitude trap, struck when the energy passes 1,000x),
B 32,000x (correct), C 1,000,000x (struck at the stop). All four competitor lessons: sound as payoff
(ticks fuse into a rising note), stakes (a city), a promise line ('wait for the 9'), a comment prompt."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from lib import *
from brand import *

DUR, T_STOP, T_TWIST = 10.5, 7.3, 8.7
assert 32 ** 3 == 32768 and 10 ** 3 == 1000
BR = Brand(19, ['Quake 9 vs quake 6:', 'how much more energy?'],
           [('A', '1,000×'), ('B', '32,000×'), ('C', '1,000,000×')],
           [('About 32,000×', BLACK, 120, GOLD), ('more energy  ·  Source: USGS', BOLD, 44, WHITE)],
           [('The shaking? Only', BOLD, 48, WHITE), ('1,000× bigger', BLACK, 96, GOLD)], T_STOP, T_TWIST, DUR,
           sub='Guess A, B or C · wait for the 9', cta='Comment your letter', q_size=84)


def mag(t):
    if t >= T_STOP:
        return 9.0
    x = t / T_STOP
    return 6.0 + 3.0 * (1 - (1 - x) ** 1.8)


def mult(m):
    return 32 ** (m - 6)


def t_at(mm):
    lo, hi = 0.0, T_STOP
    for _ in range(40):
        md = (lo + hi) / 2
        lo, hi = (lo, md) if mag(md) >= mm else (md, hi)
    return hi


T1000 = t_at(6 + math.log(1000, 32))
CX, CY, RMAX = 540, 760, 400               # energy ball: area proportional to energy
GROUND = 1290
rng = np.random.default_rng(9)
BUILD = []
x = -20
while x < W + 20:
    w = int(rng.uniform(70, 150))
    h = int(rng.uniform(140, 420))
    thr = rng.uniform(7.6, 8.95)
    wins = [(int(rng.uniform(8, w - 20)), int(rng.uniform(15, h - 30))) for _ in range(max(3, w * h // 2600))]
    BUILD.append((x, w, h, thr, wins))
    x += w + int(rng.uniform(4, 16))
COLLAPSE = sorted((t_at(b[3]), b[0] + b[1] / 2) for b in BUILD)
YY = np.linspace(0, 1, H)[:, None, None]
BGA = np.broadcast_to((np.array((14, 10, 30)) * (1 - YY) + np.array((40, 18, 30)) * YY), (H, W, 3)).astype(np.uint8)
STARS = [(rng.uniform(0, W), rng.uniform(0, 1100), rng.uniform(0.8, 2.2)) for _ in range(120)]


def ball_sprite(r):
    s = int(2 * r * 1.6) + 4
    yy, xx = np.mgrid[0:s, 0:s]
    d = np.sqrt((xx - s / 2) ** 2 + (yy - s / 2) ** 2) / max(r, 1)
    core = np.clip(1 - d, 0, 1)
    halo = np.clip(1 - (d - 1) / 0.6, 0, 1) * (d > 1)
    a = np.clip(core * 0 + (d <= 1) * 1.0 + halo ** 2 * 0.5, 0, 1)
    col = np.dstack([255 * np.ones_like(d), 120 + 120 * core, 40 + 160 * core ** 2])
    return Image.fromarray(np.dstack([col, a * 255]).astype(np.uint8), 'RGBA')


def fmt_mult(v):
    if v < 10:
        return f'×{v:.1f}'
    if v < 1000:
        return f'×{v:,.0f}'
    return f'×{int(round(v, -1 if v < 10000 else -2)):,}'


def states(t):
    st = {'A': 'out' if t >= T1000 else 'idle', 'B': 'win' if t >= T_STOP else 'idle', 'C': 'out' if t >= T_STOP else 'idle'}
    pops = {'A': math.exp(-(t - T1000) * 6) if t >= T1000 else 0, 'B': math.exp(-(t - T_STOP) * 5) if t >= T_STOP else 0}
    return st, pops


def frame_core(t):
    m = mag(t)
    sh = 0 if t >= T_STOP + 0.6 else 1.2 * (m - 6) ** 2.4 * (1 if t < T_STOP else max(0, 1 - (t - T_STOP) / 0.6))
    ox, oy = sh * math.sin(t * 83), sh * math.cos(t * 71)
    img = Image.fromarray(BGA, 'RGB').convert('RGBA')
    d = ImageDraw.Draw(img, 'RGBA')
    for sx, sy, sr in STARS:
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(200, 200, 230, 150))
    # seismograph: trace swing grows 10x per magnitude step (USGS: 10x amplitude); runs off the chart near M9
    PX0, PX1, PY0, PY1 = 70, 1010, 495, 1120
    pc = (PY0 + PY1) / 2
    d.rounded_rectangle([PX0 + ox * 0.3, PY0 + oy * 0.3, PX1 + ox * 0.3, PY1 + oy * 0.3], radius=18,
                        fill=(20, 16, 30, 210), outline=(90, 80, 120, 160), width=2)
    for gy in range(int(PY0) + 40, int(PY1), 60):
        d.line([PX0 + 12, gy, PX1 - 12, gy], fill=(80, 70, 110, 70), width=1)
    pen = PX1 - 150
    pts = []
    for i in range(0, int(pen - PX0 - 10), 3):
        xx = pen - i
        tau = t - i / 300
        mm = mag(max(0.0, tau)) if tau < T_STOP else 9.0
        if tau > T_STOP + 0.25:
            amp_ = 0.5 * 10 ** (3) * math.exp(-(tau - T_STOP) * 2.5)
        else:
            amp_ = 0.5 * 10 ** (mm - 6)
        n = (math.sin(tau * 61.0) * 0.6 + math.sin(tau * 97.3 + 1.3) * 0.3 + math.sin(tau * 23.7 + 0.4) * 0.4)
        yv = max(PY0 + 8, min(PY1 - 8, pc + amp_ * n + 3 * math.sin(tau * 5)))
        pts.append((xx + ox * 0.3, yv + oy * 0.3))
    if len(pts) > 1:
        d.line(pts, fill=(255, 80, 70, 255), width=4, joint='curve')
        d.ellipse([pts[0][0] - 9, pts[0][1] - 9, pts[0][0] + 9, pts[0][1] + 9], fill=(255, 200, 190))
    if 0.5 * 10 ** (m - 6) * 1.0 > (PY1 - PY0) / 2 - 10 and t < T_STOP:
        d.text((PX1 - 24 + ox * 0.3, PY0 + 36), 'OFF THE CHART', font=font(XB, 40), fill=(255, 90, 80), anchor='rm')
    # city
    d = ImageDraw.Draw(img, 'RGBA')
    for (bx, bw, bh, thr, wins) in BUILD:
        tc = t_at(thr)
        k = clamp((t - tc) / 0.5) if t >= tc else 0.0
        if k >= 1:
            # rubble
            d.polygon([(bx + ox, GROUND), (bx + bw / 2 + ox, GROUND - 26), (bx + bw + ox, GROUND)], fill=(22, 18, 30))
            continue
        top = GROUND - bh * (1 - ease_in(k))
        tilt = 30 * ease_in(k) * (1 if int(bx) % 2 else -1)
        d.polygon([(bx + ox, GROUND + oy * 0.3), (bx + bw + ox, GROUND + oy * 0.3),
                   (bx + bw + ox + tilt, top + oy), (bx + ox + tilt, top + oy)], fill=(22, 18, 34))
        lights_on = True
        for wx, wy in wins:
            yy = GROUND - bh + wy
            if yy < top:
                continue
            flick = (int(wx * 7 + wy * 3 + t * 20) % (9 if m < 8.2 else 3) != 0) if m > 7.6 else True
            if lights_on and flick:
                d.rectangle([bx + wx + ox + tilt * (1 - (yy - top) / max(1, GROUND - top)), yy + oy,
                             bx + wx + 9 + ox + tilt * (1 - (yy - top) / max(1, GROUND - top)), yy + 12 + oy],
                            fill=(255, 210, 120, 200))
    d.rectangle([0, GROUND, W, H], fill=(12, 10, 18))
    # one big number: energy multiple; small magnitude label
    ca = 1 - ramp(t, T_TWIST - 0.1, T_TWIST + 0.15)
    if ca > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        ld.text((W / 2, 1318), f'MAGNITUDE {m:.1f}', font=font(SEMI, 34), fill=(225, 225, 240), anchor='mm')
        val = '×32,768' if t >= T_STOP else fmt_mult(mult(m))
        ld.text((W / 2, 1388), val, font=font(BLACK, 96), fill=GOLD if t >= T_STOP else WHITE, anchor='mm')
        comp(img, lay, ca)
    st, pops = states(t)
    BR.overlay(img, t, st, pops)
    return punch(img, t, T_STOP)


render_frame = looped(frame_core, DUR)


def music(mu):
    lvl = lambda tt: (mag(tt) - 6) / 3
    mu.bed(0, T_STOP, cutoff=lambda tt: 0.03 + 0.12 * lvl(tt), vol=lambda tt: (0.03 + 0.12 * lvl(tt) ** 1.5) * clamp(tt / 0.05), seed=31)
    mu.drone(0, T_STOP, lambda tt: 38 + 10 * lvl(tt), vol=0.05)
    rate = lambda tt: 3.0 * 2 ** ((mag(tt) - 6) * 2.1)
    mu.click_train(0, T_STOP - 0.3, rate, vol=0.26, tone=1500)
    mu.click_train(3.5, T_STOP - 0.3, lambda tt: 2 * rate(tt), vol=0.07, tone=2400)
    for tc, bxc in COLLAPSE:
        if tc < T_STOP - 0.3:
            pan = bxc / W * 1.6 - 0.8
            mu.boom(tc, 0.35, 0.8, pan=pan)
            mu.whoosh(tc, 0.7, 0.16, pan, pan, bright=0.6)
    mu.bell(T1000, 1567.98, 0.14, -0.5)
    for hb in (T_STOP - 1.5, T_STOP - 1.08, T_STOP - 0.72):
        mu.thump(hb, 0.5)
    mu.silence(T_STOP - 0.32, T_STOP)
    mu.stop_signature(T_STOP)
    mu.boom(T_STOP + 0.02, 0.9, 2.0)
    mu.bed(T_STOP + 0.4, DUR, cutoff=lambda tt: 0.02, vol=lambda tt: 0.012, seed=5)
    mu.bell(T_TWIST, 659.25, 0.2, -0.3); mu.bell(T_TWIST + 0.1, 987.77, 0.2, 0.3)


if __name__ == '__main__':
    main(render_frame, DUR, music, sys.argv)
