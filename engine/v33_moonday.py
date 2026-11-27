"""v6 FACT 033 How long is one day on the Moon? 13 s, + next-up teaser (odd number).
Non-human-scale arm of the topic test; a "tempting wrong answer" fact (24 hours) like #018/#027/#031.
Source: ESA, "Moon facts: A day on the Moon" (2021): "The Moon takes around 29.53 Earth days to rotate once on its
axis. So if you lived on the Moon you would experience about two weeks of day and two weeks of night."
NASA (Top Moon Questions) gives the same 29.5 days from new moon to new moon (the Moon's solar day).
Milestones: noon after 29.53/4 = 7.4 Earth days; sunset after 29.53/2 = 14.8. Twist: then about two weeks of night.
Hero: a lunar horizon with Earth hanging in the black sky; the Sun crawls up, across and down, then night."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from scipy.interpolate import PchipInterpolator
from lib import *
from lib2 import big_text
from brand2 import *

DUR, T_STOP, T_TWIST = 13.0, 9.6, 11.0
LDAY = 29.53
NOON, SUNSET = LDAY / 4, LDAY / 2
assert round(NOON, 1) == 7.4 and round(SUNSET, 1) == 14.8 and round(LDAY, 1) == 29.5

KEYS = [(0, 0.0), (1.4, 2.4), (3.2, 7.25), (4.1, 7.55), (5.8, 14.62), (6.7, 14.95), (8.7, 28.9), (9.6, LDAY)]
_P = PchipInterpolator([k[0] for k in KEYS], [k[1] for k in KEYS])


def days(t):
    return float(_P(min(max(t, 0.0), T_STOP)))


def t_at(v):
    lo, hi = 0.0, T_STOP
    for _ in range(40):
        md = (lo + hi) / 2
        lo, hi = (lo, md) if days(md) >= v else (md, hi)
    return hi


MILESTONES = [(NOON, t_at(NOON), ['Noon', '7.4 Earth days in']),
              (SUNSET, t_at(SUNSET), ['Sunset', '14.8 days: now night'])]
BR = Brand2(33, ['How long is one day', 'on the Moon?'], 'How long is one day on the Moon?',
            [('A', '24 hours'), ('B', '7 days'), ('C', '29.5 days')],
            [('29.5 Earth days', BLACK, 100, GOLD), ('Sunrise to sunrise (ESA: 29.53 days)', BOLD, 36, WHITE)],
            [('Then the night lasts', BOLD, 48, WHITE), ('about 2 weeks', BLACK, 80, GOLD)], T_STOP, T_TWIST, DUR,
            sub='Wait for the next sunrise', cta='Comment your letter', q_size=84,
            next_line='Next: FACT 034 · Count your cells, 1 a second: how long?')
RESULT = {'A': 'out', 'B': 'out', 'C': 'win'}

HZ = 1180                     # horizon y
AX, AY, AR = 540, HZ, 400     # Sun's arc
EX, EY, ER = 850, 820, 52     # Earth


def sky():
    ys = np.linspace(0, 1, H)[:, None, None]
    top, bot = np.array((2, 2, 6)), np.array((6, 6, 14))
    arr = np.broadcast_to(top * (1 - ys) + bot * ys, (H, W, 3)).astype(np.uint8)
    img = Image.fromarray(np.ascontiguousarray(arr), 'RGB').convert('RGBA')
    return img


def stars():
    c = Canvas()
    rng = np.random.default_rng(33)
    for _ in range(170):
        c.circle(rng.uniform(0, W), rng.uniform(0, HZ - 10), rng.uniform(0.8, 1.9), fill=(225, 230, 255, int(rng.uniform(70, 200))))
    return c.down()


def ground(lit):
    c = Canvas()
    g = int(70 + 110 * lit)
    c.polygon([(0, HZ + 18), (180, HZ - 6), (420, HZ + 8), (700, HZ - 12), (W, HZ + 10), (W, H), (0, H)], fill=(g, g, g + 6, 255))
    rng = np.random.default_rng(5)
    for _ in range(26):
        x, y, r = rng.uniform(0, W), rng.uniform(HZ + 40, HZ + 260), rng.uniform(10, 46)
        c.ellipse([x - r, y - r * 0.32, x + r, y + r * 0.32], fill=(int(g * 0.72), int(g * 0.72), int(g * 0.75), 255))
    return c.down()


def earth():
    c = Canvas()
    c.circle(EX, EY, ER, fill=(40, 96, 190, 255))
    c.ellipse([EX - 30, EY - 28, EX + 6, EY + 6], fill=(70, 140, 80, 255))
    c.ellipse([EX + 4, EY + 8, EX + 34, EY + 34], fill=(70, 140, 80, 255))
    c.circle(EX - 12, EY + 30, 14, fill=(235, 240, 250, 200))
    c.circle(EX, EY, ER, outline=(160, 200, 255, 220), width=2)
    return c.down()


SKY, STARS, EARTH = sky(), stars(), earth()
G_DARK, G_LIT = ground(0.0), ground(1.0)


def sun_pos(d):
    th = math.pi * (d / SUNSET)
    return AX - AR * math.cos(th), AY - AR * 0.9 * math.sin(th)


def daylight(d):
    dd = d % LDAY
    if dd <= SUNSET:
        return max(0.0, math.sin(math.pi * dd / SUNSET)) ** 0.5
    return 0.0


def frame_core(t):
    d = days(t)
    lit = daylight(d)
    img = SKY.copy()
    comp(img, STARS, 1 - 0.6 * lit)
    img.alpha_composite(EARTH)
    # the Sun (hero): visible from sunrise to sunset and again at the next sunrise
    dd = d % LDAY if d < LDAY - 1e-6 else 0.0
    vis = dd <= SUNSET or d >= LDAY - 0.3
    if vis:
        sx, sy = sun_pos(min(dd, SUNSET) if d < LDAY - 0.3 else 0.0)
        hc = Canvas()
        hc.circle(sx, sy, 44, fill=(255, 236, 180, 255))
        hc.circle(sx, sy, 44, outline=(255, 214, 102, 255), width=4)
        comp(img, glow(hc.down(), radius=26, strength=0.9), 1.0)
    img.alpha_composite(G_DARK)
    comp(img, G_LIT, lit)
    for vv, tp, txt in MILESTONES:
        al = ease_io(ramp(t, tp - 0.2, tp + 0.05)) * (1 - ease_io(ramp(t, tp + 0.9, tp + 1.15)))
        if al > 0.02 and t < T_STOP:
            lb, _ = big_text([(txt[0], XB, 52, WHITE), (txt[1], BOLD, 42, GOLD)], 0)
            sub = lb.crop(lb.getbbox())
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            lay.alpha_composite(sub, ((W - sub.width) // 2, 470))
            comp(img, lay, al)
    ca = 1 - ramp(t, T_TWIST - 0.1, T_TWIST + 0.2)
    if ca > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        dd2 = ImageDraw.Draw(lay)
        val = f'{LDAY:.1f} days' if t >= T_STOP else f'{d:.1f} days'
        dd2.rounded_rectangle([250, 1322, 830, 1440], radius=40, fill=(6, 6, 14, 215))
        dd2.text((W / 2 + 4, 1385), val, font=font(BLACK, 84), fill=(0, 0, 0, 150), anchor='mm')
        dd2.text((W / 2, 1381), val, font=font(BLACK, 84), fill=GOLD if t >= T_STOP else WHITE, anchor='mm')
        comp(img, lay, ca)
    return BR.overlay(img, t, RESULT)


render_frame = looped(frame_core, DUR, xf=0.5)


def music(mu):
    from brand import drum_track, ding, drop_hit
    lvl = lambda tt: days(tt) / LDAY
    mu.bed(0, T_STOP, cutoff=lambda tt: 0.05 + 0.06 * lvl(tt), vol=lambda tt: (0.015 + 0.04 * lvl(tt)) * clamp(tt / 0.05), seed=33)
    drum_track(mu, T_STOP - 0.32, lvl, bpm0=96, bpm1=150, key=-3, roll=1.4)
    for vv, tp, _ in MILESTONES:
        ding(mu, tp, key=-3, vol=0.15, pan=0.4 if vv < 10 else -0.4)
    mu.silence(T_STOP - 0.32, T_STOP)
    drop_hit(mu, T_STOP, key=-3)
    mu.bed(T_STOP + 0.4, DUR, cutoff=lambda tt: 0.02, vol=lambda tt: 0.01, seed=17)
    mu.bell(T_TWIST, 659.25, 0.16, -0.3); mu.bell(T_TWIST + 0.1, 987.77, 0.16, 0.3)


if __name__ == '__main__':
    main(render_frame, DUR, music, sys.argv)
