"""Shared helpers for the satisfying-facts prototypes (1080x1920, 30 fps)."""
import os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.io import wavfile

W, H, FPS = 1080, 1920, 30
SR = 44100
import os as _os
FD = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'fonts') + '/'
BLACK, XB, BOLD, SEMI, MED = ('InterDisplay-Black', 'InterDisplay-ExtraBold',
                              'InterDisplay-Bold', 'Inter-SemiBold', 'Inter-Medium')
BG = (10, 12, 18)
WHITE = (245, 247, 250)
MUTED = (140, 152, 176)
BLUE = (64, 170, 255)
GOLD = (255, 204, 51)

_fonts = {}


def font(name, size):
    k = (name, size)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(FD + name + '.otf', size)
    return _fonts[k]


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ramp(t, a, b):
    return clamp((t - a) / (b - a))


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in(x):
    x = clamp(x)
    return x ** 3


def ease_io(x):
    x = clamp(x)
    return 3 * x * x - 2 * x ** 3


def text_layer(lines, y, plate=None, gap=14, tracking=None):
    """lines: list of (text, fontname, size, fill). Centered block starting at y.
    Returns (RGBA layer, y_end)."""
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    boxes, cy = [], y
    for text, fn, size, fill in lines:
        f = font(fn, size)
        l, t, r, b = d.textbbox((0, 0), text, font=f)
        boxes.append((text, f, fill, (W - (r - l)) // 2 - l, cy - t, r - l, b - t))
        cy += (b - t) + gap + int(size * 0.18)
    y_end = cy - gap
    if plate:
        wmax = max(b[5] for b in boxes)
        pad = 34
        d.rounded_rectangle([(W - wmax) // 2 - pad, y - pad, (W + wmax) // 2 + pad, y_end + pad - 10],
                            radius=28, fill=plate)
    for text, f, fill, x, ty, _, _ in boxes:
        d.text((x, ty), text, font=f, fill=fill)
    return layer, y_end


def comp(base, layer, a=1.0):
    """Alpha-composite an RGBA layer on an RGBA base with extra opacity a."""
    if a <= 0.003:
        return
    if a >= 0.997:
        base.alpha_composite(layer)
        return
    tmp = layer.copy()
    tmp.putalpha(layer.getchannel('A').point(lambda v: int(v * a)))
    base.alpha_composite(tmp)


def new_frame():
    return Image.new('RGBA', (W, H), BG + (255,))


class Enc:
    """Pipe raw frames to one encoded file; rename only when ffmpeg exits 0."""

    def __init__(self, path):
        self.path = path
        self.tmp = path[:-4] + '.part.mp4'
        self.p = subprocess.Popen(
            ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
             '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '18',
             '-preset', 'veryfast', '-pix_fmt', 'yuv420p', self.tmp], stdin=subprocess.PIPE)

    def add(self, img):
        self.p.stdin.write(img.convert('RGB').tobytes())

    def close(self):
        self.p.stdin.close()
        rc = self.p.wait()
        assert rc == 0, 'ffmpeg failed'
        os.replace(self.tmp, self.path)


class Audio:
    def __init__(self, dur):
        self.dur = dur
        self.a = np.zeros(int(SR * (dur + 2)), dtype=np.float32)

    def _add(self, t, w):
        if t < 0:
            return
        i = int(t * SR)
        n = min(len(w), len(self.a) - i)
        if n > 0:
            self.a[i:i + n] += w[:n]

    def tick(self, t, freq=900.0, vol=0.22, dur=0.06):
        x = np.arange(int(SR * dur)) / SR
        w = (np.sin(2 * np.pi * freq * x) + 0.35 * np.sin(2 * np.pi * freq * 2.01 * x)) * np.exp(-x * 70)
        self._add(t, (vol * w).astype(np.float32))

    def thunk(self, t, freq=140.0, vol=0.5, dur=0.22):
        x = np.arange(int(SR * dur)) / SR
        w = np.sin(2 * np.pi * (freq * (1 + 0.6 * np.exp(-x * 30))) * x) * np.exp(-x * 16)
        self._add(t, (vol * w).astype(np.float32))

    def ding(self, t, freqs=(659.3, 987.8, 1318.5), vol=0.26, dur=1.6):
        x = np.arange(int(SR * dur)) / SR
        w = sum(np.sin(2 * np.pi * f * x) * np.exp(-x * (2.6 + i)) for i, f in enumerate(freqs))
        self._add(t, (vol * w / len(freqs) * 2).astype(np.float32))

    def whoosh(self, t, dur=0.7, vol=0.16, up=True):
        n = int(SR * dur)
        x = np.arange(n) / SR
        rng = np.random.default_rng(7)
        noise = rng.standard_normal(n).astype(np.float32)
        k = 220
        sm = np.convolve(noise, np.ones(k) / k, mode='same')
        hp = noise - sm
        env = np.sin(np.pi * x / dur) ** 2
        mix = np.linspace(0, 1, n) if up else np.linspace(1, 0, n)
        self._add(t, (vol * env * (sm * 6 * (1 - mix) + hp * mix)).astype(np.float32))

    def write(self, path):
        a = self.a[:int(SR * self.dur)].copy()
        fade = int(SR * 0.02)
        a[-fade:] *= np.linspace(1, 0, fade)
        peak = float(np.max(np.abs(a))) or 1.0
        a = a / peak * 0.85
        st = np.stack([a, a], axis=1)
        wavfile.write(path, SR, (st * 32767).astype(np.int16))


def mux(video, wav, out):
    tmp = out[:-4] + '.part.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', video, '-i', wav, '-map', '0:v', '-map', '1:a',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', tmp],
                   check=True)
    os.replace(tmp, out)


def run(render_frame, dur, name, audio_fn, argv):
    _here = _os.path.dirname(_os.path.abspath(__file__))
    _os.makedirs(_os.path.join(_here, 'preview'), exist_ok=True)
    _os.makedirs(_os.path.join(_here, 'out'), exist_ok=True)
    """Preview mode: `--preview 0,3.5,9` writes PNGs. Otherwise full render + sound."""
    here = os.path.dirname(os.path.abspath(__file__))
    if len(argv) > 2 and argv[1] == '--preview':
        for ts in argv[2].split(','):
            t = float(ts)
            render_frame(t).convert('RGB').save(os.path.join(here, 'preview', f'{name}_{t:05.2f}.png'))
        return
    silent = os.path.join(here, 'out', f'{name}_silent.mp4')
    enc = Enc(silent)
    n = int(round(dur * FPS))
    for i in range(n):
        enc.add(render_frame(i / FPS))
    enc.close()
    au = Audio(dur)
    audio_fn(au)
    wav = os.path.join(here, 'out', f'{name}.wav')
    au.write(wav)
    mux(silent, wav, os.path.join(here, 'out', f'{name}.mp4'))
    print('done', name, n, 'frames')


def loop_sim(img, sim, t, dur, t_out=13.05, t_in=13.45):
    """Composite sim(tt) -> RGBA layer so the last frame equals the first: the current cycle
    fades out from t_out, the next cycle (tt = t - dur) fades in from t_in."""
    if t < t_out + 0.45:
        comp(img, sim(t), 1 - ease_io(ramp(t, t_out, t_out + 0.4)))
    if t >= t_in:
        comp(img, sim(t - dur), ease_io(ramp(t, t_in, t_in + 0.4)))


def loop_text(img, hook, reveal, t, t_rev):
    """Hook until the reveal, reveal until the reset, hook back for the loop."""
    rin = ease_io(ramp(t, t_rev, t_rev + 0.35))
    comp(img, hook, (1 - rin) if t < 13 else ease_io(ramp(t, 13.5, 13.9)))
    comp(img, reveal, rin * (1 - ease_io(ramp(t, 13.1, 13.45))))


def layer():
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    return lay, ImageDraw.Draw(lay)
