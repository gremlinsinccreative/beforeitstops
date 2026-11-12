"""FACT 010 - Shuffle a deck of cards. Has this order existed before? (counter engine)
Arithmetic: 52 cards can be ordered in 52! = 52 x 51 x ... x 1 ways =
80,658,175,170,943,878,571,660,636,856,403,766,975,289,505,440,883,277,824,000,000,000,000 (68 digits, about 8 x 10^67)."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from lib import *

DUR, N = 14.0, 52
T0, T1 = -0.1, 9.0
T_REV = T1 + 0.15
CP, RP, CW, CHH = 74, 104, 62, 90
GX, GY = (W - 13 * CP) // 2 + 6, 630
NY = GY + 4 * RP + 60
RED, INK = (226, 62, 74), (16, 20, 30)
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
ORDER = [int(x) for x in np.random.default_rng(52).permutation(52)]
assert len(str(math.factorial(52))) == 68


def t_card(k):                               # k = 1..52
    return T0 + (T1 - T0) * ((k - 1) / (N - 1)) ** 0.9


def cards_at(t):
    k = 0
    while k < N and t >= t_card(k + 1):
        k += 1
    return k


def lines_of(n):
    g = f'{n:,}'.split(',')
    return [','.join(g[i:i + 8]) + (',' if i + 8 < len(g) else '') for i in range(0, len(g), 8)]


HOOK, _ = text_layer([('FACT 010', SEMI, 30, MUTED), ('Shuffle a deck of cards.', XB, 80, WHITE),
                      ('Has this order existed?', XB, 80, WHITE), ('Guess before it stops.', SEMI, 40, GOLD)], 232)
REVEAL, _ = text_layer([('FACT 010', SEMI, 30, MUTED), ('Almost certainly', BLACK, 104, GOLD),
                        ('never.', BLACK, 104, GOLD),
                        ('52 cards: a 68-digit number of orders', MED, 34, MUTED)], 232)


def sim(t):
    lay, d = layer()
    n = cards_at(t)
    for k in range(1, n + 1):
        x, y = GX + (k - 1) % 13 * CP, GY + (k - 1) // 13 * RP
        c = ORDER[k - 1]
        pop = 7 * max(0.0, 1 - (t - t_card(k)) * 6)
        d.rounded_rectangle([x - pop, y - pop, x + CW + pop, y + CHH + pop], radius=9, fill=WHITE + (255,))
        col = RED if c // 13 in (1, 2) else INK
        d.text((x + CW / 2, y + CHH / 2 - 8), RANKS[c % 13], font=font(BLACK, 38), fill=col + (255,), anchor='mm')
        d.ellipse([x + CW / 2 - 6, y + CHH - 22, x + CW / 2 + 6, y + CHH - 10], fill=col + (255,))
    if n:
        d.text((W / 2, NY), f'POSSIBLE ORDERS OF {n} CARD' + ('S' if n > 1 else ''), font=font(SEMI, 26),
               fill=MUTED + (255,), anchor='mm')
        for i, s in enumerate(lines_of(math.factorial(n))):
            d.text((W / 2, NY + 62 + i * 56), s, font=font(BOLD, 46), fill=(GOLD if n == N else WHITE) + (255,),
                   anchor='mm')
    return lay


def render_frame(t):
    img = new_frame()
    d = ImageDraw.Draw(img)
    for k in range(N):
        x, y = GX + k % 13 * CP, GY + k // 13 * RP
        d.rounded_rectangle([x, y, x + CW, y + CHH], radius=9, fill=(26, 32, 48))
    loop_sim(img, sim, t, DUR)
    loop_text(img, HOOK, REVEAL, t, T_REV)
    return img


def audio(au):
    for k in range(1, N + 1):
        tk = t_card(k)
        au.tick(tk if tk >= 0 else tk + DUR, freq=360 * 2 ** (k / 26), vol=0.2, dur=0.07)
    au.thunk(T1, freq=80, vol=0.6, dur=0.35)
    au.ding(T_REV)
    au.whoosh(13.05, dur=0.8, vol=0.2, up=False)


if __name__ == '__main__':
    run(render_frame, DUR, 'fact010_deck', audio, sys.argv)
