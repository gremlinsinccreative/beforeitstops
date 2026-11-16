"""FACT 015 - Which is hotter: lightning or the Sun's surface? (twin thermometer engine)
Sources: NOAA National Weather Service (weather.gov/safety/lightning-temperature): lightning can heat the air
it passes through to 50,000 F, "5 times hotter than the surface of the sun". NASA NSSDCA Sun Fact Sheet:
effective temperature 5772 K.
Arithmetic: 50,000 F = 27,760 C = 28,033 K. 5772 K = 5,499 C = 9,930 F. Ratio in kelvin 4.86, in F 5.04: about 5x."""
import sys
from PIL import Image, ImageDraw
from lib import *

DUR = 14.0
L_F, S_K = 50000.0, 5772.0
L_C = (L_F - 32) * 5 / 9
S_C = S_K - 273.15
S_F = S_C * 9 / 5 + 32
assert round(L_C) == 27760 and round(S_C) == 5499 and round(S_F) == 9930
assert 4.8 < (L_C + 273.15) / S_K < 5.1 and 4.9 < L_F / S_F < 5.1
L_SHOW, S_SHOW = round(L_C, -2), round(S_C, -2)           # 27,800 and 5,500
assert (L_SHOW, S_SHOW) == (27800, 5500)
T1 = 9.0
T_REV = T1 + 0.15
BASE, TOP = 1300, 690
PX = (BASE - TOP) / L_C
XL, XR, BW = 330, 750, 150
T_SUN = T1 * (S_C / L_C) ** (1 / 1.3) - 0.15
VIOLET = (170, 140, 255)


def temp(t):
    return L_C * ramp(t, -0.15, T1) ** 1.3


HOOK, _ = text_layer([('FACT 015', SEMI, 30, MUTED), ('Which is hotter: lightning', XB, 74, WHITE),
                      ("or the Sun's surface?", XB, 74, WHITE), ('Guess before it stops.', SEMI, 40, GOLD)], 232)
REVEAL, _ = text_layer([('FACT 015', SEMI, 30, MUTED), ('Lightning. 5x hotter.', BLACK, 96, VIOLET),
                        ('Air in a bolt: 27,800 °C (50,000 °F)', XB, 46, WHITE),
                        ("Sun's surface: about 5,500 °C", XB, 46, GOLD)], 232)


def sim(t):
    lay, d = layer()
    c = temp(t)
    for x, v, col in ((XL, min(c, S_C), GOLD), (XR, c, VIOLET)):
        h = v * PX
        if h > 2:
            d.rounded_rectangle([x - BW // 2, BASE - h, x + BW // 2, BASE], radius=14, fill=col + (255,))
    sun_done = c >= S_C
    sv = S_SHOW if sun_done else int(c // 100) * 100
    lv = L_SHOW if t >= T1 else int(c // 100) * 100
    d.text((XL, BASE - min(c, S_C) * PX - 44), f'{sv:,.0f} °C', font=font(BOLD, 46), fill=GOLD + (255,), anchor='mm')
    d.text((XR, BASE - c * PX - 44), f'{lv:,.0f} °C', font=font(BOLD, 46), fill=VIOLET + (255,), anchor='mm')
    if sun_done:
        d.text((XL, BASE - S_C * PX - 92), 'stops here', font=font(MED, 26), fill=MUTED + (255,), anchor='mm')
    if t > T1 + 1.0:
        d.text((W / 2, BASE + 130), 'Sources: NOAA National Weather Service; NASA', font=font(MED, 24),
               fill=MUTED + (int(255 * ease_io(ramp(t, T1 + 1.0, T1 + 1.4))),), anchor='mm')
    return lay


def render_frame(t):
    img = new_frame()
    d = ImageDraw.Draw(img)
    for x in (XL, XR):
        d.rounded_rectangle([x - BW // 2, TOP, x + BW // 2, BASE], radius=14, fill=(22, 27, 40))
    d.line([(160, BASE + 4), (920, BASE + 4)], fill=MUTED, width=3)
    d.text((XL, BASE + 44), "SUN'S SURFACE", font=font(SEMI, 28), fill=MUTED, anchor='mm')
    d.text((XR, BASE + 44), 'LIGHTNING BOLT', font=font(SEMI, 28), fill=MUTED, anchor='mm')
    loop_sim(img, sim, t, DUR)
    loop_text(img, HOOK, REVEAL, t, T_REV)
    return img


def audio(au):
    t = 0.0
    while t < T1:
        x = t / T1
        au.tick(t, freq=420 + 1300 * x, vol=0.14, dur=0.05)
        t += 0.12 - 0.07 * x
    au.ding(T_SUN, freqs=(880.0, 1318.5), vol=0.16, dur=0.7)
    au.thunk(T1, freq=80, vol=0.6, dur=0.35)
    au.ding(T_REV)
    au.whoosh(13.05, dur=0.8, vol=0.2, up=False)


if __name__ == '__main__':
    run(render_frame, DUR, 'fact015_lightning', audio, sys.argv)
