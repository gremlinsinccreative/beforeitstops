"""Before It Stops - style v4 brand layer: calm and focused.
Rules: one hero visual + one number while it runs; answer chips only on the hook and again (resolved) at the STOP;
no camera shake, no flicker, no zoom punch; every shape is drawn 2x and downsampled (smooth edges);
glow on the hero only. Sound comes from brand.SMusic."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from lib import *
from lib2 import big_text
from brand import SMusic, chip_row, looped, main, render as _r, HEADER_SHADE

SS = 2
HOOK_END = 1.2


class Canvas:
    """2x supersampled RGBA layer with the same coordinates as the 1080x1920 frame."""

    def __init__(self):
        self.img = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img, 'RGBA')

    @staticmethod
    def _p(pts):
        return [(x * SS, y * SS) for x, y in pts]

    def line(self, pts, fill, width=2):
        self.d.line(self._p(pts), fill=fill, width=int(width * SS), joint='curve')

    def ellipse(self, box, fill=None, outline=None, width=1):
        self.d.ellipse([v * SS for v in box], fill=fill, outline=outline, width=int(width * SS))

    def circle(self, x, y, r, fill=None, outline=None, width=1):
        self.ellipse([x - r, y - r, x + r, y + r], fill, outline, width)

    def polygon(self, pts, fill):
        self.d.polygon(self._p(pts), fill=fill)

    def rect(self, box, fill=None, outline=None, width=1, radius=0):
        b = [v * SS for v in box]
        if radius:
            self.d.rounded_rectangle(b, radius=radius * SS, fill=fill, outline=outline, width=int(width * SS))
        else:
            self.d.rectangle(b, fill=fill, outline=outline, width=int(width * SS))

    def down(self):
        return self.img.resize((W, H), Image.LANCZOS)


def glow(layer, radius=18, strength=1.0):
    """Return layer with a soft glow underneath (blurred copy, brightened)."""
    small = layer.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(radius / 4))
    g = small.resize((W, H), Image.BILINEAR)
    if strength != 1.0:
        g.putalpha(g.getchannel('A').point(lambda v: min(255, int(v * strength))))
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    out.alpha_composite(g)
    out.alpha_composite(g)
    out.alpha_composite(layer)
    return out


class Brand2:
    def __init__(self, num, q_lines, q_short, chips, answer_lines, twist_lines, t_stop, t_twist, dur=10.5,
                 sub='Guess before it stops.', cta=None, q_size=92):
        self.num, self.chips, self.t_stop, self.t_twist, self.dur, self.cta = num, chips, t_stop, t_twist, dur, cta
        self.hook, _ = big_text([(f'FACT {num:03d}', SEMI, 30, MUTED)] + [(s, XB, q_size, WHITE) for s in q_lines]
                                + [(sub, SEMI, 42, GOLD)], 260)
        self.q_short = q_short
        self.run_head, _ = big_text([(f'FACT {num:03d}', BOLD, 30, (205, 210, 225)), (q_short, BOLD, 44, (240, 242, 250))], 112)
        self.answer, _ = big_text(answer_lines, 150)
        self.twist_lines = twist_lines

    def overlay(self, img, t, result):
        """result: {'A': 'out'|'win'|'idle'} shown only at the STOP."""
        a = ease_io(ramp(t, HOOK_END, HOOK_END + 0.35))
        if t < self.t_stop:
            if a < 1:
                lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
                lay.alpha_composite(HEADER_SHADE)
                lay.alpha_composite(self.hook)
                chip_row(ImageDraw.Draw(lay), self.chips, {}, 660, 'big')
                comp(img, lay, 1 - a)
            if a > 0:
                lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
                lay.alpha_composite(HEADER_SHADE)
                lay.alpha_composite(self.run_head)
                comp(img, lay, a * 0.9)
        else:
            k = ease_out(ramp(t, self.t_stop, self.t_stop + 0.35))
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            lay.alpha_composite(HEADER_SHADE)
            ImageDraw.Draw(lay).text((W / 2, 112), f'FACT {self.num:03d}', font=font(SEMI, 28), fill=MUTED, anchor='mm')
            lay.alpha_composite(self.answer)
            chip_row(ImageDraw.Draw(lay), self.chips, result, 420, 'small')
            comp(img, lay, k)
        if t >= self.t_twist:
            b = ease_out(ramp(t, self.t_twist, self.t_twist + 0.4))
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(lay)
            y = 1140 + 24 * (1 - b)
            d.rounded_rectangle([130, y, 950, y + 220], radius=36, fill=(8, 8, 18, 245), outline=GOLD + (255,), width=3)
            tw, _ = big_text(self.twist_lines, int(y + 34), shadow=False)
            lay.alpha_composite(tw)
            if self.cta:
                d.text((W / 2, y + 262), self.cta, font=font(BOLD, 40), fill=GOLD, anchor='mm')
            comp(img, lay, b)
        if self.t_stop <= t < self.t_stop + 0.45:          # soft flash, no zoom
            k = (1 - (t - self.t_stop) / 0.45) ** 2
            img.alpha_composite(Image.new('RGBA', (W, H), (255, 245, 225, int(120 * k))))
        return img
