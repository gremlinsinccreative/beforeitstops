"""v6 FACT 029 Which is wider: Pluto or Australia? 13 s, + next-up teaser (odd number).
Non-human-scale arm of the topic test; "most people say X" settle-it fact like #018/#027: most say Pluto (it's a planet-sized world).
Sources: Pluto equatorial diameter 2,377 km (NASA Pluto facts, science.nasa.gov, upd. 22 Apr 2025);
Australia "almost 4,000 kilometres wide, from east to west" (Geoscience Australia, Extreme points). Number on screen:
great-circle distance Steep Point (26°09'05"S 113°09'18"E) to Cape Byron (28°38'15"S 153°38'14"E), the westernmost and
easternmost mainland points in Geoscience Australia's table: 3,987 km (haversine, R = 6,371 km), recomputed below.
Twist: even our Moon is wider than Pluto: 3,475 km (NASA Moon facts, mean radius 1,737.4 km).
Hero: Australia's outline revealed by a measuring ruler sweeping west to east, Pluto's disk drawn over it at the same scale."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.interpolate import PchipInterpolator
from lib import *
from lib2 import big_text
from brand2 import *

DUR, T_STOP, T_TWIST = 13.0, 9.6, 11.0


def hav(la1, lo1, la2, lo2, R=6371.0):
    p1, p2 = math.radians(la1), math.radians(la2)
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lo2 - lo1) / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


STEEP = (-(26 + 9 / 60 + 5 / 3600), 113 + 9 / 60 + 18 / 3600)
BYRON = (-(28 + 38 / 60 + 15 / 3600), 153 + 38 / 60 + 14 / 3600)
AUS = round(hav(*STEEP, *BYRON))
PLUTO, MOON = 2377, round(2 * 1737.4)
assert AUS == 3987 and MOON == 3475 and AUS - PLUTO == 1610 and MOON > PLUTO

KEYS = [(0, 0.0), (1.4, 300.0), (3.4, 1150.0), (4.1, 1230.0), (6.1, 2330.0), (6.8, 2420.0), (8.7, 3920.0), (9.6, float(AUS))]
_P = PchipInterpolator([k[0] for k in KEYS], [k[1] for k in KEYS])


def km(t):
    return float(_P(min(max(t, 0.0), T_STOP)))


def t_at(v):
    lo, hi = 0.0, T_STOP
    for _ in range(40):
        md = (lo + hi) / 2
        lo, hi = (lo, md) if km(md) >= v else (md, hi)
    return hi


MILESTONES = [(PLUTO / 2, t_at(PLUTO / 2), ['Middle of Pluto', '1,189 km']),
              (PLUTO, t_at(PLUTO), ["Pluto ends here", '2,377 km (NASA)'])]
assert round(PLUTO / 2) == 1188 or round(PLUTO / 2) == 1189
BR = Brand2(29, ['Which is wider:', 'Pluto or Australia?'], 'Which is wider: Pluto or Australia?',
            [('A', 'Australia'), ('B', 'Pluto'), ('C', 'Same width')],
            [('Australia', BLACK, 120, GOLD), ('Almost 4,000 km wide vs Pluto\'s 2,377 km', BOLD, 36, WHITE)],
            [('Even our Moon is wider:', BOLD, 48, WHITE), ('3,475 km', BLACK, 80, GOLD)], T_STOP, T_TWIST, DUR,
            sub='Wait for the ruler', cta='Comment your letter', q_size=84,
            next_line='Next: FACT 030 · Live to 80: how many Mondays?')
RESULT = {'A': 'win', 'B': 'out', 'C': 'out'}

# simplified mainland coastline (lon, lat), clockwise from Steep Point; plus Tasmania
COAST = [(113.15, -26.15), (113.8, -21.8), (116.0, -20.6), (118.6, -20.3), (121.0, -19.5), (122.2, -18.0), (122.9, -16.4),
         (124.4, -15.6), (125.0, -14.5), (126.9, -13.7), (128.2, -14.9), (129.5, -14.9), (130.2, -13.2), (130.8, -12.4),
         (132.5, -11.3), (134.0, -11.9), (136.0, -12.0), (136.9, -12.3), (135.6, -14.6), (136.5, -15.8), (138.3, -16.8),
         (139.5, -17.5), (140.8, -17.4), (141.6, -15.0), (141.5, -12.5), (142.5, -10.7), (143.5, -14.0), (145.3, -15.5),
         (145.8, -16.9), (146.8, -19.3), (149.2, -21.1), (150.8, -22.6), (151.2, -23.8), (153.2, -25.0), (153.1, -27.4),
         (153.64, -28.64), (153.1, -30.3), (151.8, -32.9), (151.3, -33.9), (150.2, -35.8), (149.98, -37.5), (147.8, -37.9),
         (146.4, -39.1), (144.9, -38.3), (143.5, -38.8), (141.6, -38.4), (139.7, -37.2), (139.0, -35.6), (138.1, -35.6),
         (138.5, -34.9), (138.0, -34.0), (137.5, -35.1), (137.0, -35.2), (137.8, -32.8), (135.8, -34.7), (134.2, -32.9),
         (133.7, -32.1), (131.1, -31.5), (128.9, -31.7), (126.0, -32.3), (121.9, -33.9), (117.9, -35.0), (115.1, -34.4),
         (115.0, -33.5), (115.7, -32.0), (114.6, -28.8), (113.8, -26.5)]
TAS = [(144.6, -40.7), (148.3, -40.9), (148.3, -42.2), (147.8, -43.2), (146.0, -43.6), (145.2, -42.2)]

X0, X1 = 190, 890                      # ruler: 0 km at X0, AUS km at X1
PX_KM = (X1 - X0) / AUS
KX = math.cos(math.radians(27)) * 111.32 * PX_KM          # px per degree of longitude
LON0, LON1 = STEEP[1], BYRON[1]
KX = (X1 - X0) / (LON1 - LON0)                            # map Steep Point to X0 and Cape Byron to X1 exactly
KY = KX / math.cos(math.radians(27))                      # px per degree of latitude (keeps the shape's proportions)
MY = 990                                                 # map centre y (lat -27)


def proj(lon, lat):
    return X0 + (lon - LON0) * KX, MY - (lat + 27.0) * KY


PLUTO_R = PLUTO * PX_KM / 2
PCX, PCY = X0 + PLUTO_R, 990
RULER_Y = 640


def background():
    ys = np.linspace(0, 1, H)[:, None, None]
    top, bot = np.array((8, 10, 24)), np.array((10, 22, 40))
    arr = np.broadcast_to(top * (1 - ys) + bot * ys, (H, W, 3)).astype(np.uint8)
    img = Image.fromarray(np.ascontiguousarray(arr), 'RGB').convert('RGBA')
    c = Canvas()
    rng = np.random.default_rng(29)
    for _ in range(110):
        c.circle(rng.uniform(0, W), rng.uniform(0, H * 0.74), rng.uniform(0.8, 1.8), fill=(220, 226, 255, int(rng.uniform(40, 130))))
    img.alpha_composite(c.down())
    return img


def land_layer():
    c = Canvas()
    c.polygon([proj(*p) for p in COAST], fill=(196, 132, 74, 255))
    c.polygon([proj(*p) for p in TAS], fill=(196, 132, 74, 255))
    return c.down()


def pluto_layer():
    c = Canvas()
    c.circle(PCX, PCY, PLUTO_R, fill=(214, 196, 176, 215))
    c.circle(PCX + PLUTO_R * 0.28, PCY + PLUTO_R * 0.12, PLUTO_R * 0.36, fill=(244, 234, 220, 200))   # the 'heart'
    c.circle(PCX + PLUTO_R * 0.05, PCY + PLUTO_R * 0.3, PLUTO_R * 0.3, fill=(244, 234, 220, 200))
    c.circle(PCX - PLUTO_R * 0.45, PCY + PLUTO_R * 0.35, PLUTO_R * 0.32, fill=(150, 112, 96, 150))
    c.circle(PCX, PCY, PLUTO_R, outline=(255, 246, 230, 255), width=3)
    return c.down()


BG_IMG, LAND, PLUTO_IMG = background(), land_layer(), pluto_layer()
_tw = font(SEMI, 26)


def frame_core(t):
    k = km(t)
    xr = X0 + k * PX_KM
    img = BG_IMG.copy()
    # Australia, revealed only left of the ruler's tip (nothing ahead of it gives the answer away)
    mask = Image.new('L', (W, H), 0)
    ImageDraw.Draw(mask).rectangle([0, 0, int(xr), H], fill=255)
    land = LAND.copy()
    a = land.getchannel('A')
    land.putalpha(Image.composite(a, a.point(lambda v: 0), mask))
    img.alpha_composite(land)
    img.alpha_composite(PLUTO_IMG)
    hc = Canvas()
    hc.line([(X0, RULER_Y), (xr, RULER_Y)], fill=(255, 214, 102, 255), width=8)
    hc.line([(X0, RULER_Y - 22), (X0, RULER_Y + 22)], fill=(255, 214, 102, 255), width=5)
    hc.line([(xr, RULER_Y - 26), (xr, MY + 300)], fill=(255, 226, 140, 200), width=3)
    for tk in range(0, int(k) + 1, 500):
        x = X0 + tk * PX_KM
        hc.line([(x, RULER_Y), (x, RULER_Y + (16 if tk % 1000 == 0 else 9))], fill=(255, 214, 102, 230), width=3)
    comp(img, glow(hc.down(), radius=12, strength=0.5), 1 - 0.7 * ease_io(ramp(t, T_TWIST - 0.1, T_TWIST + 0.3)))
    wa = ease_io(ramp(t, HOOK_END + 0.1, HOOK_END + 0.4)) * (1 - ease_io(ramp(t, T_STOP - 0.3, T_STOP)))
    if wa > 0.02:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(lay).text((X0, RULER_Y - 44), 'West coast', font=_tw, fill=(200, 206, 225), anchor='lm')
        comp(img, lay, wa)
    for vv, tp, txt in MILESTONES:
        al = ease_io(ramp(t, tp - 0.2, tp + 0.05)) * (1 - ease_io(ramp(t, tp + 0.9, tp + 1.15)))
        if al > 0.02 and t < T_STOP:
            lb, _ = big_text([(txt[0], XB, 52, WHITE), (txt[1], BOLD, 42, GOLD)], 0)
            sub = lb.crop(lb.getbbox())
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            lay.alpha_composite(sub, ((W - sub.width) // 2, 492))
            comp(img, lay, al)
    ca = 1 - ramp(t, T_TWIST - 0.1, T_TWIST + 0.2)
    if ca > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(lay)
        val = f'{AUS:,} km' if t >= T_STOP else f'{int(k):,} km'
        dd.rounded_rectangle([270, 1322, 810, 1448], radius=40, fill=(6, 10, 22, 210))
        dd.text((W / 2 + 4, 1389), val, font=font(BLACK, 92), fill=(0, 0, 0, 150), anchor='mm')
        dd.text((W / 2, 1385), val, font=font(BLACK, 92), fill=GOLD if t >= T_STOP else WHITE, anchor='mm')
        comp(img, lay, ca)
    return BR.overlay(img, t, RESULT)


render_frame = looped(frame_core, DUR, xf=0.5)


def music(mu):
    from brand import drum_track, ding, drop_hit
    lvl = lambda tt: km(tt) / AUS
    mu.bed(0, T_STOP, cutoff=lambda tt: 0.05 + 0.06 * lvl(tt), vol=lambda tt: (0.015 + 0.04 * lvl(tt)) * clamp(tt / 0.05), seed=29)
    drum_track(mu, T_STOP - 0.32, lvl, bpm0=96, bpm1=150, key=-2, roll=1.4)
    for vv, tp, _ in MILESTONES:
        ding(mu, tp, key=-2, vol=0.15, pan=0.4 if vv < 2000 else -0.4)
    mu.silence(T_STOP - 0.32, T_STOP)
    drop_hit(mu, T_STOP, key=-2)
    mu.bed(T_STOP + 0.4, DUR, cutoff=lambda tt: 0.02, vol=lambda tt: 0.01, seed=17)
    mu.bell(T_TWIST, 659.25, 0.16, -0.3); mu.bell(T_TWIST + 0.1, 987.77, 0.16, 0.3)


if __name__ == '__main__':
    main(render_frame, DUR, music, sys.argv)
