"""PROPOSAL C - How many Earths fill the Sun's volume? (remake of fact 016) in 'cinematic swarm' style.
Glowing Sun with corona; Earth-dots stream in from all edges and pack the disc; counter accelerates.
1 dot = 1,000 Earths, 1,304 dots. NASA Sun Fact Sheet ratio 1,304,000."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from lib import *
from lib2 import *

DUR, T1 = 14.0, 9.0
RATIO = 1304000
N = RATIO // 1000
P, CX, CY = 17, 540, 905
g = [(ix * P + P / 2, iy * P + P / 2) for ix in range(-30, 30) for iy in range(-30, 30)]
g.sort(key=lambda p: p[0] ** 2 + p[1] ** 2)
CELLS = np.array(g[:N])
DISC_R = math.sqrt(CELLS[-1][0] ** 2 + CELLS[-1][1] ** 2) + 8
rng = np.random.default_rng(4)
ANG = rng.uniform(0, 2 * np.pi, N)
START = np.stack([CX + 1100 * np.cos(ANG), CY + 1100 * np.sin(ANG)], 1)
# fill from the centre outward; arrival times follow an accelerating curve
ARR = np.array([T1 * (k / N) ** (1 / 1.6) for k in range(N)])
FLY = 0.9

BG = gradient_bg(top=(30, 8, 10), bottom=(4, 2, 6), glow_at=(CX, CY), glow_col=(90, 30, 0), glow_r=900)
HOOK, _ = big_text([("How many Earths", XB, 92, WHITE), ("fill the Sun's volume?", XB, 92, WHITE),
                    ('Guess before it stops.', SEMI, 44, GOLD)], 200)
REVEAL, _ = big_text([('1.3 million', BLACK, 136, GOLD), ('Earths, by volume', XB, 64, WHITE),
                      ('Source: NASA Sun Fact Sheet', MED, 32, MUTED)], 200)
TAG, _ = text_layer([('FACT 016', SEMI, 30, MUTED)], 145)


def frame_core(t):
    glow = Image.new('RGB', (W, H), (0, 0, 0))
    d = ImageDraw.Draw(glow)
    # sun body + corona (pulses at reveal)
    pr = 1 + 0.05 * math.exp(-max(0, t - T1) * 3) * (t >= T1)
    for k, (rr, c) in enumerate(((DISC_R * 1.15, (55, 16, 0)), (DISC_R * 1.06, (100, 34, 0)), (DISC_R, (110, 40, 4)))):
        r = rr * pr * (1 + 0.01 * math.sin(t * 3 + k))
        d.ellipse([CX - r, CY - r, CX + r, CY + r], fill=c)
    # Earth dots
    e = np.clip((t - (ARR - FLY)) / FLY, 0, 1)
    ee = 1 - (1 - e) ** 3
    pos = START * (1 - ee[:, None]) + (CELLS + [CX, CY]) * ee[:, None]
    landed = t >= ARR
    arr = bloom(BG + np.asarray(glow, np.float32), 1.0)
    img = to_img(arr)
    dd = ImageDraw.Draw(img)
    for i in np.where((e > 0) & ~landed)[0]:
        x, y = pos[i]
        dd.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(150, 215, 255))
    for i in np.where(landed)[0]:
        x, y = pos[i]
        f = math.exp(-(t - ARR[i]) * 5)
        c = (int(40 + 200 * f), int(130 + 120 * f), 255)
        dd.ellipse([x - 6, y - 6, x + 6, y + 6], fill=c)
    n = int(landed.sum())
    shown = RATIO if t >= T1 else n * 1000
    dd.text((CX, 1342), f'{shown:,}', font=font(BLACK, 96), fill=GOLD if t >= T1 else WHITE, anchor='mm')
    dd.text((CX, 1420), 'Earths  ·  1 dot = 1,000', font=font(MED, 32), fill=MUTED, anchor='mm')
    img.alpha_composite(TAG)
    comp(img, HOOK, 1 - ramp(t, T1 - 0.1, T1 + 0.1))
    comp(img, REVEAL, ease_out(ramp(t, T1 + 0.05, T1 + 0.35)))
    return img


F0 = None


def render_frame(t):
    global F0
    img = frame_core(t)
    if t > DUR - 0.6:
        if F0 is None:
            F0 = frame_core(0.0)
        img = Image.blend(img, F0, ease_io(ramp(t, DUR - 0.6, DUR - 0.05)))
    return img


def music(m):
    m.pad(0, T1, [98.0, 146.83, 196.0], vol=0.06)
    # arrivals as a rising shimmer: one note per 1/40 of the dots
    step = N // 40
    for k in range(0, N, step):
        m.pluck(ARR[k], note_freq(2 + (k // step) % 5 + (k // step) // 8 * 2), vol=0.22)
    m.riser(T1 - 1.8, 1.8, 0.10)
    m.boom(T1, 0.9)
    m.chord(T1, [196.0, 246.94, 293.66, 392.0, 493.88], 0.35, 4.0)


if __name__ == '__main__':
    import os
    out = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2] == '--preview':
        for ts in sys.argv[3].split(','):
            render_frame(float(ts)).convert('RGB').save(f'{out}_{float(ts):05.2f}.png')
    else:
        render(render_frame, DUR, out, music, os.path.dirname(out))
