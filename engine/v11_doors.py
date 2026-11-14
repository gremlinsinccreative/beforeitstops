"""FACT 011 - 3 doors, 1 prize. Switch or stay? (tally engine, Monty Hall problem)
Arithmetic: your first pick is right 1 time in 3. The host, who knows where the prize is, always opens an
empty door among the other two, so switching wins exactly when the first pick was wrong: 2/3 = 66.7%.
The 300 games shown are a seeded random run chosen to end on exactly 200 switch wins (the expected value)."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from lib import *

DUR, N = 14.0, 300
T0, T1 = -0.6, 9.0
T_REV = T1 + 0.15
DX, DY, DW, DH = (300, 540, 780), 660, 150, 200
BX0, BX1 = 120, 960
DARK = (26, 32, 48)


def _games():
    for seed in range(10000):
        r = np.random.default_rng(seed)
        car, pick = r.integers(0, 3, N), r.integers(0, 3, N)
        if int((car != pick).sum()) == 200:
            host = [min(d for d in range(3) if d != c and d != p) for c, p in zip(car, pick)]
            return [int(x) for x in car], [int(x) for x in pick], host
    raise SystemExit('no seed')


CAR, PICK, HOST = _games()
SW = np.cumsum([c != p for c, p in zip(CAR, PICK)])
assert SW[-1] == 200 and abs(2 / 3 - SW[-1] / N) < 1e-12


def t_game(k):                               # k = 1..N, slow at first, then a blur
    return T0 + (T1 - T0) * math.sqrt(k / N)


def games_at(t):
    if t < t_game(1):
        return 0
    return min(N, int(N * ((t - T0) / (T1 - T0)) ** 2 + 1e-9))


HOOK, _ = text_layer([('FACT 011', SEMI, 30, MUTED), ('3 doors. 1 prize.', XB, 92, WHITE),
                      ('Switch or stay?', XB, 92, WHITE), ('Guess before it stops.', SEMI, 40, GOLD)], 232)
REVEAL, _ = text_layer([('FACT 011', SEMI, 30, MUTED), ('Switch.', BLACK, 128, GOLD),
                        ('It wins 2 times in 3', XB, 64, WHITE),
                        ('Staying only wins if your first pick was right: 1 in 3', MED, 32, MUTED)], 232)


def sim(t):
    lay, d = layer()
    n = games_at(t)
    if n:
        car, pick, host = CAR[n - 1], PICK[n - 1], HOST[n - 1]
        for i, x in enumerate(DX):
            box = [x - DW / 2, DY, x + DW / 2, DY + DH]
            if i == host:
                d.rounded_rectangle(box, radius=14, fill=BG + (255,), outline=MUTED + (255,), width=3)
                d.text((x, DY + DH / 2), 'empty', font=font(MED, 26), fill=MUTED + (255,), anchor='mm')
            if i == car:
                d.ellipse([x - 34, DY + DH / 2 - 34, x + 34, DY + DH / 2 + 34], fill=GOLD + (255,))
            if i == pick:
                d.rounded_rectangle([box[0] - 8, box[1] - 8, box[2] + 8, box[3] + 8], radius=20,
                                    outline=WHITE + (255,), width=5)
                d.text((x, DY + DH + 36), 'YOUR PICK', font=font(SEMI, 24), fill=WHITE + (255,), anchor='mm')
    sw = int(SW[n - 1]) if n else 0
    st = n - sw
    for y, name, v, col in ((1010, 'STAY', st, BLUE), (1120, 'SWITCH', sw, GOLD)):
        d.text((BX0, y - 30), f'{name} WINS', font=font(SEMI, 26), fill=MUTED + (255,), anchor='lm')
        d.text((BX1, y - 30), str(v), font=font(BOLD, 34), fill=WHITE + (255,), anchor='rm')
        if v:
            d.rounded_rectangle([BX0, y, BX0 + max(28, (BX1 - BX0) * v / 200), y + 44], radius=14, fill=col + (255,))
    if n:
        d.text((W / 2, 1270), f'Switch wins {100 * sw / n:.1f}%', font=font(BLACK, 76),
               fill=(GOLD if n == N else WHITE) + (255,), anchor='mm')
        d.text((W / 2, 1350), f'{n} GAME' + ('S' if n > 1 else '') + ' PLAYED', font=font(SEMI, 26),
               fill=MUTED + (255,), anchor='mm')
    return lay


def render_frame(t):
    img = new_frame()
    d = ImageDraw.Draw(img)
    d.text((W / 2, 610), 'You pick. The host opens an empty door.', font=font(MED, 30), fill=MUTED, anchor='mm')
    for x in DX:
        d.rounded_rectangle([x - DW / 2, DY, x + DW / 2, DY + DH], radius=14, fill=DARK)
    for y in (1010, 1120):
        d.rounded_rectangle([BX0, y, BX1, y + 44], radius=14, fill=DARK)
    loop_sim(img, sim, t, DUR)
    loop_text(img, HOOK, REVEAL, t, T_REV)
    return img


def audio(au):
    last = -1.0
    for k in range(1, N + 1):
        tk = t_game(k)
        if tk - last < 0.05:
            continue
        last = tk
        win = CAR[k - 1] != PICK[k - 1]
        au.tick(tk if tk >= 0 else tk + DUR, freq=(660 if win else 440) * 2 ** (k / 300), vol=0.2, dur=0.07)
    au.thunk(T1, freq=80, vol=0.6, dur=0.35)
    au.ding(T_REV)
    au.whoosh(13.05, dur=0.8, vol=0.2, up=False)


if __name__ == '__main__':
    run(render_frame, DUR, 'fact011_doors', audio, sys.argv)
