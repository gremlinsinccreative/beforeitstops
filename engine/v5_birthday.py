"""FACT 003 - 23 people in a room: do two share a birthday? (drop engine)
Arithmetic: P(n) = 1 - prod_{k<n} (365-k)/365; P(23) = 50.7%. Assumes 365 equally likely birthdays."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from lib import *

DUR, N = 14.0, 23
MONTHS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
CP, RP = 27, 44
GX, GY = (W - 31 * CP) // 2 + 34, 640
MX0, MX1, MY = GX, GX + 31 * CP - 6, 1250
STEP, FALL = 0.355, 0.3
T_REV = -0.12 + STEP * (N - 1) + FALL + 0.45
rng = np.random.default_rng(23)
DAYS = [int(x) for x in rng.choice(365, N, replace=False)]


def cell_xy(day):
    m = 0
    while day >= MONTHS[m]:
        day -= MONTHS[m]
        m += 1
    return GX + day * CP, GY + m * RP


def prob(n):
    p = 1.0
    for k in range(n):
        p *= (365 - k) / 365
    return 1 - p


def t_start(k):
    return -0.12 + STEP * k


HOOK, _ = text_layer([('FACT 003', SEMI, 30, MUTED), ('23 people in a room.', XB, 84, WHITE),
                      ('Two share a birthday?', XB, 84, WHITE), ('Guess the odds.', SEMI, 40, GOLD)], 232)
REVEAL, _ = text_layer([('FACT 003', SEMI, 30, MUTED), ('50.7%', BLACK, 128, GOLD),
                        ('Better than a coin flip', XB, 60, WHITE),
                        ('with just 23 people', XB, 60, WHITE)], 232)


def draw_people(d, tt, clear=0.0):
    landed = 0
    for k in range(N):
        x, y = cell_xy(DAYS[k])
        u = (tt - t_start(k)) / FALL
        if u < 0:
            continue
        if u < 1:
            yy = 560 + (y - 560) * ease_in(u) if u > 0 else 560
            d.ellipse([x + 1, yy + 4, x + 21, yy + 24], fill=WHITE)
        else:
            landed += 1
            pop = 1 + 0.5 * max(0.0, 1 - (u - 1) * 2.5)
            c = BLUE if clear <= 0 else tuple(int(BLUE[i] + ((26, 32, 48)[i] - BLUE[i]) * clear) for i in range(3))
            w, h = 21 * pop, 34 * pop
            cx, cy = x + 10.5, y + 17
            d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=5, fill=c)
    return landed


def render_frame(t):
    img = new_frame()
    d = ImageDraw.Draw(img)
    for m in range(12):
        d.text((GX - 16, GY + m * RP + 17), NAMES[m], font=font(MED, 24), fill=MUTED, anchor='rm')
        for day in range(MONTHS[m]):
            x, y = GX + day * CP, GY + m * RP
            d.rounded_rectangle([x, y, x + 21, y + 34], radius=5, fill=(26, 32, 48))
    clear = ease_io(ramp(t, 13.05, 13.5))
    n = draw_people(d, t, clear)
    if t > 13.5:
        draw_people(d, t - DUR)
    p = prob(n) * (1 - clear)
    d.text((MX0, MY - 38), 'CHANCE THAT TWO SHARE A BIRTHDAY', font=font(SEMI, 26), fill=MUTED, anchor='lm')
    d.rounded_rectangle([MX0, MY, MX1, MY + 44], radius=14, fill=(26, 32, 48))
    if p > 0.004:
        d.rounded_rectangle([MX0, MY, MX0 + (MX1 - MX0) * p, MY + 44], radius=14, fill=GOLD if p >= 0.5 else BLUE)
    mid = (MX0 + MX1) / 2
    d.line([(mid, MY - 10), (mid, MY + 54)], fill=WHITE, width=3)
    d.text((mid, MY + 78), '50%', font=font(SEMI, 26), fill=WHITE, anchor='mm')
    a = 1 - clear
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    who = '1 person' if n == 1 else f'{n} people'
    ld.text((W / 2, MY + 150), f'{who}:  {p * 100:.1f}%', font=font(BLACK, 76), fill=WHITE + (255,), anchor='mm')
    comp(img, lay, a)
    rin = ease_io(ramp(t, T_REV, T_REV + 0.35))
    comp(img, HOOK, (1 - rin) if t < 13 else ease_io(ramp(t, 13.5, 13.9)))
    comp(img, REVEAL, rin * (1 - ease_io(ramp(t, 13.1, 13.45))))
    return img


def audio(au):
    for k in range(N):
        tl = t_start(k) + FALL
        au.tick(tl, freq=420 * 2 ** (k / 12), vol=0.22, dur=0.09)
        if tl + DUR < DUR:
            au.tick(tl + DUR, freq=420, vol=0.22, dur=0.09)
    au.thunk(t_start(N - 1) + FALL, freq=90, vol=0.6, dur=0.35)
    au.ding(T_REV)
    au.whoosh(13.0, dur=0.8, vol=0.2, up=False)


if __name__ == '__main__':
    run(render_frame, DUR, 'fact003_birthday', audio, sys.argv)
