"""TEST A - FACT 001 fold, identical picture to p5_fold.py; only the sound changes (competitor lesson:
'the sound is the payoff'). Each doubling speeds up a tick train: ~3 ticks/s at fold 3, ~190/s at fold 42,
so the ticks fuse into a rising note. The STOP is a full drop: silence, then the signature."""
import sys, math
from p5_fold import *
import p5_fold as base


def rate(tt):
    return 2.2 * 2 ** (base.nvis(tt) / 6.5)


def music(m):
    lhs = lambda tt: (math.log10(alt(nfold(tt))) + 4) / 12.6
    m.bed(0, T_STOP, cutoff=lambda tt: 0.9 - 0.85 * clamp(lhs(tt) * 1.15),
          vol=lambda tt: 0.035 * (1 - 0.7 * clamp(lhs(tt) * 1.2)) * clamp(tt / 0.05), seed=3)
    m.drone(0, T_STOP, lambda tt: 40 + 1.2 * nfold(tt), vol=0.03)
    m.click_train(0, T_STOP - 0.3, rate, vol=0.28)
    # an octave-up shadow that fades in late, so the note gets brighter as it climbs
    m.click_train(4.0, T_STOP - 0.3, lambda tt: 2 * rate(tt), vol=0.08, tone=2600, pan=0.0)
    pans = {'Burj Khalifa': (-0.9, 0.2), 'Everest': (0.9, -0.2), 'Space Station': (0.8, -0.6), 'The Moon': (-0.3, 0.3)}
    for name, pt in PASS.items():
        m.whoosh(pt - 0.35, 0.8, 0.22, *pans[name])
    m.silence(T_STOP - 0.32, T_STOP)
    m.stop_signature(T_STOP)
    m.bed(T_STOP + 0.4, DUR, cutoff=lambda tt: 0.02, vol=lambda tt: 0.012, seed=5)
    m.bell(T_TWIST, 659.25, 0.2, -0.3); m.bell(T_TWIST + 0.1, 987.77, 0.2, 0.3)


if __name__ == '__main__':
    main(render_frame, DUR, music, sys.argv)
