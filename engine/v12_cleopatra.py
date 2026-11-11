"""FACT 002 - Cleopatra: closer to the pyramids or the Moon landing? (timeline race engine)
Dates: Great Pyramid of Giza completed c. 2560 BC; Cleopatra VII died 30 BC; Apollo 11 landed 1969.
30 BC -> 1969 = 1,998 years (no year zero). 2560 BC -> 30 BC = 2,530 years."""
import sys
from PIL import Image, ImageDraw
from lib import *

DUR = 14.0
X0, X1, TY = 70, 1010, 1010
SPAN = 2560 + 1969 - 1
PXY = (X1 - X0) / SPAN
CX = X0 + 2530 * PXY
Y_L, Y_R = 2530, 1998
T0, T1 = -0.15, 9.0
V = Y_L / (T1 - T0)
T_R = T0 + Y_R / V


def years(t):
    if t >= 13.1:
        if t < 13.8:
            k = 1 - ease_io(ramp(t, 13.1, 13.8))
            return Y_L * k, Y_R * k
        return years(t - DUR)
    y = max(0.0, (t - T0) * V)
    return min(Y_L, y), min(Y_R, y)


HOOK, _ = text_layer([('FACT 002', SEMI, 30, MUTED), ('Cleopatra lived closer to', XB, 70, WHITE),
                      ('the pyramids or the Moon landing?', XB, 58, WHITE),
                      ('Guess before it stops.', SEMI, 40, GOLD)], 232)
REVEAL, _ = text_layer([('FACT 002', SEMI, 30, MUTED), ('The Moon landing', BLACK, 108, GOLD),
                        ('by about 500 years', XB, 60, WHITE),
                        ('Great Pyramid c. 2560 BC. Cleopatra died 30 BC.', MED, 30, MUTED)], 232)


def render_frame(t):
    img = new_frame()
    d = ImageDraw.Draw(img)
    yl, yr = years(t)
    d.rounded_rectangle([X0, TY - 26, X1, TY + 26], radius=12, fill=(22, 27, 40))
    for yr_tick in range(-2500, 2000, 500):
        x = X0 + (yr_tick + 2560) * PXY
        d.line([(x, TY + 34), (x, TY + 48)], fill=(60, 70, 92), width=2)
        lab = f'{-yr_tick} BC' if yr_tick < 0 else (f'AD {yr_tick}' if yr_tick > 0 else '1 BC / AD 1')
        if yr_tick % 1000 == 0 and yr_tick != 0:
            d.text((x, TY + 70), lab, font=font(MED, 22), fill=(90, 100, 124), anchor='mm')
    if yl > 0:
        d.rounded_rectangle([CX - yl * PXY, TY - 26, CX, TY + 26], radius=12, fill=BLUE)
    if yr > 0:
        d.rounded_rectangle([CX, TY - 26, CX + yr * PXY, TY + 26], radius=12, fill=GOLD)
    d.ellipse([CX - 20, TY - 20, CX + 20, TY + 20], fill=WHITE)
    left_done, right_done = yl >= Y_L - 0.5, yr >= Y_R - 0.5
    d.text((X0, TY - 150), 'Great Pyramid', font=font(BOLD, 40), fill=BLUE if left_done else MUTED, anchor='lm')
    d.text((X0, TY - 100), 'c. 2560 BC', font=font(MED, 30), fill=MUTED, anchor='lm')
    d.line([(X0 + 3, TY - 74), (X0 + 3, TY - 34)], fill=BLUE if left_done else MUTED, width=4)
    d.text((CX, TY - 150), 'Cleopatra', font=font(BOLD, 40), fill=WHITE, anchor='mm')
    d.text((CX, TY - 100), 'd. 30 BC', font=font(MED, 30), fill=MUTED, anchor='mm')
    d.text((X1, TY - 150), 'Moon landing', font=font(BOLD, 40), fill=GOLD if right_done else MUTED, anchor='rm')
    d.text((X1, TY - 100), '1969', font=font(MED, 30), fill=MUTED, anchor='rm')
    d.line([(X1 - 3, TY - 74), (X1 - 3, TY - 34)], fill=GOLD if right_done else MUTED, width=4)
    a = (1 - ease_io(ramp(t, 13.1, 13.4))) if t > 13 else 1.0
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.text(((X0 + CX) / 2, TY + 170), f'{int(yl):,}', font=font(BLACK, 96), fill=BLUE + (255,), anchor='mm')
    ld.text(((X0 + CX) / 2, TY + 240), 'years', font=font(SEMI, 32), fill=MUTED + (255,), anchor='mm')
    ld.text(((CX + X1) / 2, TY + 170), f'{int(yr):,}', font=font(BLACK, 96), fill=GOLD + (255,), anchor='mm')
    ld.text(((CX + X1) / 2, TY + 240), 'years', font=font(SEMI, 32), fill=MUTED + (255,), anchor='mm')
    comp(img, lay, a)
    rin = ease_io(ramp(t, T1 + 0.15, T1 + 0.5))
    comp(img, HOOK, (1 - rin) if t < 13 else ease_io(ramp(t, 13.5, 13.9)))
    comp(img, REVEAL, rin * (1 - ease_io(ramp(t, 13.1, 13.45))))
    return img


def audio(au):
    for y in range(100, Y_L + 1, 100):
        au.tick(T0 + y / V, freq=380 + y * 0.28, vol=0.18, dur=0.07)
    au.ding(T_R, freqs=(880.0, 1318.5), vol=0.2, dur=0.9)
    au.thunk(T1, freq=80, vol=0.6, dur=0.35)
    au.ding(T1 + 0.1)
    au.whoosh(13.05, dur=0.8, vol=0.2, up=False)


if __name__ == '__main__':
    run(render_frame, DUR, 'fact002_cleopatra', audio, sys.argv)
