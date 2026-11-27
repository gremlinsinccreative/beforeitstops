"""v6 FACT 031 Lily pads double daily; the lake is full on day 48. When is it half full? 13 s, + next-up teaser (odd number).
Non-human-scale arm of the topic test; a "tempting wrong answer" puzzle like #018/#027 (Analytics 26 Nov item 2).
Source of the question: Frederick, S. (2005), "Cognitive Reflection and Decision Making", Journal of Economic
Perspectives 19(4): 25-42 (Cognitive Reflection Test, lily pad item; wording read on UBC Sauder DMIDI, 27 Nov).
The answer is pure arithmetic: the patch doubles each day, so one day before full it covers half -> day 47.
Milestones: day 40 covers 2^-8 = 0.39% of the lake; day 45 covers 2^-3 = 1/8. Twist: day 24 covers 2^-24 = 0.000006%.
Hero: a pond seen from above; the lily patch's area is 2^(day-48) of the lake (radius R*sqrt of that)."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from scipy.interpolate import PchipInterpolator
from lib import *
from lib2 import big_text
from brand2 import *

DUR, T_STOP, T_TWIST = 13.0, 9.6, 11.0
FULL, ANS = 48, 47
assert 2.0 ** (ANS - FULL) == 0.5
assert round(100 * 2.0 ** (40 - FULL), 2) == 0.39 and 2.0 ** (45 - FULL) == 0.125
assert f'{100 * 2.0 ** (24 - FULL):.6f}' == '0.000006'

KEYS = [(0, 0.0), (1.4, 14.0), (3.2, 39.3), (3.9, 40.4), (5.9, 44.6), (6.6, 45.3), (8.7, 46.8), (9.6, float(ANS))]
_P = PchipInterpolator([k[0] for k in KEYS], [k[1] for k in KEYS])


def day(t):
    return float(_P(min(max(t, 0.0), T_STOP)))


def t_at(v):
    lo, hi = 0.0, T_STOP
    for _ in range(40):
        md = (lo + hi) / 2
        lo, hi = (lo, md) if day(md) >= v else (md, hi)
    return hi


MILESTONES = [(40, t_at(40), ['Day 40', 'just 0.4% of the lake']),
              (45, t_at(45), ['Day 45', 'still only 1/8'])]
BR = Brand2(31, ['Lily pads double daily.', 'The lake is full on day 48.', 'When was it half full?'],
            'Doubles daily, full on day 48. Half?',
            [('A', '24 days'), ('B', '47 days'), ('C', '36 days')],
            [('Day 47', BLACK, 120, GOLD), ('It doubles daily: half is one day before full', BOLD, 34, WHITE)],
            [('On day 24 it covered:', BOLD, 48, WHITE), ('0.000006%', BLACK, 80, GOLD)], T_STOP, T_TWIST, DUR,
            sub='Wait for half the lake', cta='Comment your letter', q_size=70,
            next_line='Next: FACT 032 · Stack people to the ISS: how many?')
RESULT = {'A': 'out', 'B': 'win', 'C': 'out'}

CX, CY, R = 540, 1010, 310


def background():
    ys = np.linspace(0, 1, H)[:, None, None]
    top, bot = np.array((10, 20, 18)), np.array((14, 30, 24))
    arr = np.broadcast_to(top * (1 - ys) + bot * ys, (H, W, 3)).astype(np.uint8)
    img = Image.fromarray(np.ascontiguousarray(arr), 'RGB').convert('RGBA')
    c = Canvas()
    rng = np.random.default_rng(31)
    for _ in range(60):                                  # reeds / grass tufts around the bank
        a = rng.uniform(0, 2 * math.pi); rr = R + rng.uniform(22, 90)
        x, y = CX + rr * math.cos(a), CY + rr * math.sin(a)
        c.circle(x, y, rng.uniform(5, 13), fill=(40, 70, 44, int(rng.uniform(90, 170))))
    c.circle(CX, CY, R + 14, fill=(58, 52, 40, 255))      # muddy bank
    c.circle(CX, CY, R, fill=(22, 62, 88, 255))           # water
    c.circle(CX - 70, CY - 90, R * 0.55, fill=(30, 76, 104, 120))
    for k in range(5):
        c.circle(CX + 40 - k * 30, CY + 60 + k * 18, 60 + k * 45, outline=(60, 110, 140, 40), width=2)
    img.alpha_composite(c.down())
    return img


def pads_layer():
    """Lily pads covering the whole lake; the patch shows the part within its radius."""
    c = Canvas()
    rng = np.random.default_rng(7)
    pts = []
    for _ in range(2600):
        rr = R * math.sqrt(rng.uniform(0, 1)); a = rng.uniform(0, 2 * math.pi)
        pts.append((CX + rr * math.cos(a), CY + rr * math.sin(a), rng.uniform(9, 17), rng.uniform(0, 2 * math.pi)))
    c.circle(CX, CY, R, fill=(34, 96, 52, 255))
    for x, y, s, a in pts:
        g = int(rng.uniform(120, 175))
        c.circle(x, y, s, fill=(46, g, 70, 255))
        c.polygon([(x, y), (x + s * math.cos(a - 0.3), y + s * math.sin(a - 0.3)),
                   (x + s * math.cos(a + 0.3), y + s * math.sin(a + 0.3))], fill=(34, 96, 52, 255))
    for _ in range(9):                                    # a few flowers
        rr = R * math.sqrt(rng.uniform(0, 0.25)); a = rng.uniform(0, 2 * math.pi)
        c.circle(CX + rr * math.cos(a), CY + rr * math.sin(a), 7, fill=(250, 214, 226, 255))
    return c.down()


BG_IMG, PADS = background(), pads_layer()
_lbl = font(SEMI, 26)


def frame_core(t):
    d = day(t)
    r = R * math.sqrt(2.0 ** (d - FULL))
    img = BG_IMG.copy()
    if r > 0.6:
        mask = Image.new('L', (W * 2, H * 2), 0)
        ImageDraw.Draw(mask).ellipse([2 * (CX - r), 2 * (CY - r), 2 * (CX + r), 2 * (CY + r)], fill=255)
        mask = mask.resize((W, H), Image.LANCZOS)
        p = PADS.copy()
        p.putalpha(mask)
        comp(img, glow(p, radius=14, strength=0.45), 1.0)
    hc = Canvas()                                         # faint 'half the lake' ring, the target
    hc.circle(CX, CY, R / math.sqrt(2), outline=(255, 214, 102, 110), width=2)
    hc.circle(CX, CY, R, outline=(170, 200, 210, 120), width=2)
    comp(img, hc.down(), 1 - 0.7 * ease_io(ramp(t, T_TWIST - 0.1, T_TWIST + 0.3)))
    wa = ease_io(ramp(t, HOOK_END + 0.1, HOOK_END + 0.4)) * (1 - ease_io(ramp(t, T_STOP - 0.3, T_STOP)))
    if wa > 0.02:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(lay).text((CX, CY - R / math.sqrt(2) - 16), 'half the lake', font=_lbl, fill=(255, 220, 140), anchor='mb')
        comp(img, lay, wa)
    for vv, tp, txt in MILESTONES:
        al = ease_io(ramp(t, tp - 0.2, tp + 0.05)) * (1 - ease_io(ramp(t, tp + 0.9, tp + 1.15)))
        if al > 0.02 and t < T_STOP:
            lb, _ = big_text([(txt[0], XB, 52, WHITE), (txt[1], BOLD, 42, GOLD)], 0)
            sub = lb.crop(lb.getbbox())
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            lay.alpha_composite(sub, ((W - sub.width) // 2, 480))
            comp(img, lay, al)
    ca = 1 - ramp(t, T_TWIST - 0.1, T_TWIST + 0.2)
    if ca > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(lay)
        val = f'Day {ANS}' if t >= T_STOP else f'Day {int(d)}'
        dd.rounded_rectangle([290, 1342, 790, 1446], radius=40, fill=(6, 14, 12, 210))
        dd.text((W / 2 + 4, 1398), val, font=font(BLACK, 84), fill=(0, 0, 0, 150), anchor='mm')
        dd.text((W / 2, 1394), val, font=font(BLACK, 84), fill=GOLD if t >= T_STOP else WHITE, anchor='mm')
        comp(img, lay, ca)
    return BR.overlay(img, t, RESULT)


render_frame = looped(frame_core, DUR, xf=0.5)


def music(mu):
    from brand import drum_track, ding, drop_hit
    lvl = lambda tt: day(tt) / ANS
    mu.bed(0, T_STOP, cutoff=lambda tt: 0.05 + 0.06 * lvl(tt), vol=lambda tt: (0.015 + 0.04 * lvl(tt)) * clamp(tt / 0.05), seed=31)
    drum_track(mu, T_STOP - 0.32, lvl, bpm0=96, bpm1=150, key=2, roll=1.4)
    for vv, tp, _ in MILESTONES:
        ding(mu, tp, key=2, vol=0.15, pan=0.4 if vv < 43 else -0.4)
    mu.silence(T_STOP - 0.32, T_STOP)
    drop_hit(mu, T_STOP, key=2)
    mu.bed(T_STOP + 0.4, DUR, cutoff=lambda tt: 0.02, vol=lambda tt: 0.01, seed=17)
    mu.bell(T_TWIST, 659.25, 0.16, -0.3); mu.bell(T_TWIST + 0.1, 987.77, 0.16, 0.3)


if __name__ == '__main__':
    main(render_frame, DUR, music, sys.argv)
