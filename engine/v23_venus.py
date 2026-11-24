"""v6 FACT 023 Which planet is the hottest? 13 s, + next-up teaser (odd number).
Non-human-scale arm of the topic test; 'settle it' style (most people say Mercury), like #018's "204, not 64".
Sources: NASA, science.nasa.gov/venus/facts (read 24 Nov 2026): Venus is "the hottest planet in our solar system,
with surface temperatures hot enough to melt lead"; "900 degrees Fahrenheit (475 Celsius)".
Mercury's highest surface temperature 800 F (430 C): NASA Solar System Temperatures page, as cited by Live Science
(12 Sep 2026). Lead melts at 327.5 C (standard melting point), water boils at 100 C at sea level.
Replaces the zombie fact today (held: deadly real outbreak in the news, T&S rule).
Hero: a thermometer whose column climbs to 475 C, the bulb drawn as Venus. One number: the temperature."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from scipy.interpolate import PchipInterpolator
from lib import *
from lib2 import big_text
from brand2 import *

DUR, T_STOP, T_TWIST = 13.0, 9.6, 11.0
VENUS_C, MERCURY_C, LEAD_C, WATER_C = 475, 430, 327, 100
assert round((900 - 32) * 5 / 9) == 482 and abs(VENUS_C - 482) < 10      # NASA's rounded 900 F / 475 C agree within 10 C
assert round((800 - 32) * 5 / 9) == 427 and abs(MERCURY_C - 427) < 5      # 800 F ~ 430 C
assert VENUS_C - MERCURY_C == 45 and VENUS_C > LEAD_C

KEYS = [(0, 0.0), (1.4, 40.0), (2.9, 96.0), (3.6, 104.0), (5.6, 322.0), (6.4, 333.0), (8.6, 462.0), (9.6, VENUS_C)]
_P = PchipInterpolator([k[0] for k in KEYS], [k[1] for k in KEYS])


def temp(t):
    return float(_P(min(max(t, 0.0), T_STOP)))


def t_at(v):
    lo, hi = 0.0, T_STOP
    for _ in range(40):
        md = (lo + hi) / 2
        lo, hi = (lo, md) if temp(md) >= v else (md, hi)
    return hi


MILESTONES = [(WATER_C, t_at(WATER_C), ['100 °C', 'water boils']),
              (LEAD_C, t_at(LEAD_C), ['327 °C', 'lead melts'])]
BR = Brand2(23, ['Which planet', 'is the hottest?'], 'Which planet is the hottest?',
            [('A', 'Mercury'), ('B', 'Venus'), ('C', 'Mars')],
            [('Venus: about 475 °C', BLACK, 96, GOLD), ('Hot enough to melt lead  ·  Source: NASA', BOLD, 38, WHITE)],
            [('Mercury, closest to the Sun:', BOLD, 46, WHITE), ('only about 430 °C', BLACK, 66, GOLD)], T_STOP, T_TWIST, DUR,
            sub='Wait for the hottest', cta='Comment your letter', q_size=88,
            next_line='Next: FACT 024 · Your life as one day')
RESULT = {'A': 'out', 'B': 'win', 'C': 'out'}

TX, Y0, Y500, TW = 380, 1240, 830, 34          # tube centre x, 0 C level, 500 C level, tube half-width
BX, BY, BR_R = TX, 1318, 74                    # bulb = Venus


def ty(c):
    return Y0 - (Y0 - Y500) * c / 500


rng = np.random.default_rng(23)
STARS = [(rng.uniform(0, W), rng.uniform(80, 1800), rng.uniform(0.9, 2.2), rng.uniform(0, 6.28)) for _ in range(120)]


def background():
    ys = np.linspace(0, 1, H)[:, None, None]
    top, bot = np.array((10, 8, 20)), np.array((34, 16, 22))
    arr = np.broadcast_to(top * (1 - ys) + bot * ys, (H, W, 3)).astype(np.uint8)
    return Image.fromarray(np.ascontiguousarray(arr), 'RGB').convert('RGBA')


BG_IMG = background()


def frame_core(t):
    c_now = temp(t)
    k = c_now / VENUS_C
    img = BG_IMG.copy()
    c = Canvas()
    for sx, sy, sr, ph in STARS:
        c.circle(sx, sy, sr, fill=(255, 255, 255, int(130 * (0.75 + 0.25 * math.sin(ph + t * 0.6)))))
    c.rect([TX - TW, Y500 - 40, TX + TW, Y0 + 20], fill=(24, 22, 36, 255), outline=(150, 150, 175, 200), width=4, radius=TW)
    for v in range(0, 501, 100):
        y = ty(v)
        c.line([(TX + TW + 8, y), (TX + TW + 34, y)], fill=(170, 170, 195, 220), width=4)
    img.alpha_composite(c.down())
    d0 = ImageDraw.Draw(img)
    for v in range(0, 501, 100):
        d0.text((TX + TW + 46, ty(v)), f'{v}°', font=font(SEMI, 30), fill=(160, 160, 185), anchor='lm')
    hc = Canvas()
    col = (int(255), int(150 + 60 * (1 - k)), int(40 + 20 * (1 - k)), 255)
    hc.rect([TX - TW + 10, ty(c_now), TX + TW - 10, Y0 + 30], fill=col, radius=TW - 10)
    hc.circle(BX, BY, BR_R, fill=(236, 196, 120, 255))                       # Venus as the bulb
    for dy, a in [(-30, 90), (0, 70), (28, 90)]:
        hc.ellipse([BX - BR_R * 0.85, BY + dy - 9, BX + BR_R * 0.85, BY + dy + 9], fill=(250, 222, 160, a))
    img.alpha_composite(glow(hc.down(), radius=22, strength=0.35 + 0.4 * k))
    for vv, tp, txt in MILESTONES:
        al = ease_io(ramp(t, tp - 0.2, tp + 0.05)) * (1 - ease_io(ramp(t, tp + 0.9, tp + 1.15)))
        if al > 0.02 and t < T_STOP:
            lb, _ = big_text([(txt[0], XB, 56, WHITE), (txt[1], BOLD, 40, GOLD)], 0)
            sub = lb.crop(lb.getbbox())
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            lay.alpha_composite(sub, (620, int(ty(vv) - sub.height / 2)))
            comp(img, lay, al)
    ca = 1 - ramp(t, T_TWIST - 0.1, T_TWIST + 0.2)
    if ca > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(lay)
        val = f'{VENUS_C} °C' if t >= T_STOP else f'{int(c_now)} °C'
        x0, y0 = 760, 1330
        dd.text((x0 + 4, y0 + 4), val, font=font(BLACK, 104), fill=(0, 0, 0, 140), anchor='mm')
        dd.text((x0, y0), val, font=font(BLACK, 104), fill=GOLD if t >= T_STOP else WHITE, anchor='mm')
        comp(img, lay, ca)
    return BR.overlay(img, t, RESULT)


render_frame = looped(frame_core, DUR, xf=0.5)


def music(mu):
    from brand import drum_track, ding, drop_hit
    lvl = lambda tt: temp(tt) / VENUS_C
    mu.bed(0, T_STOP, cutoff=lambda tt: 0.05 + 0.07 * lvl(tt), vol=lambda tt: (0.015 + 0.045 * lvl(tt)) * clamp(tt / 0.05), seed=230)
    drum_track(mu, T_STOP - 0.32, lvl, bpm0=96, bpm1=150, key=0, roll=1.4)
    for vv, tp, _ in MILESTONES:
        ding(mu, tp, key=0, vol=0.15, pan=0.4)
    mu.silence(T_STOP - 0.32, T_STOP)
    drop_hit(mu, T_STOP, key=0)
    mu.bed(T_STOP + 0.4, DUR, cutoff=lambda tt: 0.02, vol=lambda tt: 0.01, seed=10)
    mu.bell(T_TWIST, 659.25, 0.16, -0.3); mu.bell(T_TWIST + 0.1, 987.77, 0.16, 0.3)


if __name__ == '__main__':
    main(render_frame, DUR, music, sys.argv)
