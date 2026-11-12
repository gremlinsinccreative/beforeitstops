"""FACT 008 - A penny, doubled every day for 30 days (calendar engine + linear bar)
Arithmetic: day n holds 0.01 x 2^(n-1) dollars; day 30 = 0.01 x 2^29 = $5,368,709.12.
Day 20 = $5,242.88; first day above $1 million is day 28 ($1,342,177.28)."""
import sys
from PIL import Image, ImageDraw
from lib import *

DUR, ND = 14.0, 30
T0, T1 = -0.12, 9.0
T_REV = T1 + 0.15
COLS, CW, CHH = 6, 160, 112
GX, GY = (W - COLS * CW) // 2, 630
BY = GY + 5 * CHH + 70                       # linear bar
FINAL = 0.01 * 2 ** (ND - 1)
CELL = (26, 32, 48)


def amount(n):
    return 0.01 * 2 ** (n - 1)


def short(v):
    if v < 100:
        return f'${v:.2f}'
    if v < 10000:
        return f'${v:,.0f}'
    if v < 1e6:
        return f'${v / 1000:.0f}K'
    return f'${v / 1e6:.1f}M'


def t_day(n):
    return T0 + (T1 - T0) * (n - 1) / (ND - 1)


def days_at(t):
    if t < T0:
        return 0
    return min(ND, 1 + int((t - T0) / (T1 - T0) * (ND - 1) + 1e-9))


HOOK, _ = text_layer([('FACT 008', SEMI, 30, MUTED), ('A penny, doubled daily.', XB, 84, WHITE),
                      ('How much on day 30?', XB, 84, WHITE), ('Guess before it stops.', SEMI, 40, GOLD)], 232)
REVEAL, _ = text_layer([('FACT 008', SEMI, 30, MUTED), ('$5,368,709.12', BLACK, 120, GOLD),
                        ('on day 30', XB, 64, WHITE),
                        ('1 cent, doubled 29 times', MED, 34, MUTED)], 232)


def sim(t):
    lay, d = layer()
    n = days_at(t)
    for k in range(1, n + 1):
        x, y = GX + (k - 1) % COLS * CW, GY + (k - 1) // COLS * CHH
        age = t - t_day(k)
        v = amount(k)
        col = GOLD if v >= 1e6 else BLUE
        pop = 6 * max(0.0, 1 - age * 5)
        d.rounded_rectangle([x + 6 - pop, y + 6 - pop, x + CW - 6 + pop, y + CHH - 6 + pop], radius=14,
                            fill=col + (255,))
        d.text((x + CW / 2, y + 36), f'DAY {k}', font=font(SEMI, 22), fill=BG + (255,), anchor='mm')
        d.text((x + CW / 2, y + 72), short(v), font=font(BLACK, 36), fill=BG + (255,), anchor='mm')
    v = amount(n) if n else 0.0
    frac = v / FINAL
    if frac > 0.002:
        d.rounded_rectangle([GX + 6, BY, GX + 6 + (COLS * CW - 12) * frac, BY + 40], radius=12,
                            fill=(GOLD if v >= 1e6 else BLUE) + (255,))
    if n:
        d.text((W / 2, BY + 150), f'Day {n}:  ${v:,.2f}', font=font(BLACK, 72), fill=WHITE + (255,), anchor='mm')
    return lay


def render_frame(t):
    img = new_frame()
    d = ImageDraw.Draw(img)
    for k in range(ND):
        x, y = GX + k % COLS * CW, GY + k // COLS * CHH
        d.rounded_rectangle([x + 6, y + 6, x + CW - 6, y + CHH - 6], radius=14, fill=CELL)
        d.text((x + CW / 2, y + 36), f'DAY {k + 1}', font=font(SEMI, 22), fill=MUTED, anchor='mm')
    d.rounded_rectangle([GX + 6, BY, GX + COLS * CW - 6, BY + 40], radius=12, fill=CELL)
    d.text((GX + 6, BY + 66), '$0', font=font(MED, 24), fill=MUTED, anchor='lm')
    d.text((GX + COLS * CW - 6, BY + 66), '$5.37 million', font=font(MED, 24), fill=MUTED, anchor='rm')
    loop_sim(img, sim, t, DUR)
    loop_text(img, HOOK, REVEAL, t, T_REV)
    return img


def audio(au):
    for k in range(1, ND + 1):
        au.tick(t_day(k), freq=300 * 2 ** (k / 15), vol=0.2, dur=0.08)
        if t_day(k) < 0:
            au.tick(t_day(k) + DUR, freq=300 * 2 ** (k / 15), vol=0.2, dur=0.08)
    au.thunk(t_day(28), freq=120, vol=0.4)
    au.thunk(T1, freq=80, vol=0.6, dur=0.35)
    au.ding(T_REV)
    au.whoosh(13.05, dur=0.8, vol=0.2, up=False)


if __name__ == '__main__':
    run(render_frame, DUR, 'fact008_penny', audio, sys.argv)
