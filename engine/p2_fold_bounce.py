"""PROPOSAL B - Fold paper 42 times (remake of fact 001) in the 'bounce ring' style.
Every bounce = one fold. Ball speeds up, note climbs, thickness doubles. Ring breaks at fold 42.
0.1 mm x 2^42 = 439,805 km > Moon 384,400 km. Landmarks: 2^23 x 0.1 mm = 839 m > Burj Khalifa 828 m;
2^27 = 13.4 km > Everest 8,849 m; 2^32 = 429 km > ISS orbit ~400-420 km."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from lib import *
from lib2 import *

DUR, T1 = 14.0, 9.0
CX, CY, R, BR = 540, 905, 315, 18
assert round(0.1e-6 * 2 ** 42) == 439805 and 0.1e-3 * 2 ** 23 > 828 and 0.1e-6 * 2 ** 27 > 8.849

LANDMARKS = {23: 'Taller than Burj Khalifa', 27: 'Higher than Everest', 32: 'Past the Space Station',
             42: 'Past the Moon'}


def simulate(k, s0=520.0, dt=1 / 1200):
    p = np.array([0.0, 0.0]); a = math.radians(-58); v = np.array([math.cos(a), math.sin(a)]) * s0
    t, hits, path = 0.0, [], []
    while len(hits) < 42 and t < 30:
        p = p + v * dt; t += dt
        d = np.linalg.norm(p)
        if d >= R - BR:
            n = p / d
            p = n * (R - BR)
            v = v - 2 * np.dot(v, n) * n
            # tiny deterministic twist so paths don't repeat
            ang = 0.09 * math.sin(len(hits) * 1.7)
            c, s = math.cos(ang), math.sin(ang)
            v = np.array([c * v[0] - s * v[1], s * v[0] + c * v[1]]) * k
            hits.append((t, p.copy()))
        path.append((t, p.copy()))
    return hits, path


lo, hi = 1.0, 1.2
for _ in range(40):
    k = (lo + hi) / 2
    hits, _p = simulate(k)
    if len(hits) < 42 or hits[-1][0] > T1:
        lo = k
    else:
        hi = k
HITS, PATH = simulate(hi)
assert len(HITS) == 42 and abs(HITS[-1][0] - T1) < 0.05, HITS[-1][0]
HT = np.array([h[0] for h in HITS])
PT = np.array([q[0] for q in PATH]); PP = np.array([q[1] for q in PATH])
STOP = HITS[-1][1]


def pos(t):
    if t >= HT[-1]:
        return STOP
    i = min(np.searchsorted(PT, t), len(PT) - 1)
    return PP[i]


def folds(t):
    return int(np.searchsorted(HT, t, side='right'))


def thick(n):
    m = 0.1e-3 * 2 ** n
    if m < 0.01: return f'{m * 1000:.1f} mm'
    if m < 1: return f'{m * 100:.1f} cm'
    if m < 1000: return f'{m:,.0f} m'
    return f'{m / 1000:,.0f} km' if m >= 10000 else f'{m / 1000:.1f} km'


BG = gradient_bg(top=(26, 8, 48), bottom=(3, 4, 14), glow_at=(CX, CY), glow_col=(50, 20, 90), glow_r=700)
HOOK, _ = big_text([('Fold paper 42 times.', XB, 92, WHITE), ('How thick is it?', XB, 92, WHITE),
                    ('Guess before it stops.', SEMI, 44, GOLD)], 230)
REVEAL, _ = big_text([('Past the Moon', BLACK, 120, GOLD), ('0.1 mm, doubled 42 times', XB, 60, WHITE),
                      ('Moon: 384,400 km away', MED, 38, MUTED)], 230)
TAG, _ = text_layer([('FACT 001', SEMI, 30, MUTED)], 170)
rng = np.random.default_rng(5)
SHARDS = [(a, rng.uniform(400, 1400), rng.uniform(-6, 6)) for a in np.linspace(0, 2 * np.pi, 90, endpoint=False)]


def frame_core(t):
    glow = Image.new('RGB', (W, H), (0, 0, 0))
    d = ImageDraw.Draw(glow)
    n = folds(t)
    hue = 0.75 - 0.75 * n / 42
    col = hsv(hue, 0.8, 1.0)
    since = t - HT[n - 1] if n > 0 else 9
    broken = t >= T1
    if not broken:
        flash = math.exp(-since * 8)
        rc = tuple(int(c * (0.45 + 0.55 * flash)) for c in col)
        d.ellipse([CX - R, CY - R, CX + R, CY + R], outline=rc, width=7)
        if n > 0:  # ripple from last hit
            hx, hy = HITS[n - 1][1]
            rr = 30 + since * 500
            a = max(0.0, 1 - since * 2.5)
            if a > 0:
                d.ellipse([CX + hx - rr, CY + hy - rr, CX + hx + rr, CY + hy + rr],
                          outline=tuple(int(c * a) for c in col), width=4)
    else:
        e = t - T1
        for a0, sp, rot in SHARDS:
            rr = R + sp * e ** 0.7
            a1 = a0 + 0.06
            fade = max(0.0, 1 - e / 3.5)
            c = tuple(int(v * fade) for v in col)
            x0, y0 = CX + rr * math.cos(a0 + rot * e * 0.05), CY + rr * math.sin(a0 + rot * e * 0.05)
            x1, y1 = CX + rr * math.cos(a1 + rot * e * 0.05), CY + rr * math.sin(a1 + rot * e * 0.05)
            d.line([x0, y0, x1, y1], fill=c, width=7)
    # trail
    tr = [pos(t - j / 240) for j in range(0, 60)]
    for j in range(len(tr) - 1, 0, -1):
        f = 1 - j / 60
        c = tuple(int(v * f) for v in col)
        d.line([CX + tr[j][0], CY + tr[j][1], CX + tr[j - 1][0], CY + tr[j - 1][1]], fill=c, width=int(4 + 26 * f))
    p = pos(t)
    br = BR
    if broken:
        e = ease_out(ramp(t, T1, T1 + 0.7))
        p = (STOP[0] * (1 - e), STOP[1] * (1 - e))
        br = BR + (150 - BR) * e
        d.ellipse([CX + p[0] - br, CY + p[1] - br, CX + p[0] + br, CY + p[1] + br], fill=(70, 60, 110))
        MOON[:] = [p[0], p[1], br]
    else:
        d.ellipse([CX + p[0] - br, CY + p[1] - br, CX + p[0] + br, CY + p[1] + br], fill=(255, 255, 255))
    arr = BG + np.asarray(glow, np.float32)
    arr = bloom(arr, 1.1)
    img = to_img(arr)
    dd = ImageDraw.Draw(img)
    if broken:
        mx, my, mr = MOON
        dd.ellipse([CX + mx - mr, CY + my - mr, CX + mx + mr, CY + my + mr], fill=(214, 212, 222))
        for cx_, cy_, cr in ((-0.35, -0.2, 0.22), (0.3, 0.25, 0.16), (0.1, -0.45, 0.1), (-0.1, 0.45, 0.12), (0.45, -0.15, 0.08)):
            dd.ellipse([CX + mx + (cx_ - cr) * mr, CY + my + (cy_ - cr) * mr,
                        CX + mx + (cx_ + cr) * mr, CY + my + (cy_ + cr) * mr], fill=(172, 170, 184))
    # counter
    if not broken:
        dd.text((CX, CY + R + 52), f'FOLD {n} OF 42', font=font(SEMI, 36), fill=MUTED, anchor='mm')
        dd.text((CX, CY + R + 125), thick(n), font=font(BLACK, 100), fill=WHITE, anchor='mm')
        lm = [k for k in LANDMARKS if k <= n and k < 42]
        if lm:
            k = max(lm); age = t - HT[k - 1]
            if age < 1.6:
                dd.text((CX, CY), LANDMARKS[k], font=font(BOLD, 50), fill=col, anchor='mm')
    if broken:
        dd.text((CX, CY + R + 125), '439,805 km', font=font(BLACK, 100), fill=GOLD, anchor='mm')
    img.alpha_composite(TAG)
    if t < T1 + 0.1:
        comp(img, HOOK, 1 - ramp(t, T1 - 0.1, T1 + 0.1))
    comp(img, REVEAL, ease_out(ramp(t, T1 + 0.05, T1 + 0.35)))
    return img


F0 = None
MOON = [0, 0, 0]


def render_frame(t):
    global F0
    img = frame_core(t)
    if t > DUR - 0.6:  # loop: crossfade into frame 0
        if F0 is None:
            F0 = frame_core(0.0)
        img = Image.blend(img, F0, ease_io(ramp(t, DUR - 0.6, DUR - 0.05)))
    return img


def music(m):
    m.pad(0, T1, [130.81, 196.0, 261.63], vol=0.05)
    for i, (ht, _) in enumerate(HITS[:-1]):
        idx = (i % 6) + min(i // 6, 4) * 2 + 3
        m.pluck(ht, note_freq(idx), vol=0.28)
        if (i + 1) in LANDMARKS:
            m.mallet(ht, note_freq(idx + 5), vol=0.25)
    m.riser(T1 - 1.6, 1.6, 0.10)
    m.boom(T1, 0.9)
    m.chord(T1, [261.63, 329.63, 392.0, 523.25, 659.25], 0.35, 4.0)


if __name__ == '__main__':
    import os
    out = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2] == '--preview':
        for ts in sys.argv[3].split(','):
            render_frame(float(ts)).convert('RGB').save(f'{out}_{float(ts):05.2f}.png')
    else:
        render(render_frame, DUR, out, music, os.path.dirname(out))
