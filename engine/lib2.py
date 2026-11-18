"""Style layer v2 (proposal): gradient background, bloom glow, trails, bigger type, melodic sound.
Builds on lib.py (fonts, text_layer, Enc, mux)."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.io import wavfile
from scipy.signal import fftconvolve
from lib import *

# ---------- picture ----------

def gradient_bg(top=(18, 10, 40), bottom=(4, 6, 16), glow_at=(540, 1000), glow_col=(60, 30, 120), glow_r=900):
    y = np.linspace(0, 1, H)[:, None, None]
    g = np.array(top) * (1 - y) + np.array(bottom) * y
    g = np.broadcast_to(g, (H, W, 3)).copy()
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt((xx - glow_at[0]) ** 2 + (yy - glow_at[1]) ** 2) / glow_r
    g += np.array(glow_col)[None, None, :] * np.clip(1 - d, 0, 1)[..., None] ** 2
    # vignette
    v = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2)
    g *= np.clip(1.15 - v * 0.9, 0, 1)[..., None]
    return np.clip(g, 0, 255).astype(np.float32)


def bloom(arr, strength=1.0, radius=18, scale=4):
    """arr float32 HxWx3 (0-255). Returns arr + blurred bright parts."""
    small = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).resize((W // scale, H // scale), Image.BILINEAR)
    b1 = small.filter(ImageFilter.GaussianBlur(radius / scale))
    b2 = small.filter(ImageFilter.GaussianBlur(radius * 3 / scale))
    b = (np.asarray(b1, np.float32) * 0.6 + np.asarray(b2, np.float32) * 0.6)
    b = np.asarray(Image.fromarray(np.clip(b, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32)
    return arr + b * strength


def to_img(arr):
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')


def hsv(h, s=0.85, v=1.0):
    import colorsys
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))


def big_text(lines, y, shadow=True):
    """Like text_layer but with a soft dark shadow so type reads on any background."""
    lay, ye = text_layer(lines, y)
    if not shadow:
        return lay, ye
    a = lay.getchannel('A').filter(ImageFilter.GaussianBlur(10))
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sh.putalpha(a.point(lambda v: min(255, int(v * 1.6))))
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    out.alpha_composite(sh)
    out.alpha_composite(lay)
    return out, ye

# ---------- sound ----------

PENTA = [0, 2, 4, 7, 9]


def note_freq(i, base=261.63):
    """i-th note of a major pentatonic scale from C4."""
    o, k = divmod(i, 5)
    return base * 2 ** ((12 * o + PENTA[k]) / 12)


class Music:
    def __init__(self, dur):
        self.dur = dur
        self.a = np.zeros(int(SR * (dur + 3)), np.float32)

    def _add(self, t, w):
        i = int(max(0, t) * SR)
        n = min(len(w), len(self.a) - i)
        if n > 0:
            self.a[i:i + n] += w[:n]

    def pluck(self, t, f, vol=0.3, dur=0.9, bright=1.0):
        x = np.arange(int(SR * dur)) / SR
        w = (np.sin(2 * np.pi * f * x) + 0.5 * bright * np.sin(2 * np.pi * 2 * f * x) * np.exp(-x * 8)
             + 0.25 * bright * np.sin(2 * np.pi * 3 * f * x) * np.exp(-x * 14))
        env = np.exp(-x * 5) * np.clip(x / 0.003, 0, 1)
        self._add(t, (vol * w * env).astype(np.float32))

    def mallet(self, t, f, vol=0.3, dur=1.2):
        x = np.arange(int(SR * dur)) / SR
        w = np.sin(2 * np.pi * f * x) + 0.3 * np.sin(2 * np.pi * 4.0 * f * x) * np.exp(-x * 30)
        self._add(t, (vol * w * np.exp(-x * 3.5) * np.clip(x / 0.002, 0, 1)).astype(np.float32))

    def chord(self, t, freqs, vol=0.25, dur=3.0):
        x = np.arange(int(SR * dur)) / SR
        w = sum(np.sin(2 * np.pi * f * x) + 0.3 * np.sin(2 * np.pi * 2 * f * x) for f in freqs) / len(freqs)
        env = np.clip(x / 0.02, 0, 1) * np.exp(-x * 1.2)
        self._add(t, (vol * w * env).astype(np.float32))

    def boom(self, t, vol=0.8, dur=1.2):
        x = np.arange(int(SR * dur)) / SR
        f = 45 + 90 * np.exp(-x * 9)
        ph = 2 * np.pi * np.cumsum(f) / SR
        self._add(t, (vol * np.sin(ph) * np.exp(-x * 3.5)).astype(np.float32))

    def riser(self, t, dur=1.5, vol=0.12):
        n = int(SR * dur)
        x = np.arange(n) / SR
        rng = np.random.default_rng(3)
        noise = rng.standard_normal(n).astype(np.float32)
        hp = noise - np.convolve(noise, np.ones(40) / 40, 'same')
        self._add(t, (vol * hp * (x / dur) ** 2).astype(np.float32))

    def pad(self, t0, t1, freqs, vol=0.05):
        n = int(SR * (t1 - t0))
        x = np.arange(n) / SR
        w = sum(np.sin(2 * np.pi * f * x + i) for i, f in enumerate(freqs)) / len(freqs)
        env = np.clip(x / 1.0, 0, 1) * np.clip((t1 - t0 - x) / 0.6, 0, 1)
        self._add(t0, (vol * w * env * (1 + 0.15 * np.sin(2 * np.pi * 0.5 * x))).astype(np.float32))

    def write(self, path, reverb=0.25):
        a = self.a.copy()
        # simple reverb: decaying noise impulse
        rng = np.random.default_rng(1)
        L = int(SR * 1.6)
        ir = rng.standard_normal(L).astype(np.float32) * np.exp(-np.arange(L) / SR * 3.2)
        ir /= np.sqrt((ir ** 2).sum())
        wet = fftconvolve(a, ir)[:len(a)].astype(np.float32)
        a = a + reverb * wet
        a = a[:int(SR * self.dur)]
        fade = int(SR * 0.03)
        a[-fade:] *= np.linspace(1, 0, fade)
        a = np.tanh(a / (np.max(np.abs(a)) or 1) * 1.6) / np.tanh(1.6) * 0.9
        wavfile.write(path, SR, (np.stack([a, a], 1) * 32767).astype(np.int16))


def render(render_frame, dur, out_path, music_fn, tmpdir):
    import os
    silent = os.path.join(tmpdir, 'silent.mp4')
    enc = Enc(silent)
    for i in range(int(round(dur * FPS))):
        enc.add(render_frame(i / FPS))
    enc.close()
    m = Music(dur)
    music_fn(m)
    wav = os.path.join(tmpdir, 'a.wav')
    m.write(wav)
    mux(silent, wav, out_path)
