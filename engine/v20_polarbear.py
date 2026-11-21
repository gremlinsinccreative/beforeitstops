"""v6 FACT 020 Longest polar bear swim ever tracked? 13 s, no teaser (even number, A/B rule).
Source: USGS, Durner et al. (2011) Polar Biology 34(7):975-984: a radio-collared adult female in the Beaufort Sea
made "a continuous swim of 687 km over 9 days" (late Aug - late Oct 2008) and "lost 22% of her body mass".
Hero: one swimming bear in open dark sea; the ice she left drifts away, night falls, stars come out; at day 9 the
pack ice slides in. One number: days in the water (eased curve that slows at day 3 and day 6)."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from scipy.interpolate import PchipInterpolator
from lib import *
from lib2 import big_text
from brand2 import *

DUR, T_STOP, T_TWIST = 13.0, 9.6, 11.0
KM, DAYS, MASS = 687, 9, 22
assert round(KM / DAYS, 1) == 76.3          # ~76 km a day (used nowhere on screen; sanity only)
KEYS = [(0, 0.0), (1.6, 1.25), (2.9, 2.9), (3.6, 3.06), (5.2, 5.9), (6.0, 6.06), (8.4, 8.85), (9.6, 9.0)]
_P = PchipInterpolator([k[0] for k in KEYS], [k[1] for k in KEYS])


def days(t):
    return float(_P(min(max(t, 0.0), T_STOP)))


def t_at(dv):
    lo, hi = 0.0, T_STOP
    for _ in range(40):
        md = (lo + hi) / 2
        lo, hi = (lo, md) if days(md) >= dv else (md, hi)
    return hi


MILESTONES = [(3, t_at(3.0), ['3 days in the sea', 'no ice in sight']), (6, t_at(6.0), ['6 days', 'still swimming'])]
BR = Brand2(20, ['Longest polar bear swim', 'ever tracked?'], 'Longest polar bear swim ever tracked?',
            [('A', '1 day'), ('B', '9 days'), ('C', '3 hours')],
            [('9 days nonstop', BLACK, 116, GOLD), ('687 km  ·  Source: USGS (Durner et al. 2011)', BOLD, 38, WHITE)],
            [('On the way she lost', BOLD, 48, WHITE), ('22% of her body mass', BLACK, 64, GOLD)], T_STOP, T_TWIST, DUR,
            sub='Wait for the ice', cta='Comment your letter', q_size=80)
RESULT = {'A': 'out', 'B': 'win', 'C': 'out'}

HZ = 820                                       # horizon
BX, BY = 560, 1080                             # bear head position
YY = np.linspace(0, 1, H)[:, None]
rng = np.random.default_rng(20)
STARS = [(rng.uniform(0, W), rng.uniform(150, HZ - 40), rng.uniform(1.0, 2.4), rng.uniform(0, 6.28)) for _ in range(120)]
WAVES = [(rng.uniform(0, 1), rng.uniform(0, 1), rng.uniform(0.6, 1.0)) for _ in range(70)]


def sky_sea(n):
    """n: 0 dusk .. 1 deep night. Smooth, monotone."""
    st, sb = np.array((52, 78, 128)) * (1 - n) + np.array((8, 12, 30)) * n, np.array((150, 140, 170)) * (1 - n) + np.array((22, 34, 66)) * n
    wt, wb = np.array((40, 66, 100)) * (1 - n) + np.array((14, 26, 48)) * n, np.array((8, 18, 34)) * (1 - n) + np.array((3, 7, 16)) * n
    arr = np.zeros((H, W, 3), np.float32)
    ys = np.arange(H)[:, None]
    ks = np.clip(ys / HZ, 0, 1)
    kw = np.clip((ys - HZ) / (H - HZ), 0, 1) ** 0.7
    sky = st * (1 - ks) + sb * ks
    sea = wt * (1 - kw) + wb * kw
    col = np.where(ys < HZ, sky, sea)
    arr[:] = col[:, None, :]
    return Image.fromarray(arr.astype(np.uint8), 'RGB').convert('RGBA')


def floe(c, cx, cy, s, a=255, seed=0):
    r = np.random.default_rng(seed)
    pts = []
    for i in range(11):
        ang = 2 * math.pi * i / 11
        rr = 1 + r.uniform(-0.18, 0.18)
        pts.append((cx + math.cos(ang) * 230 * s * rr, cy + math.sin(ang) * 46 * s * rr))
    c.polygon([(x, y + 10 * s) for x, y in pts], fill=(120, 150, 180, int(a * 0.8)))
    c.polygon(pts, fill=(232, 240, 248, a))


def bear(c, x, y):
    w = (236, 236, 228, 255)
    c.ellipse([x - 230, y + 6, x - 20, y + 70], fill=(226, 226, 218, 255))      # back, just above the water
    c.circle(x - 6, y - 22, 13, fill=w); c.circle(x + 50, y - 26, 13, fill=w)     # ears
    c.circle(x - 6, y - 22, 6, fill=(190, 186, 180, 255)); c.circle(x + 50, y - 26, 6, fill=(190, 186, 180, 255))
    c.ellipse([x - 30, y - 20, x + 80, y + 62], fill=w)                         # head
    c.ellipse([x + 40, y + 10, x + 118, y + 58], fill=w)                         # snout
    c.circle(x + 112, y + 26, 9, fill=(20, 20, 26, 255))                         # nose
    c.circle(x + 44, y + 12, 5, fill=(20, 20, 26, 255))                          # eye


def frame_core(t):
    d = days(t)
    n = clamp(d / 4.5) ** 0.8
    img = sky_sea(n)
    c = Canvas()
    if n > 0.05:
        for sx, sy, sr, ph in STARS:
            c.circle(sx, sy, sr, fill=(255, 255, 255, int(220 * clamp((n - 0.05) / 0.6) * (0.8 + 0.2 * math.sin(ph + t * 0.5)))))
    mx, my = 880 - 50 * t / DUR, 640 + 20 * t / DUR                       # moon drifts slowly
    c.circle(mx, my, 44, fill=(238, 236, 226, int(255 * clamp(n * 1.3) * ramp(t, 1.2, 2.0))))
    # sparse wave crests in perspective, drifting left (the bear swims right)
    for u, v, s in WAVES:
        depth = v ** 1.6
        y = HZ + 12 + depth * (H - HZ)
        if y > 1460:
            continue
        sc = 0.25 + 1.6 * depth
        x = ((u - t * 0.025 * (0.4 + sc)) % 1.2 - 0.1) * W
        c.line([(x - 28 * sc, y), (x, y - 3 * sc), (x + 28 * sc, y)], fill=(150, 180, 210, int(70 * s * (1 - 0.5 * n))), width=max(1, 1.6 * sc))
    # the ice she left: drifts away left and shrinks toward the horizon during day 1
    k = ease_io(clamp(d / 1.3))
    if k < 1:
        floe(c, 150 - 480 * k, 1175 - 320 * k, 0.85 - 0.65 * k, int(255 * (1 - k ** 3)), seed=3)
    # day 9: the pack ice slides in from the right
    m = ease_out(ramp(t, 7.6, 9.6))
    if m > 0:
        floe(c, 1400 - 420 * m, 960 + 40 * m, 1.3, int(255 * clamp(m * 2)), seed=8)
        floe(c, 1250 - 300 * m, HZ + 24, 0.55, int(255 * clamp(m * 2)), seed=11)
    img.alpha_composite(c.down())
    # wake + ripples behind the bear
    bob = 5 * math.sin(2 * math.pi * t / 2.6)
    bx, by = BX, BY + bob
    wc = Canvas()
    for i in range(4):
        ph = ((t / 1.6) + i / 4) % 1
        rx, ry = 120 + 380 * ph, 22 + 70 * ph
        wc.ellipse([bx - 60 - rx, by + 52 - ry, bx - 60 + rx, by + 52 + ry], outline=(190, 215, 235, int(90 * (1 - ph) ** 1.5)), width=3)
    wc.line([(bx + 100, by + 58), (bx - 340, by + 20)], fill=(210, 230, 245, 70), width=3)
    wc.line([(bx + 100, by + 64), (bx - 340, by + 110)], fill=(210, 230, 245, 70), width=3)
    img.alpha_composite(wc.down())
    hc = Canvas()
    bear(hc, bx, by)
    hl = hc.down()
    # water line: hide everything of the bear below by+52
    a = np.array(hl)
    cut = int(by + 52)
    a[cut:, :, 3] = (a[cut:, :, 3] * 0.12).astype(np.uint8)
    img.alpha_composite(glow(Image.fromarray(a, 'RGBA'), radius=26, strength=0.45))
    # milestone labels (left side, away from the bear's face)
    for dv, tp, txt in MILESTONES:
        al = ease_io(ramp(t, tp - 0.2, tp + 0.05)) * (1 - ease_io(ramp(t, tp + 0.9, tp + 1.15)))
        if al > 0.02 and t < T_STOP:
            lb, _ = big_text([(txt[0], XB, 58, WHITE), (txt[1], BOLD, 40, GOLD)], 0)
            sub = lb.crop(lb.getbbox())
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            lay.alpha_composite(sub, (70, 880))
            comp(img, lay, al)
    ca = 1 - ramp(t, T_TWIST - 0.1, T_TWIST + 0.2)
    if ca > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(lay)
        val = f'{DAYS} days' if t >= T_STOP else (f'{d:.1f} days' if d < 9 else '9 days')
        dd.text((W / 2 + 4, 1324), val, font=font(BLACK, 104), fill=(0, 0, 0, 120), anchor='mm')
        dd.text((W / 2, 1320), val, font=font(BLACK, 104), fill=GOLD if t >= T_STOP else WHITE, anchor='mm')
        comp(img, lay, ca)
    return BR.overlay(img, t, RESULT)


render_frame = looped(frame_core, DUR, xf=0.5)


def music(mu):
    from brand import drum_track, ding, drop_hit
    lvl = lambda tt: days(tt) / 9
    mu.bed(0, T_STOP, cutoff=lambda tt: 0.05 + 0.06 * lvl(tt), vol=lambda tt: (0.015 + 0.04 * lvl(tt)) * clamp(tt / 0.05), seed=20)
    drum_track(mu, T_STOP - 0.32, lvl, bpm0=96, bpm1=148, key=-2, roll=1.4)
    for dv, tp, _ in MILESTONES:
        ding(mu, tp, key=-2, vol=0.15, pan=-0.4 if dv == 3 else 0.4)
    mu.silence(T_STOP - 0.32, T_STOP)
    drop_hit(mu, T_STOP, key=-2)
    mu.bed(T_STOP + 0.4, DUR, cutoff=lambda tt: 0.02, vol=lambda tt: 0.01, seed=5)
    mu.bell(T_TWIST, 659.25 * 2 ** (-2 / 12), 0.16, -0.3); mu.bell(T_TWIST + 0.1, 987.77 * 2 ** (-2 / 12), 0.16, 0.3)


if __name__ == '__main__':
    main(render_frame, DUR, music, sys.argv)
