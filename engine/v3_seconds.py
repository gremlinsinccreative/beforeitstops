"""FACT 004 - 1 million seconds vs 1 billion seconds (scale engine)
Arithmetic: 1e6 s / 86,400 = 11.57 days; 1e9 s / 86,400 = 11,574 days = 31.7 years."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from lib import *

DUR = 14.0
DAYS_M = 1e6 / 86400.0                     # 11.574
DAYS_B = 1e9 / 86400.0                     # 11574.07
ROWS, COLS = 32, 365
GW, RP, CH = 949, 24, 20
GX, GY = (W - GW) // 2 + 10, 610
XS = np.minimum((np.arange(GW) / (GW / COLS)).astype(int), COLS - 1)
EMPTY = np.array([26, 32, 48], np.float32)
BL = np.array(BLUE, np.float32)
GD = np.array(GOLD, np.float32)
T_ZOOM0, T_ZOOM1 = 2.3, 3.2
T_B0, T_B1 = 3.3, 9.3
T_REV = 9.45
BIG_P, BIG_S = 74, 62                      # phase A cell pitch / size
BX, BY = (W - 12 * BIG_P) // 2 + 6, 760
BIG_H = 210


def n_billion(t):
    return DAYS_B * ramp(t, T_B0, T_B1) ** 1.9


HOOK, _ = text_layer([('FACT 004', SEMI, 30, MUTED),
                      ('1 million seconds', XB, 84, GOLD),
                      ('vs 1 billion seconds', XB, 84, BLUE),
                      ('Guess the gap.', SEMI, 40, WHITE)], 232)
REVEAL, _ = text_layer([('FACT 004', SEMI, 30, MUTED),
                        ('11.6 days', BLACK, 104, GOLD),
                        ('vs 31.7 years', BLACK, 104, BLUE)], 250)
LAB_M, _ = text_layer([('1 million seconds = 11.6 days', BOLD, 50, GOLD)], BY + 210 + 48)
SOURCE, _ = text_layer([('1 row = 1 year.  The gold sliver is the million.', MED, 30, MUTED)], GY + ROWS * RP + 86)
_cc = {}


def counter(s):
    if s not in _cc:
        _cc.clear()
        _cc[s], _ = text_layer([(s, BOLD, 46, WHITE)], GY + ROWS * RP + 22)
    return _cc[s]


def grid_image(n_b, n_m, wipe=0.0):
    idx = np.arange(ROWS * COLS, dtype=np.float32).reshape(ROWS, COLS)
    col = np.where((idx < n_b)[..., None], BL, EMPTY)
    col = np.where((idx < n_m)[..., None], GD, col)
    if wipe > 0:
        keep = (np.arange(ROWS)[:, None] < ROWS * (1 - wipe))
        col = np.where(keep[..., None], col, EMPTY)
    wide = col[:, XS, :]
    out = np.empty((ROWS * RP, GW, 3), np.float32)
    out[:] = np.array(BG, np.float32)
    for r in range(ROWS):
        out[r * RP:r * RP + CH] = wide[r]
    return Image.fromarray(out.astype(np.uint8))


def render_frame(t):
    img = new_frame()
    d = ImageDraw.Draw(img)
    z = ease_io(ramp(t, T_ZOOM0, T_ZOOM1))             # 0 = big strip, 1 = full grid
    back = ease_io(ramp(t, 13.45, 13.9))                # loop: back to the big strip
    grid_a = z * (1 - ease_io(ramp(t, 13.3, 13.6)))
    if grid_a > 0:
        wipe = ease_in(ramp(t, 13.05, 13.4))
        g = grid_image(n_billion(t), DAYS_M if t < 13.3 else 0, wipe).convert('RGBA')
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        lay.paste(g, (GX, GY))
        ld = ImageDraw.Draw(lay)
        for yr in (10, 20, 30):
            ld.text((GX - 44, GY + (yr - 1) * RP - 4), str(yr), font=font(MED, 24), fill=MUTED + (255,))
        comp(img, lay, grid_a)
    # phase A: 12 big day cells that shrink into the grid's top-left corner
    tt = t if t < 13.4 else t - DUR                     # time within the (next) cycle
    fill_days = DAYS_M * ease_io(ramp(tt, -0.25, 1.75)) if tt < T_ZOOM1 else DAYS_M
    a_strip = (1 - ease_io(ramp(t, T_ZOOM1 - 0.15, T_ZOOM1))) if t < 13 else back
    if a_strip > 0:
        zz = z if t < 13 else 0.0
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        tw = GW / COLS
        for k in range(12):
            x0 = BX + k * BIG_P + (GX + k * tw - (BX + k * BIG_P)) * zz
            y0 = BY + (GY - BY) * zz
            w = BIG_S + (tw - BIG_S) * zz
            h = BIG_H + (CH - BIG_H) * zz
            rad = max(0, int(12 * (1 - zz)))
            ld.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=rad, fill=(26, 32, 48, 255))
            f = clamp(fill_days - k)
            if f > 0:
                ld.rounded_rectangle([x0, y0, x0 + w * f, y0 + h], radius=rad if f > 0.3 else 0, fill=GOLD + (255,))
            if zz < 0.05 and k < 12:
                lab = str(k + 1)
                ld.text((x0 + w / 2, y0 - 34), lab, font=font(MED, 24), fill=MUTED + (255,), anchor='mm')
        comp(img, lay, a_strip)
        if t < 13:
            comp(img, text_layer([('days', MED, 28, MUTED)], BY - 96)[0], (1 - z) * a_strip)
            comp(img, LAB_M, ease_io(ramp(t, 1.7, 2.0)) * (1 - z))
        else:
            comp(img, text_layer([('days', MED, 28, MUTED)], BY - 96)[0], back)
    # billion counter
    if T_B0 - 0.2 <= t < 13.3:
        yrs = n_billion(t) / 365.25
        s = f'1 billion seconds = {yrs:.1f} years' if t >= T_B0 else '1 billion seconds = ...'
        comp(img, counter(s), ease_io(ramp(t, T_B0 - 0.2, T_B0 + 0.1)) * (1 - ease_io(ramp(t, 13.0, 13.3))))
    rev_in = ease_io(ramp(t, T_REV, T_REV + 0.35))
    comp(img, HOOK, (1 - rev_in) if t < 13 else ease_io(ramp(t, 13.5, 13.9)))
    comp(img, REVEAL, rev_in * (1 - ease_io(ramp(t, 13.15, 13.5))))
    comp(img, SOURCE, ease_io(ramp(t, T_REV + 0.6, T_REV + 1.0)) * (1 - ease_io(ramp(t, 13.0, 13.3))))
    return img


def audio(au):
    for k in range(12):                       # day ticks for the million
        x = (k + 0.5) / DAYS_M
        # invert ease_io numerically
        lo, hi = 0.0, 1.0
        for _ in range(30):
            mid = (lo + hi) / 2
            if ease_io(mid) < min(x, 1):
                lo = mid
            else:
                hi = mid
        au.tick(-0.25 + 2.0 * lo, freq=700 + 30 * k, vol=0.2)
    au.ding(1.8, freqs=(880.0, 1318.5), vol=0.14, dur=0.6)
    au.whoosh(T_ZOOM0, dur=0.9, vol=0.2, up=False)
    for yr in range(1, 32):                   # one tick per completed year row
        tr = T_B0 + (T_B1 - T_B0) * (yr * 365.0 / DAYS_B) ** (1 / 1.9)
        au.tick(tr, freq=330 * 2 ** (yr / 16), vol=0.2, dur=0.08)
    au.thunk(T_B1, freq=80, vol=0.6, dur=0.35)
    au.ding(T_REV)
    au.whoosh(13.0, dur=0.8, vol=0.2)


if __name__ == '__main__':
    run(render_frame, DUR, 'fact004_seconds', audio, sys.argv)
