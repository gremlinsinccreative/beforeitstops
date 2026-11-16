"""FACT 018 - How many squares on a chessboard? (square sweep engine)
Arithmetic: a k x k square fits in (9-k)^2 positions on an 8 x 8 board.
64 + 49 + 36 + 25 + 16 + 9 + 4 + 1 = 204."""
import sys
from PIL import Image, ImageDraw
from lib import *

DUR = 14.0
SEQ = [(k, r, c) for k in range(1, 9) for r in range(9 - k) for c in range(9 - k)]
TOTAL = len(SEQ)
assert TOTAL == sum((9 - k) ** 2 for k in range(1, 9)) == 204
assert [(9 - k) ** 2 for k in range(1, 9)] == [64, 49, 36, 25, 16, 9, 4, 1]
CELL, BX, BY = 76, 236, 650
T1 = 9.0
T_REV = T1 + 0.15
STARTS = {k: sum((9 - j) ** 2 for j in range(1, k)) for k in range(1, 9)}


def n_at(t):
    return TOTAL * ramp(t, -0.15, T1) ** 0.8


def t_of(n):
    return (n / TOTAL) ** (1 / 0.8) * (T1 + 0.15) - 0.15


HOOK, _ = text_layer([('FACT 018', SEMI, 30, MUTED), ('How many squares', XB, 88, WHITE),
                      ('on a chessboard?', XB, 88, WHITE), ('Guess before it stops.', SEMI, 40, GOLD)], 232)
REVEAL, _ = text_layer([('FACT 018', SEMI, 30, MUTED), ('204', BLACK, 150, GOLD),
                        ('not 64: count every size', XB, 60, WHITE),
                        ('64 + 49 + 36 + 25 + 16 + 9 + 4 + 1', MED, 36, MUTED)], 232)


def sim(t):
    lay, d = layer()
    n = n_at(t)
    i = min(TOTAL - 1, int(n))
    k, r, c = SEQ[i]
    x0, y0 = BX + c * CELL, BY + r * CELL
    d.rectangle([x0, y0, x0 + k * CELL, y0 + k * CELL], fill=GOLD + (120,), outline=GOLD + (255,), width=6)
    cnt = TOTAL if t >= T1 else i + 1
    d.text((W / 2, 1345), f'{cnt}', font=font(BLACK, 120), fill=(GOLD if t >= T1 else WHITE) + (255,), anchor='mm')
    d.text((W / 2, 1436), f'counting {k} x {k} squares', font=font(SEMI, 34), fill=MUTED + (255,), anchor='mm')
    return lay


def render_frame(t):
    img = new_frame()
    d = ImageDraw.Draw(img)
    for r in range(8):
        for c in range(8):
            col = (36, 44, 64) if (r + c) % 2 else (70, 82, 110)
            d.rectangle([BX + c * CELL, BY + r * CELL, BX + (c + 1) * CELL - 1, BY + (r + 1) * CELL - 1], fill=col)
    loop_sim(img, sim, t, DUR)
    loop_text(img, HOOK, REVEAL, t, T_REV)
    return img


def audio(au):
    for i in range(TOTAL):
        k = SEQ[i][0]
        tt = t_of(i)
        if tt >= 0 and (k > 1 or i % 2 == 0):
            au.tick(tt, freq=440 * 2 ** ((k - 1) / 6), vol=0.16 + 0.02 * k, dur=0.05 + 0.01 * k)
    for k in range(2, 9):
        au.ding(t_of(STARTS[k]), freqs=(660.0 * 2 ** ((k - 2) / 12),), vol=0.1, dur=0.4)
    au.thunk(T1, freq=80, vol=0.6, dur=0.35)
    au.ding(T_REV)
    au.whoosh(13.05, dur=0.8, vol=0.2, up=False)


if __name__ == '__main__':
    run(render_frame, DUR, 'fact018_chess', audio, sys.argv)
