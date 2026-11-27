"""v6 FACT 032 Stack people head to toe up to the space station: how many? 13 s, no teaser (even number).
Human-scale size arm of the topic test. Premise on screen: 1.7 m per person.
Source: NASA, "What Is the International Space Station?" (Grades 5-8, updated 18 Nov 2026): "It orbits Earth at an
average altitude of approximately 250 miles." 250 mi x 1.609344 = 402.336 km. 402,336 m / 1.7 m = 236,668 people.
Milestones: Everest 8,849 m (Nepal-China survey 2020, as in #025) -> 5,205 people; 100 km, the Karman line used by the
FAI as the edge of space -> 58,824 people. Twist: Everest needs only 5,205.
Hero: a glowing column of people rising from Earth's horizon past Everest and the edge of space to the ISS.
Height axis is logarithmic (marked 'height not to scale' on screen) so all three landmarks fit one frame."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from scipy.interpolate import PchipInterpolator
from lib import *
from lib2 import big_text
from brand2 import *

DUR, T_STOP, T_TWIST = 13.0, 9.6, 11.0
PERSON = 1.7
ISS_M = 250 * 1609.344
EVEREST, KARMAN = 8849.0, 100_000.0
N_ISS, N_EV, N_KA = round(ISS_M / PERSON), round(EVEREST / PERSON), round(KARMAN / PERSON)
assert round(ISS_M, 0) == 402336 and N_ISS == 236668 and N_EV == 5205 and N_KA == 58824
assert round(N_ISS, -3) == 237000

U0, U1 = math.log10(PERSON), math.log10(ISS_M)          # log10 metres
UE, UK = math.log10(EVEREST), math.log10(KARMAN)
KEYS = [(0, U0), (1.4, 1.9), (3.2, 3.925), (4.1, 3.965), (5.8, 4.975), (6.8, 5.012), (8.7, 5.57), (9.6, U1)]
_P = PchipInterpolator([k[0] for k in KEYS], [k[1] for k in KEYS])


def u(t):
    return float(_P(min(max(t, 0.0), T_STOP)))


def t_at(v):
    lo, hi = 0.0, T_STOP
    for _ in range(40):
        md = (lo + hi) / 2
        lo, hi = (lo, md) if u(md) >= v else (md, hi)
    return hi


MILESTONES = [(UE, t_at(UE), ['Everest', '5,205 people']),
              (UK, t_at(UK), ['Edge of space (100 km)', '58,824 people'])]
BR = Brand2(32, ['Stack people head to toe', 'up to the space station.', 'How many?'],
            'Stack people up to the space station: how many?',
            [('A', '237,000'), ('B', '2,370'), ('C', '23.7 million')],
            [('About 237,000 people', BLACK, 92, GOLD), ('ISS ≈ 250 miles up (NASA) = 402 km ÷ 1.7 m', BOLD, 34, WHITE)],
            [('Everest needs only', BOLD, 48, WHITE), ('5,205 of them', BLACK, 80, GOLD)], T_STOP, T_TWIST, DUR,
            sub='Wait for the space station · 1.7 m each', cta='Comment your letter', q_size=72)
RESULT = {'A': 'win', 'B': 'out', 'C': 'out'}

GROUND, TOPY = 1262, 800
COLX = 560


def ypos(uu):
    return GROUND - (uu - U0) / (U1 - U0) * (GROUND - TOPY)


def background():
    ys = np.linspace(0, 1, H)[:, None, None]
    top, bot = np.array((2, 3, 10)), np.array((22, 44, 92))
    arr = np.broadcast_to(top * (1 - ys ** 1.6) + bot * ys ** 1.6, (H, W, 3)).astype(np.uint8)
    img = Image.fromarray(np.ascontiguousarray(arr), 'RGB').convert('RGBA')
    c = Canvas()
    rng = np.random.default_rng(32)
    for _ in range(120):
        c.circle(rng.uniform(0, W), rng.uniform(0, ypos(UK)), rng.uniform(0.8, 1.8), fill=(220, 226, 255, int(rng.uniform(40, 140))))
    # Earth: a wide curved horizon
    c.circle(W / 2, GROUND + 2200, 2200, fill=(26, 70, 140, 255))
    c.circle(W / 2, GROUND + 2200, 2200, outline=(120, 180, 255, 160), width=6)
    c.circle(W / 2, GROUND + 2215, 2200, fill=(34, 92, 60, 255))
    # Everest, drawn to the log axis
    ye = ypos(UE)
    c.polygon([(150, GROUND + 8), (330, ye), (400, ye + 70), (470, GROUND + 8)], fill=(120, 124, 140, 255))
    c.polygon([(330, ye), (300, ye + 60), (345, ye + 45), (372, ye + 44)], fill=(236, 240, 248, 255))
    # edge of space: dashed line
    yk = ypos(UK)
    for x in range(40, W - 40, 36):
        c.line([(x, yk), (x + 18, yk)], fill=(150, 170, 220, 140), width=2)
    # ISS
    yi = ypos(U1)
    c.rect([COLX - 26, yi - 12, COLX + 26, yi + 12], fill=(210, 214, 224, 255))
    for s in (-1, 1):
        c.rect([COLX + s * 36 - 26, yi - 26, COLX + s * 36 + 26, yi + 26] if False else
               [min(COLX + s * 34, COLX + s * 110), yi - 22, max(COLX + s * 34, COLX + s * 110), yi + 22],
               fill=(60, 90, 170, 255), outline=(200, 210, 240, 255), width=2)
    img.alpha_composite(c.down())
    return img


BG_IMG = background()
_sm = font(SEMI, 26)


def person(c, x, y, s, col):
    c.circle(x, y - 3.2 * s, s, fill=col)
    c.line([(x, y - 2.2 * s), (x, y - 0.2 * s)], fill=col, width=1.4 * s)
    c.line([(x - 1.1 * s, y - 1.6 * s), (x + 1.1 * s, y - 1.6 * s)], fill=col, width=1.0 * s)


def frame_core(t):
    uu = u(t)
    yt = ypos(uu)
    img = BG_IMG.copy()
    hc = Canvas()
    hc.line([(COLX, GROUND), (COLX, yt)], fill=(255, 214, 102, 255), width=8)
    person(hc, COLX, yt - 4, 7, (255, 226, 140, 255))
    comp(img, glow(hc.down(), radius=14, strength=0.6), 1 - 0.7 * ease_io(ramp(t, T_TWIST - 0.1, T_TWIST + 0.3)))
    wa = ease_io(ramp(t, HOOK_END + 0.1, HOOK_END + 0.4)) * (1 - ease_io(ramp(t, T_STOP - 0.3, T_STOP)))
    if wa > 0.02:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(lay)
        dd.text((W - 60, GROUND - 24), 'height not to scale', font=_sm, fill=(170, 180, 205), anchor='rm')
        dd.text((COLX + 130, ypos(U1)), 'ISS', font=font(BOLD, 34), fill=(225, 230, 245), anchor='lm')
        comp(img, lay, wa)
    for vv, tp, txt in MILESTONES:
        al = ease_io(ramp(t, tp - 0.2, tp + 0.05)) * (1 - ease_io(ramp(t, tp + 0.9, tp + 1.15)))
        if al > 0.02 and t < T_STOP:
            lb, _ = big_text([(txt[0], XB, 50, WHITE), (txt[1], BOLD, 42, GOLD)], 0)
            sub = lb.crop(lb.getbbox())
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            lay.alpha_composite(sub, ((W - sub.width) // 2, 450))
            comp(img, lay, al)
    ca = 1 - ramp(t, T_TWIST - 0.1, T_TWIST + 0.2)
    if ca > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(lay)
        n = N_ISS if t >= T_STOP else max(1, int(10 ** uu / PERSON))
        val = f'{n:,}'
        dd.rounded_rectangle([250, 1322, 830, 1440], radius=40, fill=(4, 8, 20, 215))
        dd.text((W / 2 + 4, 1385), val, font=font(BLACK, 88), fill=(0, 0, 0, 150), anchor='mm')
        dd.text((W / 2, 1381), val, font=font(BLACK, 88), fill=GOLD if t >= T_STOP else WHITE, anchor='mm')
        comp(img, lay, ca)
    return BR.overlay(img, t, RESULT)


render_frame = looped(frame_core, DUR, xf=0.5)


def music(mu):
    from brand import drum_track, ding, drop_hit
    lvl = lambda tt: (u(tt) - U0) / (U1 - U0)
    mu.bed(0, T_STOP, cutoff=lambda tt: 0.05 + 0.06 * lvl(tt), vol=lambda tt: (0.015 + 0.04 * lvl(tt)) * clamp(tt / 0.05), seed=32)
    drum_track(mu, T_STOP - 0.32, lvl, bpm0=96, bpm1=150, key=0, roll=1.4)
    for vv, tp, _ in MILESTONES:
        ding(mu, tp, key=0, vol=0.15, pan=0.4 if vv < 4.5 else -0.4)
    mu.silence(T_STOP - 0.32, T_STOP)
    drop_hit(mu, T_STOP, key=0)
    mu.bed(T_STOP + 0.4, DUR, cutoff=lambda tt: 0.02, vol=lambda tt: 0.01, seed=17)
    mu.bell(T_TWIST, 659.25, 0.16, -0.3); mu.bell(T_TWIST + 0.1, 987.77, 0.16, 0.3)


if __name__ == '__main__':
    main(render_frame, DUR, music, sys.argv)
