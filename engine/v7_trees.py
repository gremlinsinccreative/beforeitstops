"""FACT 005 - More stars in our galaxy, or trees on Earth? (twin fill engine, 1 dot = 1 billion)
Sources: Crowther et al., Nature 525 (2015): about 3.04 trillion trees. NASA: 100-400 billion stars in the Milky Way."""
import sys
import numpy as np
from PIL import Image, ImageDraw
from lib import *

DUR = 14.0
COLS, P = 43, 10
TREES, STARS_LO, STARS_HI = 3040, 100, 400
ROWS = -(-TREES // COLS)
LX, RX, GY = 70, 580, 670
T1 = 9.0
GREEN = (86, 214, 130)
cell = np.zeros((P, P), np.float32)
cell[2:8, 2:8] = 1
MASK = np.tile(cell, (ROWS, COLS))[..., None]
IDX = np.arange(ROWS * COLS).reshape(ROWS, COLS)
BGA = np.array(BG, np.float32)


def n_at(t):
    if t >= 13.1:
        return TREES * (1 - ease_io(ramp(t, 13.1, 13.8))) if t < 13.8 else n_at(t - DUR)
    return TREES * ramp(t, -0.15, T1) ** 1.5


def field(n, lo_col, hi_col, lo, cap):
    on = IDX < min(n, cap)
    col = np.where(on[..., None], np.array(hi_col, np.float32), np.array((22, 27, 40), np.float32))
    col = np.where((on & (IDX < lo))[..., None], np.array(lo_col, np.float32), col)
    col = np.where((IDX >= cap)[..., None], BGA, col)
    big = np.repeat(np.repeat(col, P, 0), P, 1) * MASK + BGA * (1 - MASK)
    return Image.fromarray(big.astype(np.uint8))


HOOK, _ = text_layer([('FACT 005', SEMI, 30, MUTED), ('More stars in our galaxy', XB, 76, WHITE),
                      ('or trees on Earth?', XB, 76, WHITE), ('Guess before it stops.', SEMI, 40, GOLD)], 232)
REVEAL, _ = text_layer([('FACT 005', SEMI, 30, MUTED), ('Trees. By far.', BLACK, 112, GREEN),
                        ('About 3 trillion trees', XB, 58, WHITE),
                        ('vs 100-400 billion stars', XB, 58, GOLD)], 232)


def render_frame(t):
    img = new_frame()
    d = ImageDraw.Draw(img)
    n = n_at(t)
    dim_gold = tuple(int(c * 0.45) for c in GOLD)
    img.paste(field(n, GOLD, dim_gold, STARS_LO, STARS_HI), (LX, GY))
    img.paste(field(n, GREEN, GREEN, 0, TREES), (RX, GY))
    cxl, cxr = LX + COLS * P / 2, RX + COLS * P / 2
    d.text((cxl, GY - 44), 'STARS IN THE MILKY WAY', font=font(SEMI, 26), fill=MUTED, anchor='mm')
    d.text((cxr, GY - 44), 'TREES ON EARTH', font=font(SEMI, 26), fill=MUTED, anchor='mm')
    a = (1 - ease_io(ramp(t, 13.1, 13.4))) if t > 13 else 1.0
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    if n >= STARS_HI:
        ld.text((cxl, GY + 150), '100-400 billion', font=font(BOLD, 44), fill=GOLD + (255,), anchor='mm')
        ld.text((cxl, GY + 200), '(estimates vary)', font=font(MED, 26), fill=MUTED + (255,), anchor='mm')
    else:
        ld.text((cxl, GY + 150), f'{int(n):,} billion', font=font(BOLD, 44), fill=GOLD + (255,), anchor='mm')
    ld.text((cxr, GY + ROWS * P + 46), f'{int(n):,} billion', font=font(BOLD, 44), fill=GREEN + (255,), anchor='mm')
    ld.text((W / 2, GY + ROWS * P + 110), '1 dot = 1 billion', font=font(MED, 28), fill=MUTED + (255,), anchor='mm')
    if t > T1 + 1.0:
        ld.text((W / 2, GY + ROWS * P + 150), 'Sources: Crowther et al., Nature (2015); NASA', font=font(MED, 24),
                fill=MUTED + (int(255 * ease_io(ramp(t, T1 + 1.0, T1 + 1.4))),), anchor='mm')
    comp(img, lay, a)
    rin = ease_io(ramp(t, T1 + 0.15, T1 + 0.5))
    comp(img, HOOK, (1 - rin) if t < 13 else ease_io(ramp(t, 13.5, 13.9)))
    comp(img, REVEAL, rin * (1 - ease_io(ramp(t, 13.1, 13.45))))
    return img


def audio(au):
    t = 0.0
    while t < T1:
        x = t / T1
        au.tick(t, freq=500 + 1100 * x, vol=0.14, dur=0.05)
        t += 0.11 - 0.06 * x
    ts = T1 * (STARS_HI / TREES) ** (1 / 1.5)
    au.ding(ts, freqs=(880.0, 1318.5), vol=0.14, dur=0.6)
    au.thunk(T1, freq=80, vol=0.6, dur=0.35)
    au.ding(T1 + 0.1)
    au.whoosh(13.05, dur=0.8, vol=0.2, up=False)


if __name__ == '__main__':
    run(render_frame, DUR, 'fact005_trees', audio, sys.argv)
