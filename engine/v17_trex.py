"""FACT 017 - T. rex lived closer in time to you or to Stegosaurus? (timeline race engine)
Source: Natural History Museum, London, Dino Directory: Stegosaurus "Late Jurassic, 152-145 million years ago";
Tyrannosaurus "Late Cretaceous, 68-66 million years ago".
Worst case for the claim: last Stegosaurus (145) to first T. rex (68) = 77 million years; first T. rex to
today = 68 million years. 77 > 68, so it holds across the whole of both ranges; margin at least 9."""
import sys
from PIL import Image, ImageDraw
from lib import *

DUR = 14.0
ST_A, ST_B, TR_A, TR_B = 152, 145, 68, 66
Y_L, Y_R = ST_B - TR_A, TR_A
assert (Y_L, Y_R, Y_L - Y_R) == (77, 68, 9)
X0, X1, TY = 70, 1010, 1010
AXIS = 155.0
PXY = (X1 - X0) / AXIS
xa = lambda mya: X0 + (AXIS - mya) * PXY
CX = xa(TR_A)
T0, T1 = -0.15, 9.0
V = Y_L / (T1 - T0)
T_R = T0 + Y_R / V
T_REV = T1 + 0.15
GREEN = (86, 214, 130)


def years(t):
    y = max(0.0, (t - T0) * V)
    return min(Y_L, y), min(Y_R, y)


HOOK, _ = text_layer([('FACT 017', SEMI, 30, MUTED), ('T. rex lived closer in time', XB, 72, WHITE),
                      ('to you or to Stegosaurus?', XB, 72, WHITE), ('Guess before it stops.', SEMI, 40, GOLD)], 232)
REVEAL, _ = text_layer([('FACT 017', SEMI, 30, MUTED), ('To you.', BLACK, 128, GOLD),
                        ('by at least 9 million years', XB, 60, WHITE),
                        ('Source: Natural History Museum, London', MED, 30, MUTED)], 232)


def sim(t):
    lay, d = layer()
    yl, yr = years(t)
    if yl > 0.3:
        d.rounded_rectangle([CX - yl * PXY, TY - 26, CX, TY + 26], radius=12, fill=GREEN + (255,))
    if yr > 0.3:
        d.rounded_rectangle([CX, TY - 26, CX + yr * PXY, TY + 26], radius=12, fill=GOLD + (255,))
    d.ellipse([CX - 20, TY - 20, CX + 20, TY + 20], fill=WHITE + (255,))
    xl, xr = (xa(ST_B) + CX) / 2, (CX + X1) / 2
    d.text((xl, TY + 170), f'{int(yl)}', font=font(BLACK, 110), fill=GREEN + (255,), anchor='mm')
    d.text((xl, TY + 246), 'million years', font=font(SEMI, 32), fill=MUTED + (255,), anchor='mm')
    d.text((xr, TY + 170), f'{int(yr)}', font=font(BLACK, 110), fill=GOLD + (255,), anchor='mm')
    d.text((xr, TY + 246), 'million years', font=font(SEMI, 32), fill=MUTED + (255,), anchor='mm')
    return lay


def render_frame(t):
    img = new_frame()
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([X0, TY - 26, X1, TY + 26], radius=12, fill=(22, 27, 40))
    d.rectangle([xa(ST_A), TY - 26, xa(ST_B), TY + 26], fill=(40, 96, 62))
    for m in range(150, -1, 50):
        x = xa(m)
        d.line([(x, TY + 34), (x, TY + 48)], fill=(60, 70, 92), width=2)
        d.text((x, TY + 70), f'{m}M' if m else 'now', font=font(MED, 22), fill=(90, 100, 124), anchor='mm')
    d.text((X0, TY - 150), 'Stegosaurus', font=font(BOLD, 40), fill=GREEN, anchor='lm')
    d.text((X0, TY - 100), '152-145 million years ago', font=font(MED, 26), fill=MUTED, anchor='lm')
    d.line([(xa(ST_B), TY - 74), (xa(ST_B), TY - 34)], fill=GREEN, width=4)
    d.text((CX, TY - 150), 'T. rex', font=font(BOLD, 40), fill=WHITE, anchor='mm')
    d.text((CX, TY - 100), '68-66 million years ago', font=font(MED, 26), fill=MUTED, anchor='mm')
    d.text((X1, TY - 150), 'You', font=font(BOLD, 40), fill=GOLD, anchor='rm')
    d.text((X1, TY - 100), 'today', font=font(MED, 26), fill=MUTED, anchor='rm')
    d.line([(X1 - 3, TY - 74), (X1 - 3, TY - 34)], fill=GOLD, width=4)
    loop_sim(img, sim, t, DUR)
    loop_text(img, HOOK, REVEAL, t, T_REV)
    return img


def audio(au):
    for y in range(2, Y_L + 1, 2):
        au.tick(T0 + y / V, freq=380 + y * 9, vol=0.18, dur=0.07)
    au.ding(T_R, freqs=(880.0, 1318.5), vol=0.2, dur=0.9)
    au.thunk(T1, freq=80, vol=0.6, dur=0.35)
    au.ding(T_REV)
    au.whoosh(13.05, dur=0.8, vol=0.2, up=False)


if __name__ == '__main__':
    run(render_frame, DUR, 'fact017_trex', audio, sys.argv)
