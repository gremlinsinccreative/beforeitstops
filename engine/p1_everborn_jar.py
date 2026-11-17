"""PROPOSAL A - Everyone ever born: how many are alive? (remake of fact 006) in 'physics pour' style.
1 ball = 1 billion people. 117 balls pour into a glass jar with real collisions. The last 8 to fall
(the most recently born) glow gold: alive today. PRB (2022): ~117 billion ever born, ~8 billion alive.
8 / 117 = 6.8% -> 'about 7 in 100'."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from lib import *
from lib2 import *

DUR, T1 = 14.0, 9.0
N, ALIVE = 117, 8
assert round(100 * ALIVE / N) == 7
R = 24
JX0, JX1, JY0, JY1 = 250, 830, 790, 1285       # jar inner box
GRAV = 2600.0
SPAWN = [-0.45 + i * 7.6 / N for i in range(N)]

# ---------- precompute physics ----------
rng = np.random.default_rng(11)
SUB = 10
P = np.zeros((N, 2)); V = np.zeros((N, 2)); act = np.zeros(N, bool)
PRE = 15
FR = int(DUR * FPS) + 1 + PRE
POS = np.zeros((FR, N, 2)); ACT = np.zeros((FR, N), bool)
LAND = [None] * N
dt = 1 / FPS / SUB
for f in range(FR):
    for s in range(SUB):
        t = (f * SUB + s) * dt - PRE / FPS
        for i in range(N):
            if not act[i] and t >= SPAWN[i] and t < T1:
                act[i] = True
                P[i] = [540 + rng.uniform(-70, 70), 560]
                V[i] = [rng.uniform(-120, 120), 900]
        idx = np.where(act)[0]
        if len(idx) == 0:
            continue
        prev = P[idx].copy()
        V[idx, 1] += GRAV * dt
        P[idx] += V[idx] * dt
        for _ in range(3):
            q = P[idx]
            dif = q[:, None, :] - q[None, :, :]
            dist = np.sqrt((dif ** 2).sum(-1)) + np.eye(len(idx)) * 1e9
            ov = np.clip(2 * R - dist, 0, None)
            push = (dif / dist[..., None]) * (ov[..., None] * 0.5)
            q = q + push.sum(1) * 0.9
            q[:, 0] = np.clip(q[:, 0], JX0 + R, JX1 - R)
            q[:, 1] = np.minimum(q[:, 1], JY1 - R)
            P[idx] = q
        newv = (P[idx] - prev) / dt
        # landing detection: sudden vertical stop
        for k, i in enumerate(idx):
            if LAND[i] is None and V[i, 1] > 400 and newv[k, 1] < V[i, 1] * 0.4:
                LAND[i] = t
        V[idx] = newv * 0.995
    POS[f] = P; ACT[f] = act


def sprite(base, r=R, hi=(255, 255, 255)):
    s = 4 * r
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    yy, xx = np.mgrid[0:s, 0:s] / 2.0
    dx, dy = xx - r, yy - r
    d = np.sqrt(dx ** 2 + dy ** 2)
    inside = np.clip((r - d) * 1.5, 0, 1)
    lx, ly = -0.45 * r, -0.5 * r
    spec = np.clip(1 - np.sqrt((dx - lx) ** 2 + (dy - ly) ** 2) / (0.55 * r), 0, 1) ** 2
    shade = 0.55 + 0.45 * np.clip(1 - (dx * 0.3 + dy * 0.7 + r * 0.2) / (1.6 * r), 0, 1)
    rgb = np.array(base)[None, None, :] * shade[..., None]
    rgb = rgb * (1 - spec[..., None] * 0.8) + np.array(hi)[None, None, :] * spec[..., None] * 0.8
    arr = np.dstack([np.clip(rgb, 0, 255), inside * 255]).astype(np.uint8)
    return Image.fromarray(arr, 'RGBA').resize((2 * r, 2 * r), Image.LANCZOS)


SP_DEAD = sprite((120, 135, 170))
SP_DIM = sprite((60, 66, 88))
SP_GOLD = sprite((255, 196, 40), hi=(255, 250, 220))

BG = gradient_bg(top=(10, 16, 40), bottom=(3, 4, 12), glow_at=(540, 1000), glow_col=(20, 40, 80), glow_r=800)
HOOK, _ = big_text([('Of everyone ever born,', XB, 84, WHITE), ('how many are alive?', XB, 84, WHITE),
                    ('Guess before it stops.', SEMI, 44, GOLD)], 230)
REVEAL, _ = big_text([('About 7 in 100', BLACK, 124, GOLD), ('8 billion alive of 117 billion born', BOLD, 46, WHITE),
                      ('Source: Population Reference Bureau (2022)', MED, 32, MUTED)], 230)
TAG, _ = text_layer([('FACT 006', SEMI, 30, MUTED)], 170)


def frame_core(t):
    f = min(int(round(t * FPS)) + PRE, FR - 1)
    pos, act = POS[f], ACT[f]
    rev = ease_out(ramp(t, T1, T1 + 0.6))
    glow = Image.new('RGB', (W, H), (0, 0, 0))
    d = ImageDraw.Draw(glow)
    # glass jar outline
    gc = (40, 120, 200)
    d.rounded_rectangle([JX0 - 14, JY0 - 60, JX1 + 14, JY1 + 14], radius=46, outline=gc, width=6)
    d.rectangle([JX0 - 30, JY0 - 75, JX1 + 30, JY0 - 45], fill=(0, 0, 0))
    pulse = 0.75 + 0.25 * math.sin(t * 6)
    for i in range(N - ALIVE, N):
        if act[i]:
            x, y = pos[i]
            g = int(180 * (0.6 + rev * 0.6 * pulse))
            d.ellipse([x - R - 6, y - R - 6, x + R + 6, y + R + 6], fill=(g, int(g * 0.7), 0))
    arr = bloom(BG + np.asarray(glow, np.float32) * 0.8, 1.0)
    img = to_img(arr)
    for i in range(N):
        if not act[i]:
            continue
        x, y = pos[i]
        sp = SP_GOLD if i >= N - ALIVE else (SP_DEAD if rev < 0.5 else SP_DIM)
        if i < N - ALIVE and 0 < rev < 1:
            sp = Image.blend(SP_DEAD, SP_DIM, rev)
        img.alpha_composite(sp, (int(x - R), int(y - R)))
    dd = ImageDraw.Draw(img)
    cnt = int(act.sum())
    if t < T1:
        dd.text((540, 1345), f'{cnt} billion people', font=font(BLACK, 64), fill=WHITE, anchor='mm')
    else:
        dd.text((540, 1345), '8 alive  ·  109 gone', font=font(BLACK, 64), fill=GOLD, anchor='mm')
    dd.text((540, 1405), '1 ball = 1 billion people', font=font(MED, 32), fill=MUTED, anchor='mm')
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
    m.pad(0, T1, [110.0, 164.81, 220.0], vol=0.05)
    last = -1
    lands = sorted((LAND[i], i) for i in range(N) if LAND[i] is not None)
    for k, (lt, i) in enumerate(lands):
        if lt - last < 0.045:
            continue
        last = lt
        if i >= N - ALIVE:
            m.pluck(lt, note_freq(10 + (i - (N - ALIVE)) % 5), vol=0.32, bright=1.4)
        else:
            m.mallet(lt, note_freq(3 + (k * 2) % 9), vol=0.18)
    m.riser(T1 - 1.5, 1.5, 0.08)
    m.boom(T1, 0.8)
    m.chord(T1, [220.0, 277.18, 329.63, 440.0, 554.37], 0.35, 4.0)


if __name__ == '__main__':
    import os
    out = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2] == '--preview':
        for ts in sys.argv[3].split(','):
            render_frame(float(ts)).convert('RGB').save(f'{out}_{float(ts):05.2f}.png')
    else:
        render(render_frame, DUR, out, music, os.path.dirname(out))
