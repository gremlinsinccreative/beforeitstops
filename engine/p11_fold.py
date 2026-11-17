"""v4 TEST - FACT 001 Fold paper 42 times. Calm version: one hero (the paper stack climbing past silhouettes to
the Moon), one number, one label at a time, smooth 2x-drawn shapes, no shake, no streaks. Sound: ticks that fuse
into a rising note (p8). Facts as in p5_fold.py."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from lib import *
from brand2 import *
import p5_fold as F
import p8_fold_sonic as S8

DUR, T_STOP, T_TWIST = F.DUR, F.T_STOP, F.T_TWIST
BR = Brand2(1, ['Fold paper 42 times.', 'How thick?'], 'Fold paper 42 times. How thick?',
            [('A', 'Everest'), ('B', 'The Moon'), ('C', 'Mars')],
            [('Past the Moon', BLACK, 124, GOLD), ('0.1 mm, doubled 42 times', BOLD, 46, WHITE)],
            [('Real-world record:', BOLD, 48, WHITE), ('12 folds', BLACK, 100, GOLD)], T_STOP, T_TWIST, DUR,
            sub='Guess A, B or C · wait for the Moon')
RESULT = {'A': 'out', 'B': 'win', 'C': 'out'}
SX, MY, PX = 540, 1000, 340
YY = np.linspace(0, 1, H)[:, None, None]
rng = np.random.default_rng(2)
STARS = [(rng.uniform(0, W), rng.uniform(0, 1440), rng.uniform(1.0, 2.6), rng.uniform(0, 6.28)) for _ in range(150)]


def frame_core(t):
    n = F.nvis(t)
    h = F.alt(n)
    lh = math.log10(h)
    top, bot = F.sky(lh)
    arr = np.broadcast_to((np.array(top) * (1 - YY) + np.array(bot) * YY), (H, W, 3)).astype(np.uint8)
    img = Image.fromarray(arr, 'RGB').convert('RGBA')
    c = Canvas()
    sa = clamp((lh - 4.3) / 1.0)
    if sa > 0:
        for sx, sy, sr, ph in STARS:
            v = int(255 * sa * (0.7 + 0.3 * math.sin(ph + t * 0.8)))
            c.circle(sx, sy, sr, fill=(255, 255, 255, v))
    ys = {k: MY - (math.log10(v) - lh) * PX for k, v in F.LM.items()}
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
    scene = c.down()
    img.alpha_composite(scene)
    # moon (with glow) behind the stack
    y = ys['The Moon']
    if -250 < y < 1700:
        mc = Canvas()
        r = 175
        mc.circle(SX, y, r, fill=(216, 214, 226, 255))
        for cx_, cy_, cr in ((-0.35, -0.2, 0.22), (0.3, 0.25, 0.16), (0.1, -0.45, 0.1), (-0.1, 0.45, 0.12)):
            mc.circle(SX + cx_ * r, y + cy_ * r, cr * r, fill=(176, 174, 188, 255))
        img.alpha_composite(glow(mc.down(), radius=40, strength=0.5))
    # the hero: paper stack
    st = Canvas()
    st.rect([SX - 46, MY, SX + 46, 1500], fill=(246, 244, 236, 255))
    off = (n * 60) % 16
    for yy in np.arange(MY + off, 1500, 16):
        st.line([(SX - 46, yy), (SX + 46, yy)], fill=(206, 202, 192, 255), width=2)
    st.rect([SX - 52, MY - 6, SX + 52, MY + 2], fill=GOLD + (255,))
    img.alpha_composite(glow(st.down(), radius=22, strength=0.35))
    # fade into the bottom zone
    fade = Image.new('RGBA', (W, 740), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fade)
    for i in range(740):
        fd.line([0, i, W, i], fill=bot + (int(255 * clamp(i / 170) ** 0.8),))
    img.alpha_composite(fade, (0, 1180))
    # one label at a time
    for k, yv in ys.items():
        a = clamp(1 - abs(yv - MY) / 110)
        if a > 0.02 and t < T_STOP:
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            side = {'Everest': (SX - 84, 'rm'), 'The Moon': (SX + 200, 'lm')}.get(k, (SX + 84, 'lm'))
            ImageDraw.Draw(lay).text((side[0], MY - 26), k, font=font(XB, 54), fill=WHITE, anchor=side[1])
            comp(img, lay, a)
    # one number
    ca = 1 - ramp(t, T_TWIST - 0.1, T_TWIST + 0.2)
    if ca > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        val = '439,805 km' if t >= T_STOP else F.fmt(F.alt(min(41, int(n + 0.5))))
        ImageDraw.Draw(lay).text((W / 2, 1360), val, font=font(BLACK, 108), fill=GOLD if t >= T_STOP else WHITE, anchor='mm')
        comp(img, lay, ca)
    return BR.overlay(img, t, RESULT)


render_frame = looped(frame_core, DUR, xf=0.4)
music = S8.music

if __name__ == '__main__':
    main(render_frame, DUR, music, sys.argv)
