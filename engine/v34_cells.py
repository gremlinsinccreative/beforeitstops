"""v6 FACT 034 Count your cells, 1 a second: how long? 13 s, no teaser (even number).
Human-scale arm of the topic test (committed by #033's teaser).
Source: Sender, Fuchs & Milo, "Revised Estimates for the Number of Human and Bacteria Cells in the Body",
PLoS Biol 14(8): e1002533 (2016), PMC4991899: "This leaves us with 3.0·10^13 human cells in the 70 kg
'reference man'" (abstract: "about 30 trillion human cells"). BioNumbers 113006.
3.0e13 s / 31,557,600 s per Julian year = 950,643 years.
Milestones (arithmetic only): one 80-year life = 2.52 billion cells = 0.008% counted; 100,000 years = 10.5% counted.
Twist: a whole lifetime counts just 0.008% of them.
Hero: a body silhouette made of cells that fills from the feet up with exactly the fraction counted so far
(true scale: invisible for most of the count, then it floods in the last seconds)."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from scipy.interpolate import PchipInterpolator
from lib import *
from lib2 import big_text
from brand2 import *

DUR, T_STOP, T_TWIST = 13.0, 9.6, 11.0
CELLS = 3.0e13
YEAR_S = 365.25 * 86400
Y_TOTAL = CELLS / YEAR_S
LIFE = 80
assert YEAR_S == 31_557_600 and round(Y_TOTAL) == 950_643 and round(Y_TOTAL, -4) == 950_000
LIFE_PCT = LIFE * YEAR_S / CELLS * 100
assert round(LIFE * YEAR_S / 1e9, 2) == 2.52 and round(LIFE_PCT, 3) == 0.008
assert round(100_000 / Y_TOTAL * 100, 1) == 10.5

U0, U1 = -2.0, math.log10(Y_TOTAL)
UL, UH = math.log10(LIFE), 5.0
KEYS = [(0, U0), (1.4, 0.5), (3.2, 1.86), (4.1, 1.95), (5.8, 4.97), (6.8, 5.03), (8.7, 5.75), (9.6, U1)]
_P = PchipInterpolator([k[0] for k in KEYS], [k[1] for k in KEYS])


def u(t):
    return float(_P(min(max(t, 0.0), T_STOP)))


def t_at(v):
    lo, hi = 0.0, T_STOP
    for _ in range(40):
        md = (lo + hi) / 2
        lo, hi = (lo, md) if u(md) >= v else (md, hi)
    return hi


MILESTONES = [(UL, t_at(UL), ['One lifetime (80 years)', '0.008% counted']),
              (UH, t_at(UH), ['100,000 years', '10.5% counted'])]
BR = Brand2(34, ['Count your cells,', '1 every second.', 'How long?'],
            'Count your cells, 1 a second: how long?',
            [('A', '95 years'), ('B', '950,000 years'), ('C', '95 million years')],
            [('About 950,000 years', BLACK, 92, GOLD), ('30 trillion cells (Sender et al., PLoS Biol 2016)', BOLD, 34, WHITE)],
            [('A whole lifetime counts', BOLD, 48, WHITE), ('just 0.008% of them', BLACK, 80, GOLD)], T_STOP, T_TWIST, DUR,
            sub='Wait for your last cell', cta='Comment your letter', q_size=80)
RESULT = {'A': 'out', 'B': 'win', 'C': 'out'}

FEET, HEAD = 1270, 610           # body spans y 610..1270
CX = W / 2


def body_shape(c, fill):
    c.circle(CX, HEAD + 62, 62, fill=fill)                                   # head
    c.rect([CX - 34, HEAD + 112, CX + 34, HEAD + 150], fill=fill)            # neck
    c.rect([CX - 112, HEAD + 140, CX + 112, HEAD + 420], fill=fill, radius=56)   # torso
    for s in (-1, 1):
        c.line([(CX + s * 104, HEAD + 180), (CX + s * 168, HEAD + 330), (CX + s * 188, HEAD + 460)], fill=fill, width=54)  # arms
        c.circle(CX + s * 188, HEAD + 466, 30, fill=fill)
        c.line([(CX + s * 58, HEAD + 390), (CX + s * 72, HEAD + 560), (CX + s * 80, FEET - 30)], fill=fill, width=72)  # legs
        c.rect([CX + s * 80 - 44, FEET - 44, CX + s * 80 + 44, FEET], fill=fill, radius=20)


def _mask():
    c = Canvas()
    body_shape(c, (255, 255, 255, 255))
    return np.asarray(c.down().getchannel('A'), np.float32) / 255


MASK = _mask()
YY = np.arange(H, dtype=np.float32)[:, None]


def _cells_tex():
    """Faint hexagonal cell pattern inside the body (the 'empty' cells)."""
    c = Canvas()
    r = 13
    for j, y in enumerate(np.arange(HEAD - 10, FEET + 10, r * 1.7)):
        off = (r * 1.0) if j % 2 else 0
        for x in np.arange(CX - 260 + off, CX + 260, r * 2.0):
            c.circle(x, y, r * 0.78, outline=(120, 200, 230, 120), width=1.6)
    a = np.asarray(c.down(), np.float32)
    a[:, :, 3] *= MASK
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def background():
    ys = np.linspace(0, 1, H)[:, None, None]
    top, bot = np.array((3, 10, 16)), np.array((10, 44, 58))
    arr = np.broadcast_to(top * (1 - ys ** 1.4) + bot * ys ** 1.4, (H, W, 3)).astype(np.uint8)
    img = Image.fromarray(np.ascontiguousarray(arr), 'RGB').convert('RGBA')
    c = Canvas()
    rng = np.random.default_rng(34)
    for _ in range(70):           # drifting free-floating cells, static and faint
        x, y, r = rng.uniform(0, W), rng.uniform(300, 1400), rng.uniform(5, 16)
        c.circle(x, y, r, outline=(90, 170, 190, int(rng.uniform(25, 70))), width=1.4)
    img.alpha_composite(c.down())
    sil = Image.new('RGBA', (W, H), (14, 40, 54, 0))
    sil.putalpha(Image.fromarray((MASK * 200).astype(np.uint8), 'L'))
    img.alpha_composite(sil)
    img.alpha_composite(_cells_tex())
    return img


BG_IMG = background()
_GOLD_FILL = np.zeros((H, W, 4), np.uint8)
_GOLD_FILL[:, :, :3] = (255, 196, 92)


def fill_layer(frac):
    yline = FEET - frac * (FEET - HEAD)
    a = MASK * np.clip((YY - yline) / 3.0 + 0.5, 0, 1)
    arr = _GOLD_FILL.copy()
    arr[:, :, 3] = (a * 235).astype(np.uint8)
    return Image.fromarray(arr, 'RGBA'), yline


def fmt_count(uu, stopped):
    if stopped:
        return f'{Y_TOTAL:,.0f} years'
    y = 10 ** uu
    if y < 1:
        return f'{int(y * 365.25)} days'
    if y < 2:
        return '1 year'
    return f'{int(y):,} years'


def frame_core(t):
    uu = u(t)
    frac = min(1.0, 10 ** uu / Y_TOTAL)
    img = BG_IMG.copy()
    fl, yline = fill_layer(frac)
    k = 1 - 0.6 * ease_io(ramp(t, T_TWIST - 0.1, T_TWIST + 0.3))
    if frac > 0.002:
        hc = Canvas()
        hc.line([(CX - 270, yline), (CX + 270, yline)], fill=(255, 226, 150, 200), width=3)
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        lay.alpha_composite(fl)
        lay.alpha_composite(hc.down())
        comp(img, glow(lay, radius=16, strength=0.55), k)
    else:                         # nothing visible yet: a thin gold rim at the feet shows where it starts
        hc = Canvas()
        hc.line([(CX - 140, FEET + 6), (CX + 140, FEET + 6)], fill=(255, 214, 102, 230), width=5)
        comp(img, glow(hc.down(), radius=12, strength=0.6), k)
    for vv, tp, txt in MILESTONES:
        al = ease_io(ramp(t, tp - 0.2, tp + 0.05)) * (1 - ease_io(ramp(t, tp + 0.9, tp + 1.15)))
        if al > 0.02 and t < T_STOP:
            lb, _ = big_text([(txt[0], XB, 50, WHITE), (txt[1], BOLD, 42, GOLD)], 0)
            sub = lb.crop(lb.getbbox())
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            lay.alpha_composite(sub, ((W - sub.width) // 2, 410))
            comp(img, lay, al)
    ca = 1 - ramp(t, T_TWIST - 0.1, T_TWIST + 0.2)
    if ca > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(lay)
        val = fmt_count(uu, t >= T_STOP)
        dd.rounded_rectangle([190, 1322, 890, 1440], radius=40, fill=(4, 10, 16, 215))
        dd.text((W / 2 + 4, 1385), val, font=font(BLACK, 80), fill=(0, 0, 0, 150), anchor='mm')
        dd.text((W / 2, 1381), val, font=font(BLACK, 80), fill=GOLD if t >= T_STOP else WHITE, anchor='mm')
        comp(img, lay, ca)
    return BR.overlay(img, t, RESULT)


render_frame = looped(frame_core, DUR, xf=0.5)


def music(mu):
    from brand import drum_track, ding, drop_hit
    lvl = lambda tt: (u(tt) - U0) / (U1 - U0)
    mu.bed(0, T_STOP, cutoff=lambda tt: 0.05 + 0.06 * lvl(tt), vol=lambda tt: (0.015 + 0.04 * lvl(tt)) * clamp(tt / 0.05), seed=34)
    drum_track(mu, T_STOP - 0.32, lvl, bpm0=96, bpm1=150, key=2, roll=1.4)
    for vv, tp, _ in MILESTONES:
        ding(mu, tp, key=2, vol=0.15, pan=0.4 if vv < 3 else -0.4)
    mu.silence(T_STOP - 0.32, T_STOP)
    drop_hit(mu, T_STOP, key=2)
    mu.bed(T_STOP + 0.4, DUR, cutoff=lambda tt: 0.02, vol=lambda tt: 0.01, seed=19)
    mu.bell(T_TWIST, 659.25, 0.16, -0.3); mu.bell(T_TWIST + 0.1, 987.77, 0.16, 0.3)


if __name__ == '__main__':
    main(render_frame, DUR, music, sys.argv)
