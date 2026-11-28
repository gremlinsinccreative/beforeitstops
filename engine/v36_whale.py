"""v6 FACT 036 A blue whale weighs how many people? 13 s, no teaser (even number).
Human-scale size arm of the topic test ("how many Y fit in Z").
Source: NOAA Fisheries, "Blue Whale" species page, Quick Facts: "Weight: Up to 330,000 pounds", "Length: Up to 110 feet";
"they are the largest animals ever to live on our planet". Person = 70 kg, the same reference adult as #034
(Sender et al. 2016). 330,000 lb x 0.45359237 = 149,685 kg = 150 tonnes; / 70 kg = 2,138 people.
Milestones (arithmetic): 500 people = 35 tonnes; 1,000 people = 70 tonnes, still not halfway.
Twist: the largest animal ever to live (NOAA).
Hero: a balance scale, whale on one pan, people piling onto the other until the beam levels at the STOP
(each figure on screen = 10 people)."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from scipy.interpolate import PchipInterpolator
from lib import *
from lib2 import big_text
from brand2 import *

DUR, T_STOP, T_TWIST = 13.0, 9.6, 11.0
LB = 0.45359237
KG = 330_000 * LB
PERSON = 70.0
N = KG / PERSON
assert round(KG) == 149_685 and round(KG / 1000) == 150 and round(N) == 2138 and round(N, -2) == 2100
assert 500 * PERSON / 1000 == 35 and 1000 * PERSON / 1000 == 70 and 1000 < N / 2
NT = round(N)

KEYS = [(0, 0.0), (1.4, 120.0), (3.2, 480.0), (4.1, 520.0), (5.8, 975.0), (6.8, 1030.0), (8.7, 1900.0), (9.6, N)]
_P = PchipInterpolator([k[0] for k in KEYS], [k[1] for k in KEYS])


def count(t):
    return float(_P(min(max(t, 0.0), T_STOP)))


def t_at(v):
    lo, hi = 0.0, T_STOP
    for _ in range(40):
        md = (lo + hi) / 2
        lo, hi = (lo, md) if count(md) >= v else (md, hi)
    return hi


MILESTONES = [(500, t_at(500), ['500 people', '35 tonnes']),
              (1000, t_at(1000), ['1,000 people', '70 tonnes: not even halfway'])]
BR = Brand2(36, ['A blue whale weighs', 'how many people?'], 'A blue whale weighs how many people?',
            [('A', '21'), ('B', '210'), ('C', '2,100')],
            [('About 2,100 people', BLACK, 92, GOLD), ('Up to 330,000 lb = 150 tonnes (NOAA) ÷ 70 kg', BOLD, 34, WHITE)],
            [('The largest animal', BOLD, 48, WHITE), ('ever to live (NOAA)', BLACK, 76, GOLD)], T_STOP, T_TWIST, DUR,
            sub='Wait for the scale to level · 70 kg each', cta='Comment your letter', q_size=84)
RESULT = {'A': 'out', 'B': 'out', 'C': 'win'}

PX, PY = 540, 800          # pivot
HALF = 270                 # half beam
HANG = 250                 # pan hangs this far below the beam end
FLOOR = 1290
MAXANG = math.radians(14)
COLS, ICON_W, ICON_H = 24, 15, 22
ICONS = math.ceil(NT / 10)


def background():
    ys = np.linspace(0, 1, H)[:, None, None]
    top, bot = np.array((4, 10, 22)), np.array((8, 40, 70))
    arr = np.broadcast_to(top * (1 - ys ** 1.3) + bot * ys ** 1.3, (H, W, 3)).astype(np.uint8)
    img = Image.fromarray(np.ascontiguousarray(arr), 'RGB').convert('RGBA')
    c = Canvas()
    c.rect([0, FLOOR, W, FLOOR + 8], fill=(40, 70, 100, 255))
    c.polygon([(PX - 70, FLOOR), (PX - 16, PY + 10), (PX + 16, PY + 10), (PX + 70, FLOOR)], fill=(70, 86, 110, 255))
    img.alpha_composite(c.down())
    return img


BG_IMG = background()
_sm = font(SEMI, 26)


def whale(c, cx, cy):
    """Side-on blue whale lying on the pan (cx, cy = bottom centre)."""
    col, belly = (70, 120, 190, 255), (150, 180, 220, 255)
    y = cy - 62
    c.ellipse([cx - 190, y - 52, cx + 150, y + 56], fill=col)
    c.polygon([(cx + 120, y - 30), (cx + 215, y - 6), (cx + 215, y + 10), (cx + 120, y + 40)], fill=col)
    c.polygon([(cx + 200, y), (cx + 250, y - 46), (cx + 236, y + 2), (cx + 252, y + 44)], fill=col)   # tail flukes
    c.ellipse([cx - 180, y + 8, cx + 100, y + 54], fill=belly)
    for i in range(6):
        c.line([(cx - 150 + i * 30, y + 24), (cx - 120 + i * 30, y + 50)], fill=(110, 150, 205, 255), width=2)
    c.circle(cx - 120, y - 6, 6, fill=(20, 30, 50, 255))
    c.polygon([(cx + 40, y - 48), (cx + 70, y - 66), (cx + 70, y - 46)], fill=col)                  # small dorsal fin


def person(c, x, y, col):
    c.circle(x, y - 19, 5, fill=col)
    c.rect([x - 5, y - 13, x + 5, y], fill=col, radius=3)


def frame_core(t):
    n = count(t)
    shown = NT if t >= T_STOP else n
    ang = MAXANG * (1 - min(1.0, shown / N))           # left (whale) side down until balanced
    lx, ly = PX - HALF * math.cos(ang), PY + HALF * math.sin(ang)
    rx, ry = PX + HALF * math.cos(ang), PY - HALF * math.sin(ang)
    img = BG_IMG.copy()
    c = Canvas()
    for (bx, by) in ((lx, ly), (rx, ry)):
        py = by + HANG
        c.line([(bx, by), (bx - 190, py)], fill=(170, 180, 200, 255), width=2.5)
        c.line([(bx, by), (bx + 190, py)], fill=(170, 180, 200, 255), width=2.5)
        c.rect([bx - 200, py, bx + 200, py + 14], fill=(150, 160, 185, 255), radius=6)
    c.line([(lx, ly), (rx, ry)], fill=(200, 208, 226, 255), width=12)
    c.circle(PX, PY, 16, fill=(220, 226, 240, 255))
    whale(c, lx - 40, ly + HANG)
    img.alpha_composite(c.down())
    hc = Canvas()                                        # hero: the growing pile of people (each = 10)
    k = min(ICONS, int(math.ceil(shown / 10)))
    base_y = ry + HANG
    for i in range(k):
        row, col = divmod(i, COLS)
        x = rx - (COLS - 1) * ICON_W / 2 + col * ICON_W + (ICON_W / 2 if row % 2 else 0) * 0.5
        person(hc, x, base_y - 2 - row * ICON_H, (255, 210, 120, 255))
    comp(img, glow(hc.down(), radius=12, strength=0.55), 1 - 0.7 * ease_io(ramp(t, T_TWIST - 0.1, T_TWIST + 0.3)))
    wa = ease_io(ramp(t, HOOK_END + 0.1, HOOK_END + 0.4)) * (1 - ease_io(ramp(t, T_STOP - 0.3, T_STOP)))
    if wa > 0.02:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(lay).text((W - 50, FLOOR - 26), 'each figure = 10 people', font=_sm, fill=(170, 185, 210), anchor='rm')
        comp(img, lay, wa)
    for vv, tp, txt in MILESTONES:
        al = ease_io(ramp(t, tp - 0.2, tp + 0.05)) * (1 - ease_io(ramp(t, tp + 0.9, tp + 1.15)))
        if al > 0.02 and t < T_STOP:
            lb, _ = big_text([(txt[0], XB, 50, WHITE), (txt[1], BOLD, 42, GOLD)], 0)
            sub = lb.crop(lb.getbbox())
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            lay.alpha_composite(sub, ((W - sub.width) // 2, 440))
            comp(img, lay, al)
    ca = 1 - ramp(t, T_TWIST - 0.1, T_TWIST + 0.2)
    if ca > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(lay)
        val = f'{NT if t >= T_STOP else int(n):,} people'
        dd.rounded_rectangle([220, 1322, 860, 1440], radius=40, fill=(4, 10, 22, 215))
        dd.text((W / 2 + 4, 1385), val, font=font(BLACK, 84), fill=(0, 0, 0, 150), anchor='mm')
        dd.text((W / 2, 1381), val, font=font(BLACK, 84), fill=GOLD if t >= T_STOP else WHITE, anchor='mm')
        comp(img, lay, ca)
    return BR.overlay(img, t, RESULT)


render_frame = looped(frame_core, DUR, xf=0.5)


def music(mu):
    from brand import drum_track, ding, drop_hit
    lvl = lambda tt: count(tt) / N
    mu.bed(0, T_STOP, cutoff=lambda tt: 0.05 + 0.06 * lvl(tt), vol=lambda tt: (0.015 + 0.04 * lvl(tt)) * clamp(tt / 0.05), seed=36)
    drum_track(mu, T_STOP - 0.32, lvl, bpm0=96, bpm1=150, key=3, roll=1.4)
    for vv, tp, _ in MILESTONES:
        ding(mu, tp, key=3, vol=0.15, pan=0.4 if vv < 800 else -0.4)
    mu.silence(T_STOP - 0.32, T_STOP)
    drop_hit(mu, T_STOP, key=3)
    mu.bed(T_STOP + 0.4, DUR, cutoff=lambda tt: 0.02, vol=lambda tt: 0.01, seed=29)
    mu.bell(T_TWIST, 659.25, 0.16, -0.3); mu.bell(T_TWIST + 0.1, 987.77, 0.16, 0.3)


if __name__ == '__main__':
    main(render_frame, DUR, music, sys.argv)
