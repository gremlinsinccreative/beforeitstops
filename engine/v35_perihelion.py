"""v6 FACT 035 When is Earth closest to the Sun? 13 s, + next-up teaser (odd number).
Non-human-scale arm of the topic test; a "tempting wrong answer" fact (most people guess summer).
Sources: USNO, "The Seasons and the Earth's Orbit" (aa.usno.navy.mil/faq/seasons_orbit): "The Earth reaches perihelion
- the point in its orbit closest to the Sun - in early January, only about two weeks after the December solstice" and
"the distance to the Sun at perihelion is only about 3% less than its distance at aphelion".
timeanddate.com perihelion/aphelion table, 2027 row: perihelion January 2, 2027 9:38 pm Columbus time (= 3 Jan 02:38 UT)
at 91,406,556 mi = 147.10 million km; aphelion July 5, 2027 at 94,510,857 mi = 152.10 million km.
Difference 5.0 million km = 3.3% (USNO: "about 3%").
Counter: Earth-Sun distance from Kepler's equation for the half orbit from aphelion (July) to perihelion (early January).
Milestones: early October and early December with their computed distances.
Twist: seasons come from the tilt, not the distance.
Hero: Sun and a glowing Earth on its orbit (shape exaggerated, marked on screen), a glowing Sun-Earth distance line."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from scipy.interpolate import PchipInterpolator
from lib import *
from lib2 import big_text
from brand2 import *

DUR, T_STOP, T_TWIST = 13.0, 9.6, 11.0
MI = 1.609344
RP = 91_406_556 * MI / 1e6          # million km
RA = 94_510_857 * MI / 1e6
assert round(RP, 1) == 147.1 and round(RA, 1) == 152.1 and round(RA - RP, 1) == 5.0
assert round((RA - RP) / RA * 100, 1) == 3.3
A_T, E_T = (RA + RP) / 2, (RA - RP) / (RA + RP)
YEAR = 365.256
DP = YEAR / 2                        # days from aphelion to perihelion


def kepler(d):
    """d days after aphelion -> (true anomaly measured from perihelion, distance in million km)."""
    M = math.pi + 2 * math.pi * d / YEAR
    E = M
    for _ in range(30):
        E -= (E - E_T * math.sin(E) - M) / (1 - E_T * math.cos(E))
    nu = 2 * math.atan2(math.sqrt(1 + E_T) * math.sin(E / 2), math.sqrt(1 - E_T) * math.cos(E / 2))
    return nu, A_T * (1 - E_T * math.cos(E))


assert round(kepler(0)[1], 1) == 152.1 and round(kepler(DP)[1], 1) == 147.1
D_OCT, D_DEC = 91.0, 150.0           # aphelion is 3-6 July: +91 d = early October, +150 d = early December
R_OCT, R_DEC = kepler(D_OCT)[1], kepler(D_DEC)[1]
assert round(R_OCT, 1) == 149.7 and round(R_DEC, 1) == 147.5, (R_OCT, R_DEC)

KEYS = [(0, 0.0), (1.4, 38.0), (3.2, 88.0), (4.1, 93.0), (5.8, 147.5), (6.8, 152.0), (8.7, 178.0), (9.6, DP)]
_P = PchipInterpolator([k[0] for k in KEYS], [k[1] for k in KEYS])


def days(t):
    return float(_P(min(max(t, 0.0), T_STOP)))


def t_at(v):
    lo, hi = 0.0, T_STOP
    for _ in range(40):
        md = (lo + hi) / 2
        lo, hi = (lo, md) if days(md) >= v else (md, hi)
    return hi


MILESTONES = [(D_OCT, t_at(D_OCT), ['October', f'{R_OCT:.1f} million km']),
              (D_DEC, t_at(D_DEC), ['December', f'{R_DEC:.1f} million km'])]
BR = Brand2(35, ['When is Earth', 'closest to the Sun?'], 'When is Earth closest to the Sun?',
            [('A', 'In July'), ('B', 'In January'), ('C', 'It never changes')],
            [('Early January', BLACK, 100, GOLD), ('147.1 million km on 3 Jan 2027 (USNO; timeanddate)', BOLD, 34, WHITE)],
            [('Seasons come from the tilt,', BOLD, 48, WHITE), ('not the distance', BLACK, 80, GOLD)], T_STOP, T_TWIST, DUR,
            sub='Wait for the closest day', cta='Comment your letter', q_size=84,
            next_line='Next: FACT 036 · A blue whale weighs how many people?')
RESULT = {'A': 'out', 'B': 'win', 'C': 'out'}

# visual orbit: same true anomaly, exaggerated eccentricity; perihelion points down
SX, SY = 540, 1045
AV, EV = 260, 0.14


def orbit_xy(nu):
    r = AV * (1 - EV ** 2) / (1 + EV * math.cos(nu))
    return SX + r * math.sin(nu), SY + r * math.cos(nu)


def background():
    ys = np.linspace(0, 1, H)[:, None, None]
    top, bot = np.array((3, 3, 10)), np.array((10, 12, 30))
    arr = np.broadcast_to(top * (1 - ys) + bot * ys, (H, W, 3)).astype(np.uint8)
    img = Image.fromarray(np.ascontiguousarray(arr), 'RGB').convert('RGBA')
    c = Canvas()
    rng = np.random.default_rng(35)
    for _ in range(160):
        c.circle(rng.uniform(0, W), rng.uniform(0, 1440), rng.uniform(0.8, 1.8), fill=(220, 226, 255, int(rng.uniform(40, 150))))
    pts = [orbit_xy(a) for a in np.linspace(0, 2 * math.pi, 240)]
    c.line(pts + [pts[0]], fill=(110, 130, 180, 150), width=2.4)
    img.alpha_composite(c.down())
    s = Canvas()
    s.circle(SX, SY, 54, fill=(255, 190, 80, 255))
    s.circle(SX, SY, 40, fill=(255, 226, 140, 255))
    img.alpha_composite(glow(s.down(), radius=30, strength=0.5))
    return img


BG_IMG = background()
_sm = font(SEMI, 26)


def frame_core(t):
    d = days(t)
    nu, r = kepler(d)
    ex, ey = orbit_xy(nu)
    img = BG_IMG.copy()
    hc = Canvas()
    hc.line([(SX, SY), (ex, ey)], fill=(255, 214, 102, 200), width=4)
    hc.circle(ex, ey, 26, fill=(50, 110, 210, 255))
    hc.ellipse([ex - 14, ey - 14, ex + 4, ey + 2], fill=(80, 160, 90, 255))
    hc.circle(ex, ey, 26, outline=(170, 210, 255, 255), width=2.5)
    comp(img, glow(hc.down(), radius=14, strength=0.6), 1 - 0.7 * ease_io(ramp(t, T_TWIST - 0.1, T_TWIST + 0.3)))
    wa = ease_io(ramp(t, HOOK_END + 0.1, HOOK_END + 0.4)) * (1 - ease_io(ramp(t, T_STOP - 0.3, T_STOP)))
    if wa > 0.02:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(lay)
        dd.text((W - 50, 1290), 'orbit shape exaggerated', font=_sm, fill=(160, 170, 200), anchor='rm')
        dd.text((SX, SY - AV * (1 - EV ** 2) / (1 - EV) - 50), 'July: farthest', font=font(BOLD, 34), fill=(200, 208, 230), anchor='mm')
        comp(img, lay, wa)
    for vv, tp, txt in MILESTONES:
        al = ease_io(ramp(t, tp - 0.2, tp + 0.05)) * (1 - ease_io(ramp(t, tp + 0.9, tp + 1.15)))
        if al > 0.02 and t < T_STOP:
            lb, _ = big_text([(txt[0], XB, 50, WHITE), (txt[1], BOLD, 42, GOLD)], 0)
            sub = lb.crop(lb.getbbox())
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            x = 70 if ex > SX else W - 70 - sub.width          # label on the side away from Earth
            lay.alpha_composite(sub, (int(x), 470))
            comp(img, lay, al)
    ca = 1 - ramp(t, T_TWIST - 0.1, T_TWIST + 0.2)
    if ca > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(lay)
        val = f'{(RP if t >= T_STOP else r):.1f} million km'
        dd.rounded_rectangle([170, 1322, 910, 1440], radius=40, fill=(4, 6, 18, 215))
        dd.text((W / 2 + 4, 1385), val, font=font(BLACK, 76), fill=(0, 0, 0, 150), anchor='mm')
        dd.text((W / 2, 1381), val, font=font(BLACK, 76), fill=GOLD if t >= T_STOP else WHITE, anchor='mm')
        comp(img, lay, ca)
    return BR.overlay(img, t, RESULT)


render_frame = looped(frame_core, DUR, xf=0.5)


def music(mu):
    from brand import drum_track, ding, drop_hit
    lvl = lambda tt: days(tt) / DP
    mu.bed(0, T_STOP, cutoff=lambda tt: 0.05 + 0.06 * lvl(tt), vol=lambda tt: (0.015 + 0.04 * lvl(tt)) * clamp(tt / 0.05), seed=35)
    drum_track(mu, T_STOP - 0.32, lvl, bpm0=96, bpm1=150, key=0, roll=1.4)
    for vv, tp, _ in MILESTONES:
        ding(mu, tp, key=0, vol=0.15, pan=0.4 if vv < 120 else -0.4)
    mu.silence(T_STOP - 0.32, T_STOP)
    drop_hit(mu, T_STOP, key=0)
    mu.bed(T_STOP + 0.4, DUR, cutoff=lambda tt: 0.02, vol=lambda tt: 0.01, seed=23)
    mu.bell(T_TWIST, 659.25, 0.16, -0.3); mu.bell(T_TWIST + 0.1, 987.77, 0.16, 0.3)


if __name__ == '__main__':
    main(render_frame, DUR, music, sys.argv)
