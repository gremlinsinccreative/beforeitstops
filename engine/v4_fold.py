"""FACT 001 - Fold paper 42 times. How thick is it? (grow engine, log scale)
Arithmetic: 0.1 mm x 2^42 = 439,805 km. Average Earth-Moon distance: 384,400 km (NASA)."""
import sys, math
from PIL import Image, ImageDraw
from lib import *

DUR, NF = 14.0, 42
Y0, PXD = 1500, 69.0                      # y of 0.1 mm; pixels per decade
T0, T1 = -0.2, 9.0
BX0, BX1 = 120, 270
MARKS = [(1e-4, '1 sheet: 0.1 mm', MUTED), (0.1, '10 cm: a hand width', MUTED), (100, '100 m: a 30-storey tower', MUTED),
         (8849, '8.8 km: Everest', MUTED), (1e5, '100 km: edge of space', MUTED),
         (3.844e8, '384,400 km: the Moon', GOLD)]


def y_of(m):
    return Y0 - (math.log10(m) + 4) * PXD


def t_fold(k):
    return T0 + (T1 - T0) * (k / NF) ** 0.9


def folds_at(t):
    if t >= 13.1:
        return NF * (1 - ease_io(ramp(t, 13.1, 13.85))) if t < 13.85 else folds_at(t - DUR)
    x = (t - T0) / (T1 - T0)
    if x <= 0:
        return 0.0
    if x >= 1:
        return float(NF)
    kf = NF * x ** (1 / 0.9)
    k = int(kf)
    return k + ease_out(min(1.0, (kf - k) * 1.7))


def fmt(m):
    if m < 0.01:
        return f'{m * 1000:.1f} mm'
    if m < 1:
        return f'{m * 100:.0f} cm'
    if m < 1000:
        return f'{m:.0f} m'
    km = m / 1000
    return f'{km:.1f} km' if km < 100 else f'{km:,.0f} km'


HOOK, _ = text_layer([('FACT 001', SEMI, 30, MUTED), ('Fold paper 42 times.', XB, 84, WHITE),
                      ('How thick is it?', XB, 84, WHITE), ('Guess before it stops.', SEMI, 40, GOLD)], 232)
REVEAL, _ = text_layer([('FACT 001', SEMI, 30, MUTED), ('Past the Moon', BLACK, 112, GOLD),
                        ('42 folds = 439,805 km', XB, 60, WHITE),
                        ('0.1 mm paper, doubled 42 times', MED, 30, MUTED)], 232)


def render_frame(t):
    img = new_frame()
    d = ImageDraw.Draw(img)
    f = folds_at(t)
    th = 1e-4 * 2 ** f
    ytop = y_of(th)
    d.rounded_rectangle([BX0 - 10, y_of(1e9) - 10, BX1 + 10, Y0 + 10], radius=18, fill=(16, 20, 30))
    for m, label, col in MARKS:
        y = y_of(m)
        passed = th >= m * 0.999
        c = (GOLD if col == GOLD else WHITE) if passed else col
        d.line([(BX1 + 14, y), (BX1 + 44, y)], fill=c, width=3)
        d.text((BX1 + 58, y), label, font=font(SEMI if passed else MED, 34), fill=c, anchor='lm')
    moon_y = y_of(3.844e8)
    d.rectangle([BX0, max(ytop, moon_y), BX1, Y0], fill=BLUE)
    if ytop < moon_y:
        d.rectangle([BX0, ytop, BX1, moon_y], fill=GOLD)
    d.rectangle([BX0, ytop - 4, BX1, ytop + 2], fill=WHITE)
    a = 1 - ease_io(ramp(t, 13.1, 13.4)) if t > 13 else 1
    k = min(NF, int(f + 1e-6))
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.text((700, 1360), f'FOLD {k}', font=font(SEMI, 40), fill=MUTED + (255,), anchor='mm')
    ld.text((700, 1432), fmt(1e-4 * 2 ** k), font=font(BLACK, 80), fill=WHITE + (255,), anchor='mm')
    comp(img, lay, a)
    rin = ease_io(ramp(t, T1 + 0.15, T1 + 0.5))
    comp(img, HOOK, (1 - rin) if t < 13 else ease_io(ramp(t, 13.5, 13.9)))
    comp(img, REVEAL, rin * (1 - ease_io(ramp(t, 13.1, 13.45))))
    return img


def audio(au):
    for k in range(1, NF + 1):
        au.tick(t_fold(k), freq=260 * 2 ** (k / 14), vol=0.2, dur=0.08)
    for m, _, _ in MARKS[1:]:
        kk = math.log2(m / 1e-4)
        au.thunk(t_fold(math.ceil(kk)), freq=120, vol=0.4)
    au.ding(T1 + 0.1)
    au.whoosh(13.05, dur=0.8, vol=0.2, up=False)


if __name__ == '__main__':
    run(render_frame, DUR, 'fact001_fold', audio, sys.argv)
