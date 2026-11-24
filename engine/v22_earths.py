"""v6 FACT 022 The Moon is how many Earths away? (Earth-Moon distance in Earth widths) 13 s, no teaser (even number).
Human-scale size arm of the topic test ("how many Y fit in Z"); wording: centre-to-centre distance in Earth widths, not "fit between".
Sources: NASA, science.nasa.gov/moon/facts (read 22 Nov 2026): average distance 384,400 km.
NASA NSSDC Earth Fact Sheet (read 24 Nov 2026): volumetric mean radius 6,371.000 km -> diameter 12,742 km.
384,400 / 12,742 = 30.17 -> "about 30 Earth widths". Twist: light (299,792.458 km/s, SI) crosses it in 1.28 s -> 1.3 s.
Hero: a line of Earths placed one by one from our Earth towards the Moon. One number: Earths placed."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from scipy.interpolate import PchipInterpolator
from lib import *
from lib2 import big_text
from brand2 import *

DUR, T_STOP, T_TWIST = 13.0, 9.6, 11.0
KM, D_EARTH, C = 384_400, 2 * 6371, 299_792.458
N = KM / D_EARTH
assert D_EARTH == 12_742 and round(N, 2) == 30.17 and round(N) == 30
assert round(KM / C, 2) == 1.28                               # twist: 1.3 s for light
assert round(10 / N * 100) == 33 and round(20 / N * 100) == 66   # milestone labels: a third / two thirds

KEYS = [(0, 1.0), (1.4, 3.6), (2.9, 9.6), (3.6, 10.15), (5.6, 19.4), (6.4, 20.2), (8.6, 29.2), (9.6, N)]
_P = PchipInterpolator([k[0] for k in KEYS], [k[1] for k in KEYS])


def count(t):
    return float(_P(min(max(t, 0.0), T_STOP)))


def t_at(v):
    lo, hi = 0.0, T_STOP
    for _ in range(40):
        md = (lo + hi) / 2
        lo, hi = (lo, md) if count(md) >= v else (md, hi)
    return hi


MILESTONES = [(10, t_at(10), ['10 Earths', 'a third of the way']),
              (20, t_at(20), ['20 Earths', 'two thirds of the way'])]
BR = Brand2(22, ['The Moon is how', 'many Earths away?'], 'The Moon is how many Earths away?',
            [('A', '3'), ('B', '30'), ('C', '300')],
            [('About 30 Earths', BLACK, 112, GOLD), ('side by side', BOLD, 44, WHITE), ('384,400 km ÷ 12,742 km  ·  Source: NASA', BOLD, 36, WHITE)],
            [('Light crosses that gap in', BOLD, 48, WHITE), ('1.3 seconds', BLACK, 72, GOLD)], T_STOP, T_TWIST, DUR,
            sub='Wait for the Moon', cta='Comment your letter', q_size=80)
RESULT = {'A': 'out', 'B': 'win', 'C': 'out'}

# straight route, bottom left -> top right; 30.17 Earth diameters long
P0 = np.array([110.0, 1770.0])
P1 = np.array([945.0, 890.0])
DIR = (P1 - P0) / np.linalg.norm(P1 - P0)
STEP = np.linalg.norm(P1 - P0) / N              # one Earth diameter on screen
RE = STEP / 2 - 1.5
MOON_R = 15
rng = np.random.default_rng(22)
STARS = [(rng.uniform(0, W), rng.uniform(80, 1800), rng.uniform(0.9, 2.3), rng.uniform(0, 6.28)) for _ in range(160)]


def pos(i):
    """Centre of Earth number i (0 = ours)."""
    return P0 + DIR * STEP * i


def background():
    ys = np.linspace(0, 1, H)[:, None, None]
    top, bot = np.array((6, 8, 24)), np.array((14, 18, 42))
    arr = np.broadcast_to(top * (1 - ys) + bot * ys, (H, W, 3)).astype(np.uint8)
    return Image.fromarray(np.ascontiguousarray(arr), 'RGB').convert('RGBA')


BG_IMG = background()


def earth(c, x, y, r, a=255):
    c.circle(x, y, r, fill=(36, 92, 190, a))
    c.ellipse([x - r * 0.6, y - r * 0.45, x + r * 0.1, y + r * 0.15], fill=(70, 160, 95, a))
    c.ellipse([x + r * 0.05, y + r * 0.05, x + r * 0.6, y + r * 0.6], fill=(70, 160, 95, a))


def frame_core(t):
    v = count(t)
    img = BG_IMG.copy()
    c = Canvas()
    for sx, sy, sr, ph in STARS:
        c.circle(sx, sy, sr, fill=(255, 255, 255, int(150 * (0.75 + 0.25 * math.sin(ph + t * 0.6)))))
    # faint guide of the whole gap
    for k in range(0, 61):
        px, py = P0 + (P1 - P0) * k / 60
        c.circle(px, py, 2.5, fill=(180, 190, 230, 60))
    img.alpha_composite(c.down())
    hc = Canvas()
    whole = int(math.floor(v))
    for i in range(0, min(whole, 30)):
        x, y = pos(i + 0.5)
        if i == whole - 1 and i != 0 and t < T_STOP:
            s = ease_out(clamp((v - whole) * 3 + 0.4))
            earth(hc, x, y, RE * (0.4 + 0.6 * s), int(255 * s))
        else:
            earth(hc, x, y, RE, 255)
    hc.circle(P1[0], P1[1], MOON_R, fill=(220, 220, 212, 255))
    hc.circle(P1[0] - 4, P1[1] - 3, 4, fill=(184, 184, 176, 255))
    img.alpha_composite(glow(hc.down(), radius=16, strength=0.45))
    for vv, tp, txt in MILESTONES:
        al = ease_io(ramp(t, tp - 0.2, tp + 0.05)) * (1 - ease_io(ramp(t, tp + 0.9, tp + 1.15)))
        if al > 0.02 and t < T_STOP:
            lb, _ = big_text([(txt[0], XB, 56, WHITE), (txt[1], BOLD, 40, GOLD)], 0)
            sub = lb.crop(lb.getbbox())
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            lay.alpha_composite(sub, (70, 640))
            comp(img, lay, al)
    ca = 1 - ramp(t, T_TWIST - 0.1, T_TWIST + 0.2)
    if ca > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(lay)
        val = '30' if t >= T_STOP else f'{int(v)}'
        x0 = 830
        dd.text((x0 + 4, 1294), val, font=font(BLACK, 150), fill=(0, 0, 0, 120), anchor='mm')
        dd.text((x0, 1290), val, font=font(BLACK, 150), fill=GOLD if t >= T_STOP else WHITE, anchor='mm')
        dd.text((x0, 1390), 'Earth' if val == '1' else 'Earths', font=font(BOLD, 44), fill=(220, 224, 236), anchor='mm')
        comp(img, lay, ca)
    return BR.overlay(img, t, RESULT)


render_frame = looped(frame_core, DUR, xf=0.5)


def music(mu):
    from brand import drum_track, ding, drop_hit
    lvl = lambda tt: count(tt) / N
    mu.bed(0, T_STOP, cutoff=lambda tt: 0.05 + 0.06 * lvl(tt), vol=lambda tt: (0.015 + 0.04 * lvl(tt)) * clamp(tt / 0.05), seed=22)
    drum_track(mu, T_STOP - 0.32, lvl, bpm0=96, bpm1=150, key=0, roll=1.4)
    for vv, tp, _ in MILESTONES:
        ding(mu, tp, key=0, vol=0.15, pan=-0.4 if vv == 10 else 0.4)
    mu.silence(T_STOP - 0.32, T_STOP)
    drop_hit(mu, T_STOP, key=0)
    mu.bed(T_STOP + 0.4, DUR, cutoff=lambda tt: 0.02, vol=lambda tt: 0.01, seed=7)
    mu.bell(T_TWIST, 659.25, 0.16, -0.3); mu.bell(T_TWIST + 0.1, 987.77, 0.16, 0.3)


if __name__ == '__main__':
    main(render_frame, DUR, music, sys.argv)
