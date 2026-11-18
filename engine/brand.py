"""Before It Stops - style v3.1 brand layer.
One focal point at a time: hook (big question + big chips, 0-1.2 s) -> compact header while the sim runs ->
answer at the STOP -> one twist card -> seamless loop. Stereo sound with a world bed and the STOP signature."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.io import wavfile
from scipy.signal import fftconvolve, lfilter
from lib import *
from lib2 import big_text, note_freq, render as _render_unused

HOOK_END = 1.15          # hook -> compact header
RED = (255, 84, 96)


# ---------------- chips ----------------
def chip_row(d, chips, states, y, size='big', pops=None):
    """chips: [(letter, label)], states: {'A': 'idle'|'out'|'win'} ."""
    fs, h, lf = (38, 88, 34) if size == 'big' else (27, 58, 24)
    gap = 18 if size == 'big' else 12
    widths = [int(d.textlength(lab, font=font(BOLD, fs))) + (h + 34) for _, lab in chips]
    x = (W - sum(widths) - gap * (len(chips) - 1)) // 2
    for (k, lab), w in zip(chips, widths):
        st = states.get(k, 'idle')
        p = (pops or {}).get(k, 0.0)
        g = int(10 * p)
        if st == 'win':
            fill, out, tc = GOLD + (255,), GOLD + (255,), (18, 14, 8)
        elif st == 'out':
            fill, out, tc = (30, 20, 30, 170), RED + (230,), (150, 150, 162)
        else:
            fill, out, tc = (8, 12, 30, 170), (255, 255, 255, 170), WHITE
        d.rounded_rectangle([x - g, y - g, x + w + g, y + h + g], radius=h // 2, fill=fill, outline=out, width=3)
        r = h * 0.32
        cx, cy = x + h * 0.5, y + h / 2
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(18, 14, 8, 255) if st == 'win' else (0, 0, 0, 110))
        d.text((cx, cy + 1), k, font=font(BLACK, lf), fill=GOLD if st == 'win' else WHITE, anchor='mm')
        d.text((x + h * 0.95, cy + 1), lab, font=font(BOLD, fs), fill=tc, anchor='lm')
        if st == 'out':
            d.line([x + h * 0.9, cy + 1, x + w - h * 0.3, cy + 1], fill=RED, width=4 if size == 'big' else 3)
        x += w + gap


HEADER_SHADE = Image.new('RGBA', (W, H), (0, 0, 0, 0))
_hs = np.zeros((H, W, 4), np.uint8)
_hs[:, :, 3] = (np.clip(1 - np.arange(H) / 470, 0, 1) ** 1.4 * 190).astype(np.uint8)[:, None]
_hs[:, :, :3] = (4, 5, 14)
HEADER_SHADE = Image.fromarray(_hs, 'RGBA')


class Brand:
    def __init__(self, num, q_lines, chips, answer_lines, twist_lines, t_stop, t_twist, dur=10.5,
                 sub='Guess before it stops.', cta=None, q_size=96):
        self.num, self.chips, self.t_stop, self.t_twist, self.dur = num, chips, t_stop, t_twist, dur
        self.cta = cta
        self.hook, _ = big_text([(f'FACT {num:03d}', SEMI, 30, MUTED)] + [(s, XB, q_size, WHITE) for s in q_lines]
                                + [(sub, SEMI, 42, GOLD)], 250)
        self.q_small = ' '.join(q_lines)
        self.answer, _ = big_text(answer_lines, 150)
        self.twist_lines = twist_lines

    def overlay(self, img, t, states, pops=None):
        """Draw all brand text for time t on img (RGBA)."""
        img.alpha_composite(HEADER_SHADE)
        a = ease_io(ramp(t, HOOK_END, HOOK_END + 0.3))
        if t < self.t_stop:
            if a < 1:   # big hook
                lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
                lay.alpha_composite(self.hook)
                chip_row(ImageDraw.Draw(lay), self.chips, states, 640, 'big', pops)
                comp(img, lay, 1 - a)
            if a > 0:   # compact header + fuse
                lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
                d = ImageDraw.Draw(lay)
                d.text((W / 2, 150), f'FACT {self.num:03d}', font=font(SEMI, 26), fill=MUTED, anchor='mm')
                d.text((W / 2, 200), self.q_small, font=font(BOLD, 42), fill=WHITE, anchor='mm')
                chip_row(d, self.chips, states, 245, 'small', pops)
                fx = 140 + 800 * clamp(1 - t / self.t_stop)
                d.rounded_rectangle([140, 322, 940, 327], radius=3, fill=(255, 255, 255, 50))
                d.rounded_rectangle([140, 322, fx, 327], radius=3, fill=GOLD)
                sp = 8 + 3 * math.sin(t * 40)
                d.ellipse([fx - sp, 324.5 - sp, fx + sp, 324.5 + sp], fill=(255, 244, 210))
                comp(img, lay, a)
        else:
            img.alpha_composite(self.answer)
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            chip_row(ImageDraw.Draw(lay), self.chips, states, 420, 'small')
            img.alpha_composite(lay)
        if t >= self.t_twist:
            b = ease_out(ramp(t, self.t_twist, self.t_twist + 0.3))
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(lay)
            y = 1150 + 24 * (1 - b)
            d.rounded_rectangle([130, y, 950, y + 220], radius=36, fill=(8, 8, 18, 248), outline=GOLD + (255,), width=3)
            tw, _ = big_text(self.twist_lines, int(y + 34), shadow=False)
            lay.alpha_composite(tw)
            if self.cta:
                ImageDraw.Draw(lay).text((W / 2, y + 262), self.cta, font=font(BOLD, 40), fill=GOLD, anchor='mm')
            comp(img, lay, b)
        if self.t_stop <= t < self.t_stop + 0.35:
            k = (1 - (t - self.t_stop) / 0.35) ** 2
            img.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(235 * k))))
        return img


def punch(img, t, t_stop):
    """Short zoom punch after the STOP."""
    if t_stop <= t < t_stop + 0.3:
        s = 1 + 0.035 * (1 - (t - t_stop) / 0.3)
        w, h = int(W * s), int(H * s)
        big = img.resize((w, h), Image.BILINEAR)
        return big.crop(((w - W) // 2, (h - H) // 2, (w - W) // 2 + W, (h - H) // 2 + H))
    return img


def looped(frame_core, dur, xf=0.35):
    cache = {}

    def render_frame(t):
        img = frame_core(t)
        if t > dur - xf:
            if 'f0' not in cache:
                cache['f0'] = frame_core(0.0)
            img = Image.blend(img, cache['f0'], ease_io(ramp(t, dur - xf, dur - 1 / FPS)))
        return img
    return render_frame


# ---------------- stereo sound ----------------
class SMusic:
    def __init__(self, dur):
        self.dur = dur
        self.a = np.zeros((int(SR * (dur + 3)), 2), np.float32)

    def add(self, t, w, pan=0.0):
        th = (clamp(pan, -1, 1) + 1) * math.pi / 4
        i = int(max(0, t) * SR)
        n = min(len(w), len(self.a) - i)
        if n > 0:
            self.a[i:i + n, 0] += w[:n] * math.cos(th)
            self.a[i:i + n, 1] += w[:n] * math.sin(th)

    def add_st(self, t, l, r):
        i = int(max(0, t) * SR)
        n = min(len(l), len(self.a) - i)
        self.a[i:i + n, 0] += l[:n]
        self.a[i:i + n, 1] += r[:n]

    @staticmethod
    def _x(dur):
        return np.arange(int(SR * dur)) / SR

    def pluck(self, t, f, vol=0.3, pan=0.0, dur=0.9, bright=1.0):
        x = self._x(dur)
        w = (np.sin(2 * np.pi * f * x) + 0.5 * bright * np.sin(4 * np.pi * f * x) * np.exp(-x * 8)
             + 0.25 * bright * np.sin(6 * np.pi * f * x) * np.exp(-x * 14))
        self.add(t, (vol * w * np.exp(-x * 5) * np.clip(x / 0.003, 0, 1)).astype(np.float32), pan)

    def bell(self, t, f, vol=0.25, pan=0.0, dur=2.0):
        x = self._x(dur)
        w = sum(a * np.sin(2 * np.pi * f * m * x) * np.exp(-x * d) for a, m, d in
                ((1, 1, 1.6), (0.5, 2.76, 3), (0.3, 5.4, 5), (0.15, 8.9, 8)))
        self.add(t, (vol * w * np.clip(x / 0.002, 0, 1)).astype(np.float32), pan)

    def clack(self, t, f=900, vol=0.3, pan=0.0):
        x = self._x(0.12)
        rng = np.random.default_rng(int(t * 1000) % 9999)
        n = rng.standard_normal(len(x)) * np.exp(-x * 120)
        w = 0.6 * n + np.sin(2 * np.pi * f * x) * np.exp(-x * 45) + 0.5 * np.sin(2 * np.pi * f * 2.3 * x) * np.exp(-x * 70)
        self.add(t, (vol * w).astype(np.float32), pan)

    def boom(self, t, vol=0.8, dur=1.4, pan=0.0):
        x = self._x(dur)
        f = 42 + 95 * np.exp(-x * 9)
        self.add(t, (vol * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 3)).astype(np.float32), pan)

    def thump(self, t, vol=0.4):
        x = self._x(0.35)
        f = 55 + 40 * np.exp(-x * 25)
        self.add(t, (vol * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 14)).astype(np.float32))

    def chord(self, t, freqs, vol=0.25, dur=3.0):
        x = self._x(dur)
        env = np.clip(x / 0.02, 0, 1) * np.exp(-x * 1.1)
        for i, f in enumerate(freqs):
            w = (np.sin(2 * np.pi * f * x) + 0.3 * np.sin(4 * np.pi * f * x)) / len(freqs)
            self.add(t, (vol * w * env).astype(np.float32), pan=(i / max(1, len(freqs) - 1)) * 1.2 - 0.6)

    def whoosh(self, t, dur=0.8, vol=0.25, pan0=-0.8, pan1=0.8, bright=1.0):
        n = int(SR * dur)
        x = np.arange(n) / SR
        rng = np.random.default_rng(int(t * 997) % 9999)
        noise = rng.standard_normal(n)
        env = np.sin(np.pi * x / dur) ** 2
        # band-ish: lowpass then highpass, cutoff sweeps down (doppler feel)
        out = np.zeros(n)
        zi = [0.0]
        for i0 in range(0, n, 512):
            c = 0.05 + 0.25 * bright * (1 - i0 / n)
            seg, zi = lfilter([c], [1, c - 1], noise[i0:i0 + 512], zi=zi)
            out[i0:i0 + 512] = seg
        out = out / (np.max(np.abs(out)) or 1) * env * vol
        pans = np.linspace(pan0, pan1, n)
        th = (pans + 1) * np.pi / 4
        self.add_st(t, (out * np.cos(th)).astype(np.float32), (out * np.sin(th)).astype(np.float32))

    def bed(self, t0, t1, cutoff, vol, seed=0):
        """Stereo filtered-noise bed; cutoff(tt) in 0..1 and vol(tt) are functions of time."""
        n = int(SR * (t1 - t0))
        rng = np.random.default_rng(seed)
        for ch in range(2):
            noise = rng.standard_normal(n)
            out = np.zeros(n)
            zi = [0.0]
            for i0 in range(0, n, 1024):
                tt = t0 + i0 / SR
                c = 0.004 + 0.3 * clamp(cutoff(tt))
                seg, zi = lfilter([c], [1, c - 1], noise[i0:i0 + 1024], zi=zi)
                out[i0:i0 + 1024] = seg * vol(tt)
            i = int(t0 * SR)
            m = min(n, len(self.a) - i)
            self.a[i:i + m, ch] += (out[:m] * 6).astype(np.float32)

    def drone(self, t0, t1, freq_fn, vol=0.06):
        n = int(SR * (t1 - t0))
        x = np.arange(n) / SR
        ff = np.array([freq_fn(t0 + v) for v in x[::441]]).repeat(441)[:n]
        ph = 2 * np.pi * np.cumsum(ff) / SR
        env = np.clip(x / 0.05, 0, 1) * np.clip((t1 - t0 - x) / 0.04, 0, 1)
        l = (np.sin(ph) + 0.4 * np.sin(2 * ph) + 0.2 * np.sin(3.01 * ph)) * vol * env
        r = (np.sin(ph * 1.004) + 0.4 * np.sin(2.01 * ph) + 0.2 * np.sin(2.99 * ph)) * vol * env
        self.add_st(t0, l.astype(np.float32), r.astype(np.float32))

    def click_train(self, t0, t1, rate_fn, vol=0.2, tone=1800.0, pan=0.0):
        """Ticks whose rate follows rate_fn(t). Above ~20/s they fuse into a buzz whose pitch IS the rate:
        the number you watch rising becomes a note you hear rising."""
        n = int(SR * (t1 - t0))
        x = np.arange(n) / SR
        r = np.array([rate_fn(t0 + v) for v in x[::147]]).repeat(147)[:n]
        ph = np.cumsum(r) / SR
        since = (ph - np.floor(ph)) / np.maximum(r, 1e-3)          # seconds since the last tick
        click = np.exp(-since / 0.0025) * np.sin(2 * np.pi * tone * since)
        body = np.exp(-since / 0.012) * np.sin(2 * np.pi * 2 * np.pi * 0 + 2 * np.pi * (tone / 4) * since)
        w = (click + 0.5 * body) * vol
        env = np.clip(x / 0.02, 0, 1) * np.clip((t1 - t0 - x) / 0.01, 0, 1)
        self.add(t0, (w * env).astype(np.float32), pan)

    def silence(self, t0, t1):
        if not hasattr(self, 'sil'):
            self.sil = []
        self.sil.append((t0, t1))

    def stop_signature(self, t):
        for k, f in enumerate((783.99, 1046.5, 1318.5)):
            self.pluck(t + k * 0.07, f, vol=0.3, pan=(k - 1) * 0.5, bright=1.3)
        self.boom(t, 0.95)
        self.chord(t + 0.14, [523.25, 659.25, 783.99, 1046.5], 0.32, 2.6)

    def write(self, path, reverb=0.3):
        a = self.a.copy()
        L = int(SR * 2.0)
        for ch in range(2):
            rng = np.random.default_rng(10 + ch)
            ir = rng.standard_normal(L) * np.exp(-np.arange(L) / SR * 2.6)
            ir /= np.sqrt((ir ** 2).sum())
            a[:, ch] += reverb * fftconvolve(self.a[:, ch], ir)[:len(a)].astype(np.float32)
        for t0, t1 in getattr(self, 'sil', []):
            i0, i1, f = int(t0 * SR), int(t1 * SR), int(SR * 0.04)
            a[i0 - f:i0] *= np.linspace(1, 0, f)[:, None]
            a[i0:i1] = 0
        a = a[:int(SR * self.dur)]
        fade = int(SR * 0.03)
        a[-fade:] *= np.linspace(1, 0, fade)[:, None]
        a = np.tanh(a / (np.max(np.abs(a)) or 1) * 1.8) / np.tanh(1.8) * 0.9
        wavfile.write(path, SR, (a * 32767).astype(np.int16))


def render(render_frame, dur, out_path, music_fn, tmpdir):
    import os
    silent = os.path.join(tmpdir, 'silent.mp4')
    enc = Enc(silent)
    for i in range(int(round(dur * FPS))):
        enc.add(render_frame(i / FPS))
    enc.close()
    m = SMusic(dur)
    music_fn(m)
    wav = os.path.join(tmpdir, 'a.wav')
    m.write(wav)
    mux(silent, wav, out_path)


def main(render_frame, dur, music_fn, argv):
    import os
    out = argv[1]
    if len(argv) > 2 and argv[2] == '--preview':
        for ts in argv[3].split(','):
            render_frame(float(ts)).convert('RGB').save(f'{out}_{float(ts):05.2f}.png')
    else:
        render(render_frame, dur, out, music_fn, os.path.dirname(out) or '.')


# ---------------- v5 music: a beat that accelerates with the count ----------------
_SCALE = [0, 2, 4, 7, 9]                        # major pentatonic
_CHORDS = [(0, 4, 7), (7, 11, 14), (9, 12, 16), (5, 9, 12)]   # I  V  vi  IV (semitones from root)
_PATTERN = [0, 2, 4, 2, 1, 3, 5, 3]


def _hz(semi, root=261.63):
    return root * 2 ** (semi / 12)


def marimba(m, t, f, vol=0.25, pan=0.0):
    x = SMusic._x(0.7)
    w = (np.sin(2 * np.pi * f * x) * np.exp(-x * 7)
         + 0.35 * np.sin(2 * np.pi * f * 3.93 * x) * np.exp(-x * 30)
         + 0.12 * np.sin(2 * np.pi * f * 9.2 * x) * np.exp(-x * 60))
    m.add(t, (vol * w * np.clip(x / 0.0015, 0, 1)).astype(np.float32), pan)


def soft_kick(m, t, vol=0.35):
    x = SMusic._x(0.3)
    f = 48 + 70 * np.exp(-x * 30)
    m.add(t, (vol * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 11)).astype(np.float32))


def soft_hat(m, t, vol=0.04, pan=0.2):
    x = SMusic._x(0.05)
    rng = np.random.default_rng(int(t * 1000) % 9973)
    n = rng.standard_normal(len(x))
    n = n - np.convolve(n, np.ones(6) / 6, 'same')
    m.add(t, (vol * n * np.exp(-x * 90)).astype(np.float32), pan)


def bass(m, t, f, dur, vol=0.12):
    x = SMusic._x(dur)
    w = np.sin(2 * np.pi * f * x) + 0.25 * np.sin(4 * np.pi * f * x)
    env = np.clip(x / 0.01, 0, 1) * np.exp(-x * 2.2)
    m.add(t, (vol * w * env).astype(np.float32))


def beat_track(m, t_end, prog, bpm0=96, bpm1=168, key=0):
    """Accelerating, musical count-up: tempo and note density rise with prog(t) in 0..1; the melody climbs a
    pentatonic scale on a 16th-note grid; chords I-V-vi-IV every bar. Stops at t_end (silence follows)."""
    root = 261.63 * 2 ** (key / 12)
    t, step = 0.0, 0
    while t < t_end:
        p = clamp(prog(t))
        sixteenth = 60.0 / (bpm0 + (bpm1 - bpm0) * p) / 4
        bar = step // 16
        ch = _CHORDS[bar % 4]
        if step % 16 == 0:
            bass(m, t, root / 4 * 2 ** (ch[0] / 12), 16 * sixteenth, 0.13)
        if step % 4 == 0:
            soft_kick(m, t, 0.28 + 0.15 * p)
        if step % 2 == 0:
            soft_hat(m, t, 0.025 + 0.03 * p, pan=0.25 if step % 4 else -0.25)
        dense = (step % 2 == 0) or p > 0.55
        if dense:
            lift = int(p * 9)
            idx = lift + _PATTERN[(step // (1 if p > 0.55 else 2)) % 8]
            o, k = divmod(idx, 5)
            f = root * 2 ** ((12 * o + _SCALE[k]) / 12)
            marimba(m, t, f, 0.16 + 0.06 * p, pan=0.3 * math.sin(step * 0.9))
        t += sixteenth
        step += 1


def stop_chord(m, t, key=0):
    root = 261.63 * 2 ** (key / 12)
    soft_kick(m, t, 0.6)
    m.boom(t, 0.7, 1.6)
    for i, s in enumerate((0, 7, 12, 16, 19, 26)):
        f = root / 2 * 2 ** (s / 12)
        x = SMusic._x(3.2)
        w = (np.sin(2 * np.pi * f * x) + 0.3 * np.sin(4 * np.pi * f * x)) * np.clip(x / 0.01, 0, 1) * np.exp(-x * 0.9)
        m.add(t, (0.07 * w).astype(np.float32), pan=(i / 5) * 1.2 - 0.6)
    for k, s in enumerate((24, 28, 31, 36)):
        marimba(m, t + 0.06 * k, root / 2 * 2 ** (s / 12), 0.2, pan=(k - 1.5) * 0.3)
