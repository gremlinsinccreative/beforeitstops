"""FACT 012 - How old is the sunlight you see right now? (travel engine)
Arithmetic: 1 astronomical unit = 149,597,870,700 m exactly (IAU 2012 Resolution B2); speed of light =
299,792,458 m/s exactly (SI). 149,597,870,700 / 299,792,458 = 499.0 s = 8 min 19 s at Earth's mean distance
(about 8 min 11 s at perihelion, 8 min 27 s at aphelion; NASA Earth fact sheet 147.095 and 152.100 million km)."""
import sys, math
from PIL import Image, ImageDraw, ImageFilter
from lib import *

DUR = 14.0
AU_M, C = 149_597_870_700, 299_792_458
SECS = AU_M / C
assert abs(SECS - 499.0048) < 1e-3 and divmod(int(SECS), 60) == (8, 19)
T0, T1 = -0.3, 9.0
T_REV = T1 + 0.15
SX, EX, Y, SR_, ER = 170, 930, 800, 92, 24
X0, X1 = SX + SR_, EX - ER


def prog(t):
    return ramp(t, T0, T1)


HOOK, _ = text_layer([('FACT 012', SEMI, 30, MUTED), ('How old is the sunlight', XB, 84, WHITE),
                      ('you see right now?', XB, 84, WHITE), ('Guess before it stops.', SEMI, 40, GOLD)], 232)
REVEAL, _ = text_layer([('FACT 012', SEMI, 30, MUTED), ('8 min 19 s', BLACK, 128, GOLD),
                        ('It left the Sun that long ago', XB, 60, WHITE),
                        ('149.6 million km ÷ 299,792 km/s (IAU, SI)', MED, 32, MUTED)], 232)

_g = Image.new('RGBA', (W, H), (0, 0, 0, 0))
ImageDraw.Draw(_g).ellipse([SX - 150, Y - 150, SX + 150, Y + 150], fill=GOLD + (70,))
GLOW = _g.filter(ImageFilter.GaussianBlur(40))


def sim(t):
    lay, d = layer()
    u = prog(t)
    x = X0 + (X1 - X0) * u
    if x - X0 > 2:
        d.line([(X0, Y), (x, Y)], fill=GOLD + (110,), width=6)
    d.ellipse([x - 13, Y - 13, x + 13, Y + 13], fill=WHITE + (255,))
    s = int(SECS * u)
    d.text((W / 2, 1090), f'{s // 60}:{s % 60:02d}', font=font(BLACK, 170), fill=(GOLD if u >= 1 else WHITE) + (255,),
           anchor='mm')
    d.text((W / 2, 1200), 'MINUTES SINCE IT LEFT THE SUN', font=font(SEMI, 26), fill=MUTED + (255,), anchor='mm')
    d.text((W / 2, 1290), f'{AU_M / 1e9 * u:.1f} million km', font=font(BOLD, 54), fill=WHITE + (255,), anchor='mm')
    return lay


def render_frame(t):
    img = new_frame()
    img.alpha_composite(GLOW)
    d = ImageDraw.Draw(img)
    d.ellipse([SX - SR_, Y - SR_, SX + SR_, Y + SR_], fill=GOLD)
    d.ellipse([EX - ER, Y - ER, EX + ER, Y + ER], fill=(40, 120, 220))
    d.ellipse([EX - 14, Y - 16, EX + 4, Y + 2], fill=(70, 170, 110))
    d.text((SX, Y + SR_ + 40), 'SUN', font=font(SEMI, 26), fill=MUTED, anchor='mm')
    d.text((EX, Y + SR_ + 40), 'EARTH', font=font(SEMI, 26), fill=MUTED, anchor='mm')
    d.text((W / 2, Y - 130), 'sizes not to scale', font=font(MED, 24), fill=MUTED, anchor='mm')
    for m in range(1, 9):                     # one tick per light-minute
        x = X0 + (X1 - X0) * (m * 60 / SECS)
        d.line([(x, Y + 26), (x, Y + 46)], fill=MUTED, width=3)
        d.text((x, Y + 68), str(m), font=font(MED, 24), fill=MUTED, anchor='mm')
    d.text((W / 2, Y + 108), 'light-minutes', font=font(MED, 24), fill=MUTED, anchor='mm')
    loop_sim(img, sim, t, DUR)
    loop_text(img, HOOK, REVEAL, t, T_REV)
    return img


def audio(au):
    for m in range(0, 9):
        tm = T0 + (T1 - T0) * (m * 60 / SECS)
        au.tick(max(tm, 0), freq=392 * 2 ** (m / 12), vol=0.24, dur=0.12)
    au.thunk(T1, freq=80, vol=0.6, dur=0.35)
    au.ding(T_REV)
    au.whoosh(13.05, dur=0.8, vol=0.2, up=False)


if __name__ == '__main__':
    run(render_frame, DUR, 'fact012_sunlight', audio, sys.argv)
