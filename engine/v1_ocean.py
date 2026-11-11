"""FACT 007 - Deep seafloor: how much have we seen? (dissolve engine)
Source: Bell et al., Science Advances, 2025: less than 0.001% visually observed."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from lib import *

DUR = 14.0
COLS, ROWS, P = 250, 400, 4
GX, GY = (W - COLS * P) // 2, (H - ROWS * P) // 2
SR_, SC_ = 232, 150                       # surviving dot (row, col)
DOTX, DOTY = GX + SC_ * P + 2, GY + SR_ * P + 2
T_END = 8.6                               # dissolve ends
OFF = np.array([27, 37, 60], np.float32)
LIT = np.array(BLUE, np.float32)
EDGE = np.array([225, 242, 255], np.float32)

rng = np.random.default_rng(11)
rr, cc = np.mgrid[0:ROWS, 0:COLS]
dist = np.hypot((rr - SR_) * 1.0, (cc - SC_) * 1.0)
score = dist / dist.max() * 0.72 + rng.random((ROWS, COLS)) * 0.28
score[SR_, SC_] = -1
order = np.argsort(score, axis=None)
Q = np.empty(ROWS * COLS, np.float32)
Q[order] = np.arange(ROWS * COLS) / (ROWS * COLS)
Q = Q.reshape(ROWS, COLS)                 # quantile rank: 0 = last survivor

cell = np.zeros((P, P), np.float32)
cell[1:3, 1:3] = 1
MASK = np.tile(cell, (ROWS, COLS))[..., None]


def frac(t):
    """Fraction of dots still lit at time t (loops back to 1 at the end)."""
    if t < 13.2:
        return 10 ** (-5 * ramp(t, 0.0, T_END))
    return 10 ** (-5 * (1 - ease_io(ramp(t, 13.2, 13.95))))


def fmt_pct(f):
    p = 100 * f
    if p >= 99.5:
        return '100%'
    if p >= 10:
        return f'{p:.0f}%'
    if p >= 1:
        return f'{p:.1f}%'
    if p >= 0.1:
        return f'{p:.2f}%'
    if p >= 0.01:
        return f'{p:.3f}%'
    if p > 0.00105:
        return f'{p:.4f}%'
    return '< 0.001%'


HOOK, _ = text_layer([('FACT 007', SEMI, 30, MUTED),
                      ('Deep seafloor:', XB, 84, WHITE),
                      ('how much have we seen?', XB, 72, WHITE),
                      ('Guess before it stops.', SEMI, 40, GOLD)], 250, plate=(8, 10, 16, 214))
REVEAL, _ = text_layer([('FACT 007', SEMI, 30, MUTED),
                        ('Less than 0.001%', BLACK, 104, GOLD),
                        ('of the deep seafloor', XB, 60, WHITE),
                        ('has ever been seen by humans', XB, 60, WHITE)], 250, plate=(8, 10, 16, 224))
SOURCE, _ = text_layer([('1 dot in 100,000', BOLD, 46, WHITE),
                        ('Source: Bell et al., Science Advances (2025)', MED, 28, MUTED)], 1352,
                       plate=(8, 10, 16, 224))
_counter_cache = {}


def counter_layer(s):
    if s not in _counter_cache:
        _counter_cache.clear()
        _counter_cache[s], _ = text_layer([('SEEN BY HUMANS', SEMI, 30, MUTED), (s, BLACK, 96, WHITE)], 1340,
                                          plate=(8, 10, 16, 224))
    return _counter_cache[s]


def lens(img, a):
    """Magnifier showing the single surviving dot among dark neighbours."""
    if a <= 0:
        return
    R = int(236 * a)
    cx, cy = 540, 800
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.line([(DOTX, DOTY), (cx + 150, cy + 182)], fill=(255, 204, 51, int(200 * a)), width=3)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(8, 10, 16, 255), outline=GOLD + (255,), width=6)
    pitch = 62
    for i in range(-4, 5):
        for j in range(-4, 5):
            x, y = cx + i * pitch, cy + j * pitch
            if math.hypot(x - cx, y - cy) > R - 22:
                continue
            if i == 0 and j == 0:
                continue
            d.rounded_rectangle([x - 11, y - 11, x + 11, y + 11], radius=5, fill=(30, 40, 62, 255))
    if R > 60:
        for g, al in ((46, 26), (32, 50), (22, 90)):
            d.ellipse([cx - g, cy - g, cx + g, cy + g], fill=GOLD + (al,))
        d.rounded_rectangle([cx - 13, cy - 13, cx + 13, cy + 13], radius=6, fill=GOLD + (255,))
    img.alpha_composite(lay)


def render_frame(t):
    f = frac(t)
    lit = (Q < f)
    edge = (Q >= f) & (Q < f * 1.22 + 2e-5) & (t < T_END + 0.2)
    col = np.where(lit[..., None], LIT, OFF)
    col = np.where(edge[..., None], EDGE, col)
    if f < 2e-5:                           # the survivor turns gold
        col[SR_, SC_] = GOLD
    big = np.repeat(np.repeat(col, P, 0), P, 1) * MASK + np.array(BG, np.float32) * (1 - MASK)
    img = new_frame()
    img.paste(Image.fromarray(big.astype(np.uint8)), (GX, GY))

    n_lit = int(lit.sum())
    if n_lit <= 600:                       # make the last few dots readable
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        ys, xs = np.nonzero(lit)
        gold = n_lit == 1
        for y, x in zip(ys, xs):
            px, py = GX + x * P + 2, GY + y * P + 2
            c = GOLD if gold else BLUE
            r = 5 if n_lit > 60 else 8
            d.ellipse([px - r * 2, py - r * 2, px + r * 2, py + r * 2], fill=c + (60,))
            d.ellipse([px - r, py - r, px + r, py + r], fill=c + (255,))
        if gold and t < 13.2:
            pulse = (t * 1.2) % 1.0
            rad = 14 + 60 * pulse
            d.ellipse([DOTX - rad, DOTY - rad, DOTX + rad, DOTY + rad], outline=GOLD + (int(255 * (1 - pulse)),),
                      width=4)
        img.alpha_composite(lay)

    lens(img, ease_out(ramp(t, 9.0, 9.5)) * (1 - ease_in(ramp(t, 12.95, 13.25))))

    rev_in = ease_io(ramp(t, T_END, T_END + 0.35))
    comp(img, HOOK, (1 - rev_in) if t < 13 else ease_io(ramp(t, 13.5, 13.9)))
    comp(img, REVEAL, rev_in * (1 - ease_io(ramp(t, 13.15, 13.5))))
    comp(img, counter_layer(fmt_pct(f)), 1 - ease_io(ramp(t, 9.6, 9.95)) + ease_io(ramp(t, 13.5, 13.9)))
    comp(img, SOURCE, ease_io(ramp(t, 9.7, 10.05)) * (1 - ease_io(ramp(t, 13.2, 13.5))))
    return img


def audio(au):
    t = 0.0
    while t < T_END:
        x = t / T_END
        au.tick(t, freq=1500 - 1050 * x, vol=0.16)
        t += 0.085 + 0.05 * x
    for k in range(1, 5):
        au.thunk(T_END * k / 5, freq=150 - 14 * k, vol=0.42)
    au.thunk(T_END, freq=70, vol=0.7, dur=0.4)
    au.ding(T_END + 0.05)
    au.whoosh(9.0, dur=0.5, vol=0.12)
    au.whoosh(13.15, dur=0.8, vol=0.2)


if __name__ == '__main__':
    run(render_frame, DUR, 'fact007_seafloor', audio, sys.argv)
