"""v3.1 FACT 001 - Fold paper 42 times. How thick?
0.1 mm x 2^42 = 439,805 km > Moon 384,400 km (mean). Chips: A Everest (8,849 m, passed at fold 27),
B The Moon (correct), C Mars (closest approach ~55 million km: never reached). Twist: record is 12 folds
(Britney Gallivan, 2002)."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from lib import *
from brand import *

DUR, T_STOP, T_TWIST = 10.5, 7.3, 8.7
N0, NMAX = 3.0, 42
assert round(0.1e-6 * 2 ** 42) == 439805 and 0.1e-6 * 2 ** 41 < 384400 < 0.1e-6 * 2 ** 42
BR = Brand(1, ['Fold paper 42 times.', 'How thick?'], [('A', 'Everest'), ('B', 'The Moon'), ('C', 'Mars')],
           [('Past the Moon', BLACK, 124, GOLD), ('0.1 mm, doubled 42 times', BOLD, 46, WHITE)],
           [('Real-world record:', BOLD, 48, WHITE), ('12 folds', BLACK, 100, GOLD)], T_STOP, T_TWIST, DUR)


def nfold(t):
    if t >= T_STOP:
        return float(NMAX)
    return N0 + (NMAX - N0) * (1 - (1 - t / T_STOP) ** 1.7)


def nvis(t):
    """Visual fold: holds, then snaps to the next doubling in the last 30% of each fold's time slot."""
    n = nfold(t)
    if n >= NMAX:
        return float(NMAX)
    k = math.floor(n)
    return k + ease_io(clamp((n - k - 0.7) / 0.3))


def alt(n):
    return 0.1e-3 * 2 ** n


def t_at(a):
    lo, hi = 0.0, T_STOP
    for _ in range(40):
        m = (lo + hi) / 2
        lo, hi = (lo, m) if alt(nvis(m)) >= a else (m, hi)
    return hi


SX, MY, PX = 540, 1000, 340
LM = {'Burj Khalifa': 828, 'Everest': 8849, 'Space Station': 408000, 'The Moon': 384400000}
PASS = {k: t_at(v) for k, v in LM.items()}


def fmt(m):
    if m < 0.01: return f'{m * 1000:.1f} mm'
    if m < 1: return f'{m * 100:.0f} cm'
    if m < 1000: return f'{m:,.0f} m'
    if m < 100000: return f'{m / 1000:.1f} km'
    return f'{m / 1000:,.0f} km'


def lerp(a, b, x):
    return tuple(int(a[i] + (b[i] - a[i]) * x) for i in range(3))


def sky(lh):
    st = [(-4, (24, 64, 140), (60, 115, 185)), (2.5, (20, 55, 135), (52, 104, 178)),
          (4, (14, 34, 100), (40, 86, 165)), (5, (6, 8, 30), (14, 24, 70)), (6, (3, 4, 12), (6, 8, 22))]
    for (a, t0, b0), (b, t1, b1) in zip(st, st[1:]):
        if lh <= b:
            x = clamp((lh - a) / (b - a))
            return lerp(t0, t1, x), lerp(b0, b1, x)
    return st[-1][1], st[-1][2]


rng = np.random.default_rng(2)
STARS = [(rng.uniform(0, W), rng.uniform(0, 1440), rng.uniform(1, 3.2)) for _ in range(170)]
STREAKS = [(rng.uniform(0, W), rng.uniform(0, 1440), rng.uniform(60, 180)) for _ in range(16)]
YY = np.linspace(0, 1, H)[:, None, None]


def states(t):
    st = {'A': 'out' if t >= PASS['Everest'] else 'idle'}
    st['B'] = 'win' if t >= T_STOP else 'idle'
    st['C'] = 'out' if t >= T_STOP else 'idle'
    pops = {'A': math.exp(-(t - PASS['Everest']) * 6) if t >= PASS['Everest'] else 0,
            'B': math.exp(-(t - T_STOP) * 5) if t >= T_STOP else 0}
    return st, pops


def frame_core(t):
    n = nvis(t)
    h = alt(n)
    lh = math.log10(h)
    speed = (math.log10(alt(nfold(t + 0.02))) - math.log10(alt(nfold(t)))) / 0.02 if t < T_STOP else 0   # decades/s
    top, bot = sky(lh)
    arr = np.broadcast_to((np.array(top) * (1 - YY) + np.array(bot) * YY), (H, W, 3)).astype(np.uint8)
    img = Image.fromarray(arr, 'RGB').convert('RGBA')
    d = ImageDraw.Draw(img, 'RGBA')
    sh = 0.0
    if T_STOP - 1.6 < t < T_STOP:
        sh = 9 * ((t - (T_STOP - 1.6)) / 1.6) ** 2
    ox, oy = sh * math.sin(t * 91), sh * math.cos(t * 77)
    sa = clamp((lh - 4.3) / 1.0)
    if sa > 0:
        for sx, sy, sr in STARS:
            v = int(255 * sa * (0.55 + 0.45 * math.sin(sx + t * 2)))
            d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(v, v, v))
    # speed streaks
    for sx, sy, ln in STREAKS:
        y = (sy + t * speed * 700) % 1600 - 100
        a = int(min(34, speed * 9) * clamp((t - 0.8) / 0.6))
        if a > 3:
            d.line([sx, y, sx, y + ln * min(1.5, speed / 2)], fill=(255, 255, 255, a), width=2)
    ys = {k: MY - (math.log10(v) - lh) * PX + oy for k, v in LM.items()}
    # Everest silhouette (right)
    y = ys['Everest']
    if y < 1700:
        d.polygon([(760 + ox, y), (1180 + ox, y + 620), (360 + ox, y + 620)], fill=(40, 52, 80))
        d.polygon([(760 + ox, y), (830 + ox, y + 100), (790 + ox, y + 90), (760 + ox, y + 120), (715 + ox, y + 70)],
                  fill=(225, 232, 245))
    # Burj Khalifa silhouette (left)
    y = ys['Burj Khalifa']
    if y < 1900:
        d.polygon([(250 + ox, y), (262 + ox, y + 120), (282 + ox, y + 300), (310 + ox, y + 900),
                   (190 + ox, y + 900), (218 + ox, y + 300), (238 + ox, y + 120)], fill=(30, 40, 66))
    # ISS (right)
    y = ys['Space Station']
    if -100 < y < 1500:
        cx = 260 + ox
        d.rectangle([cx - 90, y - 3, cx + 90, y + 3], fill=(200, 205, 215))
        for dx in (-80, -45, 45, 80):
            d.rectangle([cx + dx - 14, y - 34, cx + dx + 14, y + 34], fill=(70, 110, 190), outline=(200, 205, 215))
        d.rectangle([cx - 18, y - 9, cx + 18, y + 9], fill=(230, 232, 240))
    # Moon (behind the stack)
    y = ys['The Moon']
    if -200 < y < 1700:
        r = 175
        d.ellipse([SX - r + ox, y - r, SX + r + ox, y + r], fill=(214, 212, 222))
        for cx_, cy_, cr in ((-0.35, -0.2, 0.22), (0.3, 0.25, 0.16), (0.1, -0.45, 0.1), (-0.1, 0.45, 0.12)):
            d.ellipse([SX + ox + (cx_ - cr) * r, y + (cy_ - cr) * r, SX + ox + (cx_ + cr) * r, y + (cy_ + cr) * r],
                      fill=(172, 170, 184))
    # stack
    d.rectangle([SX - 46 + ox, MY + oy, SX + 46 + ox, 1440], fill=(246, 244, 236))
    off = (n * 60) % 16
    for yy in np.arange(MY + oy + off, 1440, 16):
        d.line([SX - 46 + ox, yy, SX + 46 + ox, yy], fill=(206, 202, 192), width=2)
    d.rectangle([SX - 52 + ox, MY - 6 + oy, SX + 52 + ox, MY + 2 + oy], fill=GOLD)
    # fade the stack into the bottom zone
    fade = Image.new('RGBA', (W, 740), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fade)
    for i in range(740):
        fd.line([0, i, W, i], fill=bot + (int(255 * clamp(i / 300) ** 0.8),))
    img.alpha_composite(fade, (0, 1180))
    # one label at a time, only while crossing
    for k, y in ys.items():
        a = clamp(1 - abs(y - MY) / 110)
        if a > 0.02 and t < T_STOP:
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(lay).text((SX + 80, MY - 30), k, font=font(XB, 54), fill=WHITE, anchor='lm')
            comp(img, lay, a)
    # single counter
    d = ImageDraw.Draw(img)
    val = '439,805 km' if t >= T_STOP else fmt(alt(int(n + 0.5)))
    ca = 1 - ramp(t, T_TWIST - 0.1, T_TWIST + 0.15)
    if ca > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(lay).text((W / 2, 1360), val, font=font(BLACK, 108), fill=GOLD if t >= T_STOP else WHITE, anchor='mm')
        comp(img, lay, ca)
    st, pops = states(t)
    BR.overlay(img, t, st, pops)
    return punch(img, t, T_STOP)


render_frame = looped(frame_core, DUR)


def music(m):
    lhs = lambda tt: (math.log10(alt(nfold(tt))) + 4) / 12.6        # 0 at 0.1 mm, ~1 at the Moon
    m.bed(0, T_STOP, cutoff=lambda tt: 0.9 - 0.85 * clamp(lhs(tt) * 1.15),
          vol=lambda tt: 0.05 * (1 - 0.7 * clamp(lhs(tt) * 1.2)) * clamp(tt / 0.05), seed=3)
    m.drone(0, T_STOP, lambda tt: 55 + 2.4 * nfold(tt), vol=0.05)
    k = int(N0) + 1
    for i in range(1, int(T_STOP * 400)):
        tt = i / 400
        if nvis(tt) >= k - 0.5:
            m.pluck(tt, note_freq(min(3 + (k - 3) // 2 + (k % 2) * 2, 16)), vol=0.17, pan=0.45 if k % 2 else -0.45)
            k += 1
    pans = {'Burj Khalifa': (-0.9, 0.2), 'Everest': (0.9, -0.2), 'Space Station': (0.8, -0.6), 'The Moon': (-0.3, 0.3)}
    for name, pt in PASS.items():
        m.whoosh(pt - 0.35, 0.8, 0.3, *pans[name])
        m.bell(pt, 1567.98 if name != 'The Moon' else 1046.5, 0.14, pan=pans[name][1])
    for hb in (T_STOP - 1.5, T_STOP - 1.08, T_STOP - 0.72):
        m.thump(hb, 0.5)
    m.silence(T_STOP - 0.32, T_STOP)
    m.stop_signature(T_STOP)
    m.bed(T_STOP + 0.4, DUR, cutoff=lambda tt: 0.02, vol=lambda tt: 0.012, seed=5)
    m.bell(T_TWIST, 659.25, 0.2, -0.3); m.bell(T_TWIST + 0.1, 987.77, 0.2, 0.3)


if __name__ == '__main__':
    main(render_frame, DUR, music, sys.argv)
