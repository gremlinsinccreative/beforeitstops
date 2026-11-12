"""FACT 009 - A rope around Earth. Add 1 metre. How high does it lift? (ruler engine)
Arithmetic: circumference C = 2*pi*r, so adding 1 m of rope adds 1/(2*pi) m of radius:
100 cm / (2*pi) = 15.9 cm, whatever the size of the sphere (idealised perfect circle, rope lifted evenly)."""
import sys, math
from PIL import Image, ImageDraw
from lib import *

DUR = 14.0
GAP = 100 / (2 * math.pi)                    # 15.915 cm
T0, T1 = -0.3, 9.0
T_REV = T1 + 0.15
EX, EY, ER = W // 2, 765, 130                # Earth disc
GROUND, PXCM = 1400, 22.5                    # ruler: y of ground, pixels per cm
RX = 250                                     # ruler x
SEA, LAND = (30, 96, 190), (70, 170, 110)


def gap_at(t):
    return GAP * (1 - (1 - ramp(t, T0, T1)) ** 2)


HOOK, _ = text_layer([('FACT 009', SEMI, 30, MUTED), ('A rope around Earth.', XB, 84, WHITE),
                      ('Add 1 metre. How high?', XB, 84, WHITE), ('Guess before it stops.', SEMI, 40, GOLD)], 232)
REVEAL, _ = text_layer([('FACT 009', SEMI, 30, MUTED), ('15.9 cm', BLACK, 128, GOLD),
                        ('all the way around', XB, 64, WHITE),
                        ('1 m ÷ 2π. Same for a tennis ball.', MED, 34, MUTED)], 232)


def sim(t):
    lay, d = layer()
    g = gap_at(t)
    rr = ER + 8 + 34 * g / GAP                # exaggerated ring radius
    d.ellipse([EX - rr, EY - rr, EX + rr, EY + rr], outline=GOLD + (255,), width=6)
    y = GROUND - g * PXCM
    d.rectangle([RX + 46, y - 5, 960, y + 5], fill=GOLD + (255,))
    d.polygon([(RX + 46, y), (RX + 22, y - 12), (RX + 22, y + 12)], fill=GOLD + (255,))
    d.text((960, y - 52), f'{g:.1f} cm', font=font(BLACK, 76), fill=WHITE + (255,), anchor='rm')
    d.text((RX + 70, y - 34), 'THE ROPE', font=font(SEMI, 24), fill=GOLD + (255,), anchor='lm')
    return lay


def render_frame(t):
    img = new_frame()
    d = ImageDraw.Draw(img)
    d.ellipse([EX - ER, EY - ER, EX + ER, EY + ER], fill=SEA)
    for cx, cy, r in ((-48, -42, 45), (35, -8, 38), (-18, 52, 33), (64, 60, 22), (52, -72, 19)):
        d.ellipse([EX + cx - r, EY + cy - r, EX + cx + r, EY + cy + r], fill=LAND)
    d.text((EX + ER + 150, EY), 'not to scale', font=font(MED, 24), fill=MUTED, anchor='mm')
    d.rectangle([120, GROUND, 960, GROUND + 26], fill=(26, 32, 48))
    d.text((960, GROUND + 13), 'GROUND', font=font(SEMI, 20), fill=MUTED, anchor='rm')
    d.line([(RX, GROUND), (RX, GROUND - 17 * PXCM)], fill=MUTED, width=3)
    for c in range(0, 18):
        y = GROUND - c * PXCM
        big = c % 5 == 0
        d.line([(RX - (26 if big else 12), y), (RX, y)], fill=WHITE if big else MUTED, width=3)
        if big:
            d.text((RX - 38, y), f'{c} cm', font=font(MED, 26), fill=WHITE, anchor='rm')
    loop_sim(img, sim, t, DUR)
    loop_text(img, HOOK, REVEAL, t, T_REV)
    return img


def audio(au):
    last = 0
    for i in range(int((T1 + 0.3) * 200)):
        t = -0.3 + i / 200
        c = int(gap_at(t))
        if c > last:
            last = c
            au.tick(max(t, 0), freq=380 * 2 ** (c / 12), vol=0.22, dur=0.09)
    au.thunk(T1, freq=80, vol=0.6, dur=0.35)
    au.ding(T_REV)
    au.whoosh(13.05, dur=0.8, vol=0.2, up=False)


if __name__ == '__main__':
    run(render_frame, DUR, 'fact009_rope', audio, sys.argv)
