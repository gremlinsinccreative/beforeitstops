"""v6 FACT 019 Quake 9 vs quake 6: how much more energy? Smooth version, 13 s.
USGS: each whole-number step = 10x amplitude, about 32x energy -> 3 steps = 32^3 = 32,768 (about 32,000x) energy,
1,000x amplitude. Magnitude climbs on an eased curve that slows at M7 and M8 (label held ~1 s each);
the seismograph swing grows 10x per step and freezes at the STOP. Drum beat, ding per milestone, roll, drop."""
import sys, math
from scipy.interpolate import PchipInterpolator
from lib import *
from brand2 import *
import p10_quake as Q

DUR, T_STOP, T_TWIST = 13.0, 9.6, 11.0
KEYS = [(0, 6.0), (1.6, 6.55), (2.9, 6.97), (3.6, 7.04), (5.2, 7.93), (6.0, 8.05), (8.4, 8.86), (9.6, 9.0)]
_P = PchipInterpolator([k[0] for k in KEYS], [k[1] for k in KEYS])


def mag(t):
    return float(_P(min(max(t, 0.0), T_STOP)))


def t_at(mm):
    lo, hi = 0.0, T_STOP
    for _ in range(40):
        md = (lo + hi) / 2
        lo, hi = (lo, md) if mag(md) >= mm else (md, hi)
    return hi


MILESTONES = [(7, t_at(7.0), '×32 energy'), (8, t_at(8.0), '×1,024 energy')]
Q.mag = mag                                  # reuse p10's drawing with the smooth curve
Q.T_STOP, Q.T_TWIST, Q.DUR = T_STOP, T_TWIST, DUR
Q.BR = Brand2(19, ['Quake 9 vs quake 6:', 'how much more energy?'], 'Quake 9 vs 6: how much more energy?',
              [('A', '1,000×'), ('B', '32,000×'), ('C', '1,000,000×')],
              [('About 32,000×', BLACK, 120, GOLD), ('more energy  ·  Source: USGS', BOLD, 44, WHITE)],
              [('The shaking? Only', BOLD, 48, WHITE), ('1,000× bigger', BLACK, 96, GOLD)], T_STOP, T_TWIST, DUR,
              sub='Guess A, B or C · wait for the 9', cta='Comment your letter', q_size=84)


def frame_core(t):
    img = Q.frame_core(t)
    for mm, tp, txt in MILESTONES:
        a = ease_io(ramp(t, tp - 0.2, tp + 0.05)) * (1 - ease_io(ramp(t, tp + 0.9, tp + 1.15)))
        if a > 0.02 and t < T_STOP:
            lb, _ = big_text([(f'Magnitude {mm}', XB, 60, WHITE)], 0)
            sub = lb.crop(lb.getbbox())
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            lay.alpha_composite(sub, (70, 330))
            comp(img, lay, a)
    return img


render_frame = looped(frame_core, DUR, xf=0.5)


def music(mu):
    from brand import drum_track, ding, drop_hit
    lvl = lambda tt: (mag(tt) - 6) / 3
    mu.bed(0, T_STOP, cutoff=lambda tt: 0.03 + 0.08 * lvl(tt), vol=lambda tt: (0.015 + 0.06 * lvl(tt) ** 1.5) * clamp(tt / 0.05), seed=31)
    drum_track(mu, T_STOP - 0.32, lvl, bpm0=96, bpm1=150, key=-5, roll=1.4)
    for mm, tp, _ in MILESTONES:
        ding(mu, tp, key=-5, vol=0.15)
        mu.boom(tp, 0.25, 1.0)
    mu.silence(T_STOP - 0.32, T_STOP)
    drop_hit(mu, T_STOP, key=-5)
    mu.bed(T_STOP + 0.4, DUR, cutoff=lambda tt: 0.02, vol=lambda tt: 0.01, seed=5)
    mu.bell(T_TWIST, 659.25 * 2 ** (-5 / 12), 0.16, -0.3); mu.bell(T_TWIST + 0.1, 987.77 * 2 ** (-5 / 12), 0.16, 0.3)


if __name__ == '__main__':
    main(render_frame, DUR, music, sys.argv)
