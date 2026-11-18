"""v3.1 FACT 018 - How many squares on a chessboard?
Squares of size k: (9-k)^2 -> 64+49+36+25+16+9+4+1 = 204. Chips: A 64 (struck when the count passes 64),
B 204 (correct), C 300 (struck at the stop). Twist: rectangles = C(9,2)^2 = 36^2 = 1,296."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from lib import *
from brand import *
from lib2 import hsv

DUR, T_STOP, T_TWIST = 10.5, 7.3, 8.7
assert sum((9 - k) ** 2 for k in range(1, 9)) == 204 and math.comb(9, 2) ** 2 == 1296
BR = Brand(18, ['How many squares', 'on a chessboard?'], [('A', '64'), ('B', '204'), ('C', '300')],
           [('204', BLACK, 150, GOLD), ('not 64', XB, 60, WHITE)],
           [('Count rectangles instead:', BOLD, 46, WHITE), ('1,296', BLACK, 100, GOLD)], T_STOP, T_TWIST, DUR)

CELL, BX, BY = 98, 148, 505
SIZE_DUR = {1: 1.55, 2: 1.3, 3: 1.1, 4: 0.9, 5: 0.75, 6: 0.6, 7: 0.5}
EVENTS = []          # (time, k, row, col)
t0 = 0.0
for k in range(1, 8):
    n = 9 - k
    sq = [(r, c) for r in range(n) for c in range(n)]
    for i, (r, c) in enumerate(sq):
        x = i / len(sq)
        EVENTS.append((t0 + SIZE_DUR[k] * (x ** 0.9), k, r, c))
    t0 += SIZE_DUR[k]
EVENTS.append((T_STOP, 8, 0, 0))
assert len(EVENTS) == 204 and t0 < T_STOP - 0.4
ET = np.array([e[0] for e in EVENTS])
T64 = EVENTS[64][0]          # the 65th square: count passes 64
SIZE_START = {k: min(e[0] for e in EVENTS if e[1] == k) for k in range(1, 9)}


def count(t):
    return int(np.searchsorted(ET, t, side='right'))


def size_col(k):
    return GOLD if k == 8 else hsv(0.52 + 0.06 * (k - 1), 0.75, 1.0)


YY = np.linspace(0, 1, H)[:, None, None]
BGA = np.broadcast_to((np.array((16, 14, 34)) * (1 - YY) + np.array((3, 4, 12)) * YY), (H, W, 3)).astype(np.uint8)
BOARD = Image.new('RGBA', (W, H), (0, 0, 0, 0))
_bd = ImageDraw.Draw(BOARD)
_bd.rounded_rectangle([BX - 22, BY - 22, BX + 8 * CELL + 22, BY + 8 * CELL + 22], radius=24, fill=(34, 30, 52))
for r in range(8):
    for c in range(8):
        _bd.rectangle([BX + c * CELL, BY + r * CELL, BX + (c + 1) * CELL - 1, BY + (r + 1) * CELL - 1],
                      fill=(58, 62, 96) if (r + c) % 2 == 0 else (30, 34, 58))


def states(t):
    st = {'A': 'out' if t >= T64 else 'idle', 'B': 'win' if t >= T_STOP else 'idle', 'C': 'out' if t >= T_STOP else 'idle'}
    pops = {'A': math.exp(-(t - T64) * 6) if t >= T64 else 0, 'B': math.exp(-(t - T_STOP) * 5) if t >= T_STOP else 0}
    return st, pops


def frame_core(t):
    img = Image.fromarray(BGA, 'RGB').convert('RGBA')
    sh = 7 * ((t - (T_STOP - 1.4)) / 1.4) ** 2 if T_STOP - 1.4 < t < T_STOP else 0
    ox, oy = int(sh * math.sin(t * 91)), int(sh * math.cos(t * 77))
    dim = 0.28 + 0.72 * ease_io(ramp(t, 0.9, 1.4))
    comp_board = BOARD if (ox, oy) == (0, 0) else BOARD.transform(BOARD.size, Image.AFFINE, (1, 0, -ox, 0, 1, -oy))
    comp(img, comp_board, dim)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    # flashing squares: each lights up, then fades over 0.45 s; current size keeps a faint trace
    cur = max([k for k in range(1, 9) if SIZE_START[k] <= t] or [1])
    for (te, k, r, c) in EVENTS:
        age = t - te
        if age < 0:
            break
        trace = 0.07 if k == cur and t < T_STOP else 0.0
        a = max(trace, math.exp(-age * 7)) if k < 8 else 1.0
        if a < 0.03:
            continue
        col = size_col(k)
        x0, y0 = BX + c * CELL + ox, BY + r * CELL + oy
        x1, y1 = x0 + k * CELL, y0 + k * CELL
        d.rectangle([x0 + 3, y0 + 3, x1 - 3, y1 - 3], outline=col + (int(255 * a),), width=6,
                    fill=col + (int(70 * a * (1 if age < 0.15 else 0.4)),))
    comp(img, lay, dim)
    d = ImageDraw.Draw(img, 'RGBA')
    if t >= 1.2 and t < T_STOP:
        d.text((W / 2, BY - 50), f'{cur} × {cur} squares', font=font(BOLD, 40), fill=size_col(cur), anchor='mm')
    ca = 1 - ramp(t, T_TWIST - 0.1, T_TWIST + 0.15)
    if ca > 0:
        l2 = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        n = 204 if t >= T_STOP else count(t)
        ImageDraw.Draw(l2).text((W / 2, 1378), f'{n}', font=font(BLACK, 116), fill=GOLD if t >= T_STOP else WHITE, anchor='mm')
        comp(img, l2, ca)
    st, pops = states(t)
    BR.overlay(img, t, st, pops)
    return punch(img, t, T_STOP)


render_frame = looped(frame_core, DUR)


def music(m):
    m.bed(0, T_STOP, cutoff=lambda tt: 0.05, vol=lambda tt: 0.03 * clamp(tt / 0.05), seed=21)
    m.drone(0, T_STOP, lambda tt: 65 + 6 * max([k for k in range(1, 9) if SIZE_START[k] <= tt] or [1]), vol=0.04)
    last = -1
    for (te, k, r, c) in EVENTS[:-1]:
        if te - last < 0.022:
            continue
        last = te
        pan = ((c + k / 2) / 8) * 1.6 - 0.8
        m.clack(te, f=1400 - 120 * k, vol=0.16 + 0.03 * k, pan=pan)
    for k in range(2, 8):
        m.whoosh(SIZE_START[k] - 0.25, 0.5, 0.15, -0.5, 0.5)
        m.bell(SIZE_START[k], note_freq(4 + k), 0.12)
    m.bell(T64, 1567.98, 0.14, -0.5)
    for hb in (T_STOP - 1.5, T_STOP - 1.08, T_STOP - 0.72):
        m.thump(hb, 0.5)
    m.silence(T_STOP - 0.32, T_STOP)
    m.stop_signature(T_STOP)
    m.clack(T_STOP, f=220, vol=0.6)
    m.bed(T_STOP + 0.4, DUR, cutoff=lambda tt: 0.02, vol=lambda tt: 0.012, seed=5)
    m.bell(T_TWIST, 659.25, 0.2, -0.3); m.bell(T_TWIST + 0.1, 987.77, 0.2, 0.3)


if __name__ == '__main__':
    main(render_frame, DUR, music, sys.argv)
