"""STYLE v3 PROTOTYPE - FACT 001 Fold paper 42 times.
Channel signature: answer chips on frame 1, fuse bar, chips struck as the sim passes them, ritardando,
silence, white STOP flash + signature sound, twist 1.5 s after reveal, 10.5 s seamless loop.
Fact world: a paper stack climbing on a log altitude scale; sky turns to space; the Moon approaches.
0.1 mm x 2^42 = 439,805 km > 384,400 km (Moon, mean distance). Landmarks: Burj Khalifa 828 m (2^23 -> 839 m),
Everest 8,849 m (2^27 -> 13.4 km), ISS ~400-420 km (2^32 -> 429 km). Real record: 12 folds (B. Gallivan 2002)."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from lib import *
from lib2 import *

DUR, T_STOP, T_TWIST = 10.5, 7.3, 8.8
N0, NMAX = 3.0, 42
assert round(0.1e-6 * 2 ** 42) == 439805 and 0.1e-6 * 2 ** 41 < 384400 < 0.1e-6 * 2 ** 42


def nfold(t):
    if t >= T_STOP:
        return float(NMAX)
    x = t / T_STOP
    return N0 + (NMAX - N0) * (1 - (1 - x) ** 1.7)      # fast start, slows into the stop


def alt(n):            # metres
    return 0.1e-3 * 2 ** n


MX, MY, PX = 150, 1000, 330            # stack top marker; px per decade
LANDS = [(1.7, 'A person', None), (828, 'Burj Khalifa', None), (8849, 'Everest', 'A'),
         (408000, 'Space Station', 'B'), (384400000, 'The Moon', 'C')]
CHIPS = [('A', 'Everest'), ('B', 'Space Station'), ('C', 'The Moon')]


def chip_state(t):
    n = nfold(t)
    h = alt(n)
    st = {}
    for a, lab, c in LANDS:
        if c:
            st[c] = h >= a
    return st


def pass_time(a):
    # first t where alt(nfold(t)) >= a
    lo, hi = 0.0, T_STOP
    for _ in range(40):
        m = (lo + hi) / 2
        if alt(nfold(m)) >= a: hi = m
        else: lo = m
    return hi


PASS = {lab: pass_time(a) for a, lab, c in LANDS if alt(N0) < a}


def fmt(m):
    if m < 0.01: return f'{m * 1000:.1f} mm'
    if m < 1: return f'{m * 100:.0f} cm'
    if m < 1000: return f'{m:,.0f} m'
    if m < 100000: return f'{m / 1000:.1f} km'
    return f'{m / 1000:,.0f} km'


def lerp(a, b, x):
    return tuple(int(a[i] + (b[i] - a[i]) * x) for i in range(3))


def sky(lh):
    """sky colour (top, bottom) for log10 altitude in metres."""
    stops = [(-4, (30, 80, 160), (70, 130, 200)), (2.5, (25, 65, 150), (60, 115, 190)),
             (4, (20, 45, 120), (50, 100, 190)), (5, (6, 8, 30), (14, 24, 70)), (6, (3, 4, 12), (6, 8, 22))]
    for (a, t0, b0), (b, t1, b1) in zip(stops, stops[1:]):
        if lh <= b:
            x = clamp((lh - a) / (b - a))
            return lerp(t0, t1, x), lerp(b0, b1, x)
    return stops[-1][1], stops[-1][2]


rng = np.random.default_rng(2)
STARS = [(rng.uniform(0, W), rng.uniform(0, 1440), rng.uniform(1, 3.2)) for _ in range(160)]
YY = np.linspace(0, 1, H)[:, None, None]
TAG, _ = text_layer([('FACT 001', SEMI, 30, MUTED)], 140)
Q, _ = big_text([('Fold paper 42 times.', XB, 88, WHITE), ('How thick?', XB, 88, WHITE)], 190)
ANS, _ = big_text([('Past the Moon', BLACK, 116, GOLD), ('0.1 mm, doubled 42 times', BOLD, 46, WHITE)], 190)
TWIST, _ = big_text([('Real-world record:', BOLD, 50, WHITE), ('12 folds', BLACK, 96, GOLD)], 1180)


def draw_chips(img, t):
    d = ImageDraw.Draw(img)
    st = chip_state(t)
    y0, h, gap = 455, 78, 18
    widths = []
    for k, lab in CHIPS:
        widths.append(int(d.textlength(lab, font=font(BOLD, 34))) + 110)
    x = (W - sum(widths) - gap * 2) // 2
    for (k, lab), w in zip(CHIPS, widths):
        passed = st.get(k, False) and k != 'C'
        won = t >= T_STOP and k == 'C'
        pt = PASS.get(dict((c, l) for a, l, c in LANDS if c)[k], 99)
        pop = math.exp(-max(0, t - pt) * 6) if t >= pt else 0
        fill = (255, 204, 51, 255) if won else ((40, 30, 45, 200) if passed else (8, 12, 30, 150))
        out = (255, 204, 51, 255) if won else ((255, 80, 90, 255) if passed else (255, 255, 255, 140))
        grow = int(8 * pop)
        d.rounded_rectangle([x - grow, y0 - grow, x + w + grow, y0 + h + grow], radius=39, fill=fill, outline=out, width=3)
        tc = (20, 16, 10) if won else ((150, 150, 160) if passed else WHITE)
        d.ellipse([x + 14, y0 + 14, x + 64, y0 + 64], fill=(0, 0, 0, 90) if not won else (20, 16, 10, 255))
        d.text((x + 39, y0 + 40), k, font=font(BLACK, 30), fill=GOLD if won else WHITE, anchor='mm')
        d.text((x + 80, y0 + 40), lab, font=font(BOLD, 34), fill=tc, anchor='lm')
        if passed:
            d.line([x + 76, y0 + 41, x + w - 18, y0 + 41], fill=(255, 80, 90, 255), width=5)
        x += w + gap


def frame_core(t):
    n = nfold(t)
    h = alt(n)
    lh = math.log10(h)
    top, bot = sky(lh)
    arr = (np.array(top) * (1 - YY) + np.array(bot) * YY).astype(np.float32)
    arr = np.broadcast_to(arr, (H, W, 3)).copy()
    arr[1440:] *= np.linspace(1, 0.15, H - 1440)[:, None, None]
    glow = Image.new('RGB', (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    star_a = clamp((lh - 4.3) / 1.0)
    # moon (drawn on the glow-free layer later); landmarks
    marks = []
    for a, lab, c in LANDS:
        y = MY - (math.log10(a) - lh) * PX
        marks.append((a, lab, c, y))
    # paper stack column with moving fold lines
    col_top = MY
    gd.rectangle([MX - 34, col_top, MX + 34, 1440], fill=(150, 150, 160))
    img = to_img(arr)
    d = ImageDraw.Draw(img)
    if star_a > 0:
        for sx, sy, sr in STARS:
            v = int(255 * star_a * (0.5 + 0.5 * math.sin(sx + t * 2)))
            d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(v, v, v))
    for a, lab, c, y in marks:
        if lab == 'The Moon':
            r = 120
            cy, mxc = y - r - 10, 470
            if -r < cy < 1300 + r:
                d.ellipse([mxc - r, cy - r, mxc + r, cy + r], fill=(214, 212, 222))
                for cx_, cy_, cr in ((-0.35, -0.2, 0.22), (0.3, 0.25, 0.16), (0.1, -0.45, 0.1), (-0.1, 0.45, 0.12)):
                    d.ellipse([mxc + (cx_ - cr) * r, cy + (cy_ - cr) * r, mxc + (cx_ + cr) * r,
                               cy + (cy_ + cr) * r], fill=(172, 170, 184))
        if 560 < y < 1250:
            hit = lab in PASS and 0 <= t - PASS[lab] < 0.5
            col = (255, 230, 120) if hit else (255, 255, 255)
            for xx in range(MX + 50, 1040, 28):
                d.line([xx, y, xx + 14, y], fill=col, width=3)
            d.text((1040, y - 14), f'{lab}  {fmt(a)}', font=font(BOLD, 36), fill=col, anchor='rb')
    # stack: bright paper with scrolling fold stripes
    d.rectangle([MX - 34, MY, MX + 34, 1440], fill=(246, 244, 236))
    off = (n * 40) % 20
    for yy in np.arange(MY + off, 1440, 20):
        d.line([MX - 34, yy, MX + 34, yy], fill=(200, 196, 186), width=2)
    d.rectangle([MX - 40, MY - 6, MX + 40, MY + 2], fill=GOLD)
    # counter at stack top
    d.text((1040, 1420), fmt(alt(int(n))) if t < T_STOP else '439,805 km', font=font(BLACK, 104),
           fill=GOLD if t >= T_STOP else WHITE, anchor='rb')
    d.text((1040, 1290), f'FOLD {int(n)} OF 42', font=font(SEMI, 36), fill=(230, 235, 245), anchor='rb')
    # fuse
    fx = 90 + 900 * clamp(1 - t / T_STOP)
    d.rounded_rectangle([90, 410, 990, 418], radius=4, fill=(255, 255, 255, 60))
    if t < T_STOP:
        d.rounded_rectangle([90, 410, fx, 418], radius=4, fill=GOLD)
        sp = 10 + 4 * math.sin(t * 40)
        d.ellipse([fx - sp, 414 - sp, fx + sp, 414 + sp], fill=(255, 240, 200))
    img.alpha_composite(TAG)
    draw_chips(img, t)
    comp(img, Q, 1 - ramp(t, T_STOP, T_STOP + 0.05))
    comp(img, ANS, ramp(t, T_STOP, T_STOP + 0.05))
    if t >= T_TWIST:
        d2 = ImageDraw.Draw(img)
        a = ease_out(ramp(t, T_TWIST, T_TWIST + 0.3))
        y = 1040 + 20 * (1 - a)
        pl = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        pd = ImageDraw.Draw(pl)
        pd.rounded_rectangle([250, y - 20, 1010, y + 190], radius=36, fill=(10, 10, 20, 250), outline=GOLD, width=3)
        comp(img, pl, a)
        tw, _ = big_text([('Real-world record:', BOLD, 50, WHITE), ('12 folds', BLACK, 96, GOLD)], int(y))
        tw = tw.transform(tw.size, Image.AFFINE, (1, 0, -90, 0, 1, 0))
        comp(img, tw, a)
    # STOP flash
    if T_STOP <= t < T_STOP + 0.4:
        fl = Image.new('RGBA', (W, H), (255, 255, 255, int(255 * (1 - (t - T_STOP) / 0.4) ** 2)))
        img.alpha_composite(fl)
    return img


F0 = None


def render_frame(t):
    global F0
    img = frame_core(t)
    if t > DUR - 0.35:
        if F0 is None:
            F0 = frame_core(0.0)
        img = Image.blend(img, F0, ease_io(ramp(t, DUR - 0.35, DUR - 1 / FPS)))
    return img


def stop_sig(m, t):
    """Channel sonic signature: three fast rising notes, boom, bright chord."""
    for k, f in enumerate((783.99, 1046.5, 1318.5)):
        m.pluck(t + k * 0.07, f, vol=0.32, bright=1.3)
    m.boom(t, 0.9)
    m.chord(t + 0.14, [523.25, 659.25, 783.99, 1046.5], 0.3, 2.5)


def music(m):
    # engine drone rising with altitude
    n = int(SR * T_STOP)
    x = np.arange(n) / SR
    ff = 70 + 9 * np.array([nfold(v) for v in x[::441]]).repeat(441)[:n]
    ph = 2 * np.pi * np.cumsum(ff) / SR
    drone = (np.sin(ph) + 0.4 * np.sin(2 * ph) + 0.2 * np.sin(3.01 * ph)) * 0.06 * np.clip(x / 0.05, 0, 1)
    drone *= np.clip((T_STOP - 0.35 - x) / 0.05, 0, 1)          # silence before the stop
    m._add(0, drone.astype(np.float32))
    # one pluck per fold, pitch climbs; folds slow down at the end on their own
    k = int(N0) + 1
    for i in range(1, int(T_STOP * 300)):
        t = i / 300
        if t > T_STOP - 0.35:
            break
        if nfold(t) >= k:
            m.pluck(t, note_freq(min(3 + (k - 3) // 2 + (k % 2) * 2, 16)), vol=0.2)
            k += 1
    for lab, pt in PASS.items():
        if pt < T_STOP - 0.35:
            m.mallet(pt, 1567.98, vol=0.22)
    for hb in (T_STOP - 1.5, T_STOP - 1.0, T_STOP - 0.62):     # heartbeat
        m.boom(hb, 0.35, 0.3)
    stop_sig(m, T_STOP)
    m.pluck(T_TWIST, 659.25, 0.22); m.pluck(T_TWIST + 0.09, 987.77, 0.22)


if __name__ == '__main__':
    import os
    out = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2] == '--preview':
        for ts in sys.argv[3].split(','):
            render_frame(float(ts)).convert('RGB').save(f'{out}_{float(ts):05.2f}.png')
    else:
        render(render_frame, DUR, out, music, os.path.dirname(out))
