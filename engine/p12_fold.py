"""v6 FACT 001 Fold paper 42 times - smooth version.
One continuous eased glide (monotone cubic through keyframes) that slows at each landmark so its name can be
read; no stepping, no scrolling stripes. 13 s. Drum beat that speeds up, a ding at each landmark, snare roll,
silence, drop. Facts: 0.1 mm x 2^42 = 439,805 km > Moon 384,400 km; Burj Khalifa 828 m; Everest 8,849 m;
ISS ~408 km; record 12 folds."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from scipy.interpolate import PchipInterpolator
from lib import *
from brand2 import *
import p5_fold as F

DUR, T_STOP, T_TWIST = 13.0, 9.6, 11.0
LMV = {'Burj Khalifa': 828, 'Everest': 8849, 'Space Station': 408000, 'The Moon': 384400000}
LMTXT = {'Burj Khalifa': '828 m', 'Everest': '8,849 m', 'Space Station': '408 km', 'The Moon': '384,400 km'}
NPASS = {k: math.log2(v / 1e-4) for k, v in LMV.items()}       # fold count at which the stack passes it
KEYS = [(0, 3.0), (1.4, 14.0), (2.5, 22.4), (3.4, 23.55), (4.3, 25.9), (5.15, 26.9), (6.0, 31.4), (6.85, 32.45),
        (8.6, 41.25), (9.3, 41.78), (9.6, 42.0)]
_P = PchipInterpolator([k[0] for k in KEYS], [k[1] for k in KEYS])
assert round(0.1e-6 * 2 ** 42) == 439805


def nfold(t):
    return float(_P(min(max(t, 0.0), T_STOP)))


def t_pass(nv):
    lo, hi = 0.0, T_STOP
    for _ in range(40):
        md = (lo + hi) / 2
        lo, hi = (lo, md) if nfold(md) >= nv else (md, hi)
    return hi


PASS = {k: t_pass(v) for k, v in NPASS.items()}
BR = Brand2(1, ['Fold paper 42 times.', 'How thick?'], 'Fold paper 42 times. How thick?',
            [('A', 'Everest'), ('B', 'The Moon'), ('C', 'Mars')],
            [('Past the Moon', BLACK, 124, GOLD), ('0.1 mm, doubled 42 times', BOLD, 46, WHITE)],
            [('Real-world record:', BOLD, 48, WHITE), ('12 folds', BLACK, 100, GOLD)], T_STOP, T_TWIST, DUR,
            sub='Wait for the Moon')
RESULT = {'A': 'out', 'B': 'win', 'C': 'out'}
SX, MY, PX = 540, 1000, 340
YY = np.linspace(0, 1, H)[:, None, None]
rng = np.random.default_rng(2)
STARS = [(rng.uniform(0, W), rng.uniform(0, 1440), rng.uniform(1.0, 2.6), rng.uniform(0, 6.28)) for _ in range(150)]
STACK = Canvas()
STACK.rect([SX - 46, MY, SX + 46, 1500], fill=(246, 244, 236, 255))
for _y in range(MY + 8, 1500, 16):
    STACK.line([(SX - 46, _y), (SX + 46, _y)], fill=(210, 206, 196, 255), width=2)
STACK.rect([SX - 52, MY - 6, SX + 52, MY + 2], fill=GOLD + (255,))
STACK_IMG = glow(STACK.down(), radius=22, strength=0.35)
SIDE = {'Everest': (SX - 84, 'rm'), 'The Moon': (SX + 205, 'lm'), 'Burj Khalifa': (SX + 84, 'lm'), 'Space Station': (SX + 84, 'lm')}


def frame_core(t):
    n = nfold(t)
    lh = math.log10(F.alt(n))
    top, bot = F.sky(lh)
    arr = np.broadcast_to((np.array(top) * (1 - YY) + np.array(bot) * YY), (H, W, 3)).astype(np.uint8)
    img = Image.fromarray(arr, 'RGB').convert('RGBA')
    c = Canvas()
    sa = clamp((lh - 4.3) / 1.0)
    if sa > 0:
        for sx, sy, sr, ph in STARS:
            c.circle(sx, sy, sr, fill=(255, 255, 255, int(255 * sa * (0.75 + 0.25 * math.sin(ph + t * 0.6)))))
    ys = {k: MY - (math.log10(v) - lh) * PX for k, v in LMV.items()}
    y = ys['Everest']
    if y < 1700:
        c.polygon([(770, y), (1200, y + 640), (340, y + 640)], fill=(38, 50, 80, 255))
        c.polygon([(770, y), (836, y + 96), (800, y + 86), (770, y + 116), (726, y + 70)], fill=(226, 232, 245, 255))
    y = ys['Burj Khalifa']
    if y < 1900:
        c.polygon([(250, y), (262, y + 120), (282, y + 300), (310, y + 900), (190, y + 900), (218, y + 300), (238, y + 120)],
                  fill=(30, 40, 66, 255))
    y = ys['Space Station']
    if -100 < y < 1500:
        cx = 260
        c.rect([cx - 90, y - 3, cx + 90, y + 3], fill=(200, 205, 215, 255))
        for dx in (-80, -45, 45, 80):
            c.rect([cx + dx - 14, y - 34, cx + dx + 14, y + 34], fill=(70, 110, 190, 255), outline=(200, 205, 215, 255), width=2)
        c.rect([cx - 18, y - 9, cx + 18, y + 9], fill=(230, 232, 240, 255))
    img.alpha_composite(c.down())
    y = ys['The Moon']
    if -250 < y < 1700:
        mc = Canvas()
        r = 175
        mc.circle(SX, y, r, fill=(216, 214, 226, 255))
        for cx_, cy_, cr in ((-0.35, -0.2, 0.22), (0.3, 0.25, 0.16), (0.1, -0.45, 0.1), (-0.1, 0.45, 0.12)):
            mc.circle(SX + cx_ * r, y + cy_ * r, cr * r, fill=(176, 174, 188, 255))
        img.alpha_composite(glow(mc.down(), radius=40, strength=0.5))
    img.alpha_composite(STACK_IMG)
    fade = Image.new('RGBA', (W, 740), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fade)
    for i in range(740):
        fd.line([0, i, W, i], fill=bot + (int(255 * clamp(i / 170) ** 0.8),))
    img.alpha_composite(fade, (0, 1180))
    # landmark name + height, held for about a second around the pass
    for k, tp in PASS.items():
        if t >= T_STOP - 0.05:
            break
        a = ease_io(ramp(t, tp - 0.45, tp - 0.2)) * (1 - ease_io(ramp(t, tp + 0.75, tp + 1.0)))
        if a > 0.02:
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            x, an = SIDE[k]
            lb, _ = big_text([(k, XB, 56, WHITE), (LMTXT[k], BOLD, 38, GOLD)], 0)
            bb = lb.getbbox()
            sub = lb.crop(bb)
            px = x if an == 'lm' else x - sub.width
            lay.alpha_composite(sub, (int(px), int(MY - 60)))
            comp(img, lay, a)
    ca = 1 - ramp(t, T_TWIST - 0.1, T_TWIST + 0.2)
    if ca > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        val = '439,805 km' if t >= T_STOP else F.fmt(min(F.alt(n), 4.39e8))
        ImageDraw.Draw(lay).text((W / 2, 1360), val, font=font(BLACK, 108), fill=GOLD if t >= T_STOP else WHITE, anchor='mm')
        comp(img, lay, ca)
    return BR.overlay(img, t, RESULT)


render_frame = looped(frame_core, DUR, xf=0.5)


def music(m):
    from brand import drum_track, ding, drop_hit
    prog = lambda tt: (nfold(tt) - 3) / 39
    lhs = lambda tt: (math.log10(F.alt(nfold(tt))) + 4) / 12.6
    m.bed(0, T_STOP, cutoff=lambda tt: 0.9 - 0.85 * clamp(lhs(tt) * 1.15),
          vol=lambda tt: 0.018 * (1 - 0.7 * clamp(lhs(tt) * 1.2)) * clamp(tt / 0.05), seed=3)
    drum_track(m, T_STOP - 0.32, prog, bpm0=100, bpm1=150, key=0, roll=1.4)
    for k, tp in PASS.items():
        if tp < T_STOP - 0.4:
            ding(m, tp, key=0, vol=0.15, pan={'Everest': 0.5, 'The Moon': 0.0}.get(k, -0.5))
    m.silence(T_STOP - 0.32, T_STOP)
    drop_hit(m, T_STOP, key=0)
    m.bed(T_STOP + 0.4, DUR, cutoff=lambda tt: 0.02, vol=lambda tt: 0.01, seed=5)
    m.bell(T_TWIST, 659.25, 0.16, -0.3); m.bell(T_TWIST + 0.1, 987.77, 0.16, 0.3)


if __name__ == '__main__':
    main(render_frame, DUR, music, sys.argv)
